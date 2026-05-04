#!/usr/bin/env python3
"""Train fast tabular baselines for AI4Agri Subtask 2 DACIA5 patches."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd


PATCH_RE = re.compile(r"^patch_(?P<date>\d{8})_(?P<parcel>\d+)_(?P<label>\d+)\.tif$")

PROBLEM_LABELS = {
    1: {
        0: "Wheat",
        1: "Corn",
        2: "Peas",
        3: "Rapeseed",
        4: "Potato",
        5: "Sugarbeet",
        6: "Alfalfa",
    },
    2: {
        0: "Winter Wheat",
        1: "Alfalfa",
    },
}


@dataclass(frozen=True)
class PatchRecord:
    path: Path
    rel_path: str
    problem: int
    split: str
    date: str
    year: int
    month: int
    day: int
    parcel_id: str
    label: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True, help="Extracted DACIA5 dataset root.")
    parser.add_argument("--out-dir", type=Path, default=Path("results/subtask2/baseline"))
    parser.add_argument("--problem", type=int, choices=[1, 2], default=1)
    parser.add_argument("--limit", type=int, default=0, help="Optional max patches per split for smoke tests.")
    parser.add_argument("--force-features", action="store_true", help="Recompute cached features.")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=400)
    parser.add_argument(
        "--models",
        nargs="+",
        choices=["extra_trees", "hist_gradient_boosting"],
        default=["extra_trees", "hist_gradient_boosting"],
    )
    return parser.parse_args()


def infer_split(parts: tuple[str, ...]) -> str | None:
    lowered = [part.lower() for part in parts]
    if any(part in {"training", "train"} or part.startswith(("training_", "train_")) for part in lowered):
        return "training"
    if any(part in {"test", "testing"} or part.startswith(("test_", "testing_")) for part in lowered):
        return "test"
    return None


def discover_patches(data_dir: Path, problem: int, limit: int = 0) -> pd.DataFrame:
    import pandas as pd

    root = data_dir / "Dataset" / "32x32_patches" / "32x32_multispectral_patches" / f"problem{problem}"
    if not root.exists():
        raise SystemExit(f"Missing patch root: {root}")

    records: list[PatchRecord] = []
    split_counts: dict[str, int] = {"training": 0, "test": 0}
    for path in sorted(root.rglob("patches_tiff/*.tif")):
        rel = path.relative_to(data_dir)
        split = infer_split(rel.parts)
        if split not in {"training", "test"}:
            continue
        if limit and split_counts[split] >= limit:
            continue
        match = PATCH_RE.match(path.name)
        if not match:
            continue
        date = match.group("date")
        label = int(match.group("label"))
        if label not in PROBLEM_LABELS[problem]:
            continue
        records.append(
            PatchRecord(
                path=path,
                rel_path=str(rel),
                problem=problem,
                split=split,
                date=date,
                year=int(date[:4]),
                month=int(date[4:6]),
                day=int(date[6:8]),
                parcel_id=match.group("parcel"),
                label=label,
            )
        )
        split_counts[split] += 1

    if not records:
        raise SystemExit(f"No problem {problem} TIFF patches found under {root}")
    return pd.DataFrame([record.__dict__ for record in records])


def feature_names(n_bands: int) -> list[str]:
    names: list[str] = ["year", "month", "day"]
    stats = ("mean", "std", "min", "max", "p10", "p50", "p90")
    for band_idx in range(1, n_bands + 1):
        names.extend(f"b{band_idx}_{stat}" for stat in stats)
    return names


def read_patch_features(path: Path) -> np.ndarray:
    import rasterio

    with rasterio.open(path) as src:
        array = src.read().astype(np.float32)
    if array.ndim != 3:
        raise ValueError(f"Expected bands x height x width array for {path}, got shape {array.shape}")
    band_pixels = array.reshape(array.shape[0], -1)
    parts = [
        band_pixels.mean(axis=1),
        band_pixels.std(axis=1),
        band_pixels.min(axis=1),
        band_pixels.max(axis=1),
        np.percentile(band_pixels, 10, axis=1),
        np.percentile(band_pixels, 50, axis=1),
        np.percentile(band_pixels, 90, axis=1),
    ]
    return np.concatenate(parts).astype(np.float32)


def build_or_load_features(manifest: pd.DataFrame, out_dir: Path, force: bool) -> tuple[np.ndarray, list[str]]:
    feature_path = out_dir / "features.npz"
    names_path = out_dir / "feature_names.json"
    expected_rows = len(manifest)
    if feature_path.exists() and names_path.exists() and not force:
        cached = np.load(feature_path)
        features = cached["X"]
        if features.shape[0] == expected_rows:
            names = json.loads(names_path.read_text())
            return features, names

    arrays: list[np.ndarray] = []
    first_n_bands: int | None = None
    for idx, row in manifest.reset_index(drop=True).iterrows():
        patch_features = read_patch_features(Path(row["path"]))
        n_bands = patch_features.shape[0] // 7
        if first_n_bands is None:
            first_n_bands = n_bands
        elif n_bands != first_n_bands:
            raise ValueError(f"Inconsistent band count at row {idx}: {n_bands} != {first_n_bands}")
        date_features = np.array([row["year"], row["month"], row["day"]], dtype=np.float32)
        arrays.append(np.concatenate([date_features, patch_features]))
        if (idx + 1) % 500 == 0:
            print(f"Extracted features for {idx + 1}/{expected_rows} patches")

    if first_n_bands is None:
        raise SystemExit("No features extracted.")
    features = np.vstack(arrays).astype(np.float32)
    names = feature_names(first_n_bands)
    np.savez_compressed(feature_path, X=features)
    names_path.write_text(json.dumps(names, indent=2) + "\n")
    return features, names


def split_train_validation(manifest: pd.DataFrame, random_state: int) -> tuple[np.ndarray, np.ndarray, str]:
    from sklearn.model_selection import StratifiedShuffleSplit

    train_positions = np.flatnonzero(manifest["split"].to_numpy() == "training")
    train_df = manifest.iloc[train_positions].reset_index(drop=False).rename(columns={"index": "position"})

    years = sorted(int(year) for year in train_df["year"].unique())
    if len(years) > 1:
        val_year = years[-1]
        val_positions = train_df.loc[train_df["year"] == val_year, "position"].to_numpy()
        fit_positions = train_df.loc[train_df["year"] != val_year, "position"].to_numpy()
        if len(np.unique(manifest.iloc[val_positions]["label"])) >= 2 and len(fit_positions):
            return fit_positions, val_positions, f"holdout_year_{val_year}"

    labels = train_df["label"].to_numpy()
    _, counts = np.unique(labels, return_counts=True)
    if len(labels) < 5 or counts.min() < 2:
        rng = np.random.default_rng(random_state)
        shuffled = rng.permutation(train_df["position"].to_numpy())
        val_count = max(1, int(round(0.2 * len(shuffled))))
        return shuffled[val_count:], shuffled[:val_count], "random_shuffle_20pct"

    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=random_state)
    fit_idx, val_idx = next(splitter.split(np.zeros(len(train_df)), labels))
    return (
        train_df.iloc[fit_idx]["position"].to_numpy(),
        train_df.iloc[val_idx]["position"].to_numpy(),
        "stratified_shuffle_20pct",
    )


def average_class_accuracy(y_true: np.ndarray, y_pred: np.ndarray, labels: list[int]) -> float:
    scores = []
    for label in labels:
        mask = y_true == label
        if mask.any():
            scores.append(float((y_pred[mask] == label).mean()))
    return float(np.mean(scores)) if scores else 0.0


def model_factory(name: str, random_state: int, n_estimators: int):
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier

    if name == "extra_trees":
        return ExtraTreesClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
            class_weight="balanced",
        )
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(random_state=random_state)
    raise ValueError(name)


def write_confusion_matrix(path: Path, matrix: np.ndarray, labels: list[int]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["actual\\predicted", *labels])
        for label, row in zip(labels, matrix):
            writer.writerow([label, *[int(value) for value in row]])


def train_and_evaluate(
    manifest: pd.DataFrame,
    features: np.ndarray,
    out_dir: Path,
    problem: int,
    model_names: list[str],
    random_state: int,
    n_estimators: int,
) -> dict[str, object]:
    from sklearn.metrics import accuracy_score, confusion_matrix

    labels = sorted(PROBLEM_LABELS[problem])
    y = manifest["label"].to_numpy(dtype=np.int64)
    fit_positions, val_positions, split_name = split_train_validation(manifest, random_state)
    test_positions = np.flatnonzero(manifest["split"].to_numpy() == "test")

    report: dict[str, object] = {
        "problem": problem,
        "labels": PROBLEM_LABELS[problem],
        "validation_split": split_name,
        "n_train_fit": int(len(fit_positions)),
        "n_validation": int(len(val_positions)),
        "n_test": int(len(test_positions)),
        "models": {},
    }

    for name in model_names:
        model = model_factory(name, random_state, n_estimators)
        model.fit(features[fit_positions], y[fit_positions])
        val_pred = model.predict(features[val_positions])
        oa = float(accuracy_score(y[val_positions], val_pred))
        aa = average_class_accuracy(y[val_positions], val_pred, labels)
        q_score = 0.5 * oa + 0.5 * aa
        matrix = confusion_matrix(y[val_positions], val_pred, labels=labels)

        model_dir = out_dir / name
        model_dir.mkdir(parents=True, exist_ok=True)
        write_confusion_matrix(model_dir / "confusion_matrix.csv", matrix, labels)

        val_out = manifest.iloc[val_positions][["rel_path", "date", "year", "parcel_id", "label"]].copy()
        val_out["prediction"] = val_pred
        val_out.to_csv(model_dir / "validation_predictions.csv", index=False)

        if len(test_positions):
            test_pred = model.predict(features[test_positions])
            test_out = manifest.iloc[test_positions][["rel_path", "date", "year", "parcel_id", "label"]].copy()
            test_out["prediction"] = test_pred
            test_out.to_csv(model_dir / "test_predictions.csv", index=False)

        report["models"][name] = {
            "overall_accuracy": oa,
            "average_class_accuracy": aa,
            "q_score": q_score,
            "confusion_matrix_csv": str(model_dir / "confusion_matrix.csv"),
            "validation_predictions_csv": str(model_dir / "validation_predictions.csv"),
            "test_predictions_csv": str(model_dir / "test_predictions.csv") if len(test_positions) else None,
        }
        print(f"{name}: OA={oa:.4f} AA={aa:.4f} Q={q_score:.4f}")

    return report


def main() -> None:
    args = parse_args()
    import pandas as pd

    args.out_dir.mkdir(parents=True, exist_ok=True)
    run_dir = args.out_dir / f"problem{args.problem}"
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = discover_patches(args.data_dir, args.problem, args.limit)
    manifest_for_csv = manifest.copy()
    manifest_for_csv["path"] = manifest_for_csv["path"].astype(str)
    manifest_for_csv.to_csv(run_dir / "manifest.csv", index=False)

    features, names = build_or_load_features(manifest, run_dir, args.force_features)
    pd.DataFrame(features[:50], columns=names).to_csv(run_dir / "features_preview.csv", index=False)

    report = train_and_evaluate(
        manifest=manifest,
        features=features,
        out_dir=run_dir,
        problem=args.problem,
        model_names=args.models,
        random_state=args.random_state,
        n_estimators=args.n_estimators,
    )
    report["manifest_csv"] = str(run_dir / "manifest.csv")
    report["feature_cache"] = str(run_dir / "features.npz")
    report["feature_names"] = str(run_dir / "feature_names.json")
    report["n_rows"] = int(len(manifest))
    report["limit"] = int(args.limit)

    metrics_path = run_dir / "metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {metrics_path}")


if __name__ == "__main__":
    main()
