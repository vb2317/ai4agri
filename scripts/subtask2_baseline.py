#!/usr/bin/env python3
"""Build DACIA5 Subtask 2 manifests, features, and tabular baselines."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable


PROBLEM_LABEL_COUNTS = {"problem1": 7, "problem2": 2}
PATCH_RE = re.compile(r"^patch_(?P<date>\d{8})_(?P<parcel_id>\d+)_(?P<patch_index>\d+)\.tif$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    manifest = subparsers.add_parser("manifest", help="Discover patch TIFFs and write a CSV manifest.")
    manifest.add_argument("--data-dir", required=True, type=Path, help="Extracted DACIA5 dataset root.")
    manifest.add_argument("--out", type=Path, default=Path("results/subtask2/manifest.csv"))
    manifest.add_argument("--problem", choices=["problem1", "problem2", "all"], default="all")
    manifest.add_argument("--limit", type=int, default=0, help="Optional max files per problem/split.")
    manifest.add_argument(
        "--label-mode",
        choices=["none", "filename-last-token"],
        default="none",
        help="How to populate label. Use filename-last-token only after the DACIA5 label token is confirmed.",
    )

    features = subparsers.add_parser("features", help="Extract cached tabular features from manifest TIFFs.")
    features.add_argument("--manifest", type=Path, default=Path("results/subtask2/manifest.csv"))
    features.add_argument("--out", type=Path, default=Path("results/subtask2/features/subtask2_features.csv"))
    features.add_argument("--limit", type=int, default=0, help="Optional max manifest rows to process.")
    features.add_argument(
        "--percentiles",
        default="5,25,50,75,95",
        help="Comma-separated per-band percentiles. Use empty string to disable.",
    )

    train = subparsers.add_parser("train", help="Train ExtraTrees and HistGradientBoosting baselines.")
    train.add_argument("--features", type=Path, default=Path("results/subtask2/features/subtask2_features.csv"))
    train.add_argument("--out-dir", type=Path, default=Path("results/subtask2/baseline"))
    train.add_argument("--problem", choices=["problem1", "problem2"], default="problem1")
    train.add_argument("--random-state", type=int, default=42)
    train.add_argument("--test-size", type=float, default=0.25)
    train.add_argument(
        "--allow-unverified-labels",
        action="store_true",
        help="Permit labels marked as unverified, for experiments after a human confirms the label source.",
    )

    return parser.parse_args()


def infer_problem(parts: Iterable[str]) -> str | None:
    lowered = [part.lower() for part in parts]
    if "problem1" in lowered:
        return "problem1"
    if "problem2" in lowered:
        return "problem2"
    return None


def infer_split(parts: Iterable[str]) -> str | None:
    lowered = [part.lower() for part in parts]
    if any(part == "training" or part.startswith("training_") or part == "train" for part in lowered):
        return "training"
    if any(part == "test" or part.startswith("test_") or part == "testing" for part in lowered):
        return "test"
    return None


def parse_patch_name(path: Path) -> dict[str, object]:
    match = PATCH_RE.match(path.name)
    if not match:
        return {
            "date": "",
            "year": "",
            "month": "",
            "day": "",
            "day_of_year": "",
            "parcel_id": "",
            "patch_index": "",
            "filename_parse_ok": "0",
        }
    date_text = match.group("date")
    date = datetime.strptime(date_text, "%Y%m%d")
    return {
        "date": date_text,
        "year": date.year,
        "month": date.month,
        "day": date.day,
        "day_of_year": int(date.strftime("%j")),
        "parcel_id": int(match.group("parcel_id")),
        "patch_index": int(match.group("patch_index")),
        "filename_parse_ok": "1",
    }


def label_from_name(patch_index: object, mode: str) -> tuple[str, str]:
    if mode == "none" or patch_index == "":
        return "", "not_set"
    value = int(patch_index)
    return str(value), "filename_last_token_unverified"


def discover_patch_tiffs(data_dir: Path, problem_filter: str, limit: int, label_mode: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    counts: Counter[tuple[str, str]] = Counter()
    for path in sorted(data_dir.rglob("*.tif")):
        rel = path.relative_to(data_dir)
        parts = rel.parts
        problem = infer_problem(parts)
        split = infer_split(parts)
        if not problem or not split:
            continue
        if problem_filter != "all" and problem != problem_filter:
            continue
        if "patches_tiff" not in {part.lower() for part in parts}:
            continue
        key = (problem, split)
        if limit and counts[key] >= limit:
            continue
        parsed = parse_patch_name(path)
        label_candidate = "" if parsed["patch_index"] == "" else str(parsed["patch_index"])
        label, label_status = label_from_name(parsed["patch_index"], label_mode)
        rows.append(
            {
                "path": str(path),
                "relative_path": str(rel),
                "problem": problem,
                "split": split,
                **parsed,
                "label_candidate": label_candidate,
                "label": label,
                "label_status": label_status,
            }
        )
        counts[key] += 1
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def read_tiff(path: Path):
    import rasterio

    with rasterio.open(path) as src:
        return src.read()


def safe_float(value: object) -> float:
    if value == "" or value is None:
        return math.nan
    return float(value)


def parse_percentiles(text: str) -> list[int]:
    if not text.strip():
        return []
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def band_features(array, percentiles: list[int]) -> dict[str, float]:
    import numpy as np

    arr = array.astype("float32", copy=False)
    features: dict[str, float] = {}
    for index in range(arr.shape[0]):
        band = arr[index]
        prefix = f"b{index + 1:02d}"
        features[f"{prefix}_mean"] = float(np.nanmean(band))
        features[f"{prefix}_std"] = float(np.nanstd(band))
        features[f"{prefix}_min"] = float(np.nanmin(band))
        features[f"{prefix}_max"] = float(np.nanmax(band))
        for percentile in percentiles:
            features[f"{prefix}_p{percentile:02d}"] = float(np.nanpercentile(band, percentile))
    return features


def command_manifest(args: argparse.Namespace) -> None:
    rows = discover_patch_tiffs(args.data_dir, args.problem, args.limit, args.label_mode)
    fieldnames = [
        "path",
        "relative_path",
        "problem",
        "split",
        "date",
        "year",
        "month",
        "day",
        "day_of_year",
        "parcel_id",
        "patch_index",
        "filename_parse_ok",
        "label_candidate",
        "label",
        "label_status",
    ]
    write_csv(args.out, rows, fieldnames)
    summary = Counter((row["problem"], row["split"], row["label_status"]) for row in rows)
    print(json.dumps({"rows": len(rows), "out": str(args.out), "summary": {str(k): v for k, v in summary.items()}}, indent=2))


def command_features(args: argparse.Namespace) -> None:
    percentiles = parse_percentiles(args.percentiles)
    manifest = read_csv(args.manifest)
    if args.limit:
        manifest = manifest[: args.limit]
    rows: list[dict[str, object]] = []
    for index, row in enumerate(manifest, start=1):
        try:
            array = read_tiff(Path(row["path"]))
            features = band_features(array, percentiles)
            shape = "x".join(str(part) for part in array.shape)
            error = ""
        except Exception as exc:
            features = {}
            shape = ""
            error = str(exc)
        out_row: dict[str, object] = {
            "path": row["path"],
            "relative_path": row["relative_path"],
            "problem": row["problem"],
            "split": row["split"],
            "date": row["date"],
            "year": row["year"],
            "month": row["month"],
            "day": row["day"],
            "day_of_year": row["day_of_year"],
            "parcel_id": row["parcel_id"],
            "patch_index": row["patch_index"],
            "label_candidate": row.get("label_candidate", ""),
            "label": row["label"],
            "label_status": row["label_status"],
            "array_shape": shape,
            "feature_error": error,
        }
        out_row.update(features)
        rows.append(out_row)
        if index % 250 == 0:
            print(f"processed {index}/{len(manifest)}", file=sys.stderr)
    fieldnames = list(rows[0].keys()) if rows else []
    write_csv(args.out, rows, fieldnames)
    errors = sum(1 for row in rows if row["feature_error"])
    print(json.dumps({"rows": len(rows), "errors": errors, "out": str(args.out)}, indent=2))


def metric_report(y_true, y_pred, labels: list[int]) -> dict[str, object]:
    import numpy as np
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix

    oa = float(accuracy_score(y_true, y_pred))
    aa = float(balanced_accuracy_score(y_true, y_pred))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "overall_accuracy": oa,
        "average_accuracy": aa,
        "q_score": 0.5 * oa + 0.5 * aa,
        "labels": labels,
        "confusion_matrix": matrix.astype(int).tolist(),
        "support": {str(label): int(np.sum(np.asarray(y_true) == label)) for label in labels},
    }


def feature_columns(rows: list[dict[str, str]]) -> list[str]:
    excluded = {
        "path",
        "relative_path",
        "problem",
        "split",
        "date",
        "label_candidate",
        "label",
        "label_status",
        "array_shape",
        "feature_error",
    }
    return [name for name in rows[0] if name not in excluded]


def split_train_validation(rows: list[dict[str, str]], random_state: int, test_size: float):
    from sklearn.model_selection import train_test_split

    years = sorted({int(row["year"]) for row in rows if row["year"]})
    if len(years) > 1:
        holdout = years[-1]
        train_rows = [row for row in rows if int(row["year"]) < holdout]
        valid_rows = [row for row in rows if int(row["year"]) == holdout]
        if train_rows and valid_rows:
            return train_rows, valid_rows, f"year_holdout_{holdout}"
    labels = [int(row["label"]) for row in rows]
    train_rows, valid_rows = train_test_split(
        rows,
        test_size=test_size,
        random_state=random_state,
        stratify=labels if len(set(labels)) > 1 else None,
    )
    return train_rows, valid_rows, "stratified_random"


def rows_to_xy(rows: list[dict[str, str]], columns: list[str]):
    import numpy as np

    x = np.asarray([[safe_float(row[column]) for column in columns] for row in rows], dtype="float32")
    y = np.asarray([int(row["label"]) for row in rows], dtype="int64")
    return x, y


def rows_to_x(rows: list[dict[str, str]], columns: list[str]):
    import numpy as np

    return np.asarray([[safe_float(row[column]) for column in columns] for row in rows], dtype="float32")


def write_predictions(path: Path, rows: list[dict[str, str]], predictions) -> None:
    out_rows = [
        {
            "relative_path": row["relative_path"],
            "problem": row["problem"],
            "split": row["split"],
            "date": row["date"],
            "parcel_id": row["parcel_id"],
            "patch_index": row["patch_index"],
            "prediction": int(prediction),
        }
        for row, prediction in zip(rows, predictions)
    ]
    write_csv(path, out_rows)


def command_train(args: argparse.Namespace) -> None:
    rows = [
        row
        for row in read_csv(args.features)
        if row["problem"] == args.problem and row["split"] == "training" and row["label"] != "" and not row["feature_error"]
    ]
    if not rows:
        raise SystemExit(
            "No labeled training features were found. Confirm DACIA5 label interpretation, then rerun "
            "`manifest --label-mode filename-last-token` if the final filename token is the label, or add labels to the manifest."
        )
    if not args.allow_unverified_labels:
        unverified = sorted({row["label_status"] for row in rows if "unverified" in row["label_status"]})
        if unverified:
            raise SystemExit(
                "Training labels are marked unverified: "
                + ", ".join(unverified)
                + ". Rerun with --allow-unverified-labels only after confirming the DACIA5 label source."
            )
    max_label = PROBLEM_LABEL_COUNTS[args.problem] - 1
    invalid_labels = sorted({int(row["label"]) for row in rows if not 0 <= int(row["label"]) <= max_label})
    if invalid_labels:
        raise SystemExit(
            f"Found labels outside the valid {args.problem} range 0..{max_label}: {invalid_labels}. "
            "This usually means the filename token is not the crop label."
        )
    columns = feature_columns(rows)
    train_rows, valid_rows, split_method = split_train_validation(rows, args.random_state, args.test_size)
    x_train, y_train = rows_to_xy(train_rows, columns)
    x_valid, y_valid = rows_to_xy(valid_rows, columns)
    labels = list(range(PROBLEM_LABEL_COUNTS[args.problem]))

    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline

    models = {
        "extra_trees": make_pipeline(
            SimpleImputer(strategy="median"),
            ExtraTreesClassifier(
                n_estimators=500,
                random_state=args.random_state,
                class_weight="balanced",
                n_jobs=-1,
            ),
        ),
        "hist_gradient_boosting": make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(random_state=args.random_state),
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "problem": args.problem,
        "split_method": split_method,
        "feature_count": len(columns),
        "train_rows": len(train_rows),
        "valid_rows": len(valid_rows),
        "label_status_counts": dict(Counter(row["label_status"] for row in rows)),
        "models": {},
    }
    all_rows = [row for row in read_csv(args.features) if row["problem"] == args.problem and not row["feature_error"]]
    test_rows = [row for row in all_rows if row["split"] == "test"]

    for name, model in models.items():
        model.fit(x_train, y_train)
        valid_pred = model.predict(x_valid)
        model_report = metric_report(y_valid, valid_pred, labels)
        report["models"][name] = model_report
        write_predictions(args.out_dir / f"{args.problem}_{name}_valid_predictions.csv", valid_rows, valid_pred)
        if test_rows:
            x_test = rows_to_x(test_rows, columns)
            test_pred = model.predict(x_test)
            write_predictions(args.out_dir / f"{args.problem}_{name}_test_predictions.csv", test_rows, test_pred)

    metrics_path = args.out_dir / f"{args.problem}_metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote {metrics_path}")


def main() -> None:
    args = parse_args()
    if args.command == "manifest":
        command_manifest(args)
    elif args.command == "features":
        command_features(args)
    elif args.command == "train":
        command_train(args)
    else:
        raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
