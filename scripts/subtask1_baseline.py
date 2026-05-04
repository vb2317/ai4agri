#!/usr/bin/env python3
"""Train and run a sampled-pixel AgriPotential baseline."""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import struct
import zipfile
import zlib
from contextlib import ExitStack
from pathlib import Path


SPLIT_COLUMNS = ("patch_id", "row", "col", "patch_size", "n_annotated")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    train = subparsers.add_parser("train", help="Train sampled-pixel tabular models from local rasters.")
    train.add_argument("--data-dir", required=True, type=Path, help="Local AgriPotential data directory.")
    train.add_argument("--out-dir", type=Path, default=Path("results/subtask1/baseline"))
    train.add_argument("--label-name", default="viticulture", choices=["viticulture", "market", "field"])
    train.add_argument("--train-split", default="train.csv")
    train.add_argument("--val-split", default="val.csv")
    train.add_argument("--patch-limit", type=int, default=0, help="Optional max train patches for smoke tests.")
    train.add_argument("--val-patch-limit", type=int, default=0, help="Optional max validation patches.")
    train.add_argument("--pixels-per-patch", type=int, default=512)
    train.add_argument("--max-train-pixels", type=int, default=200000)
    train.add_argument("--random-state", type=int, default=42)
    train.add_argument("--model", choices=["hist_gradient_boosting", "extra_trees"], default="hist_gradient_boosting")
    train.add_argument("--sampling", choices=["uniform", "class_balanced"], default="class_balanced")
    train.add_argument("--feature-mode", choices=["raw", "raw_temporal"], default="raw_temporal")

    infer = subparsers.add_parser("infer", help="Predict test masks and write a CodaBench ZIP.")
    infer.add_argument("--data-dir", required=True, type=Path, help="Local AgriPotential data directory.")
    infer.add_argument("--model-path", type=Path, default=Path("results/subtask1/baseline/model.pkl"))
    infer.add_argument("--split", default="test.csv")
    infer.add_argument("--out", type=Path, default=Path("results/subtask1/submissions/subtask1_baseline.zip"))
    infer.add_argument("--limit", type=int, default=0, help="Optional max patches for smoke tests.")
    infer.add_argument("--feature-mode", choices=["raw", "raw_temporal"], default=None, help="Override saved feature mode.")

    return parser.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        rows = list(csv.DictReader(file))
    return rows


def require_split_columns(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        raise SystemExit(f"empty split CSV: {path}")
    missing = [column for column in SPLIT_COLUMNS if column not in rows[0]]
    if missing:
        raise SystemExit(f"{path} is missing required columns: {', '.join(missing)}")


def metadata_files(data_dir: Path) -> list[Path]:
    metadata_path = data_dir / "metadata.csv"
    rows = read_csv_rows(metadata_path)
    if not rows or "filename" not in rows[0]:
        raise SystemExit(f"{metadata_path} must contain a filename column")
    files = [data_dir / row["filename"] for row in rows if row.get("filename")]
    missing = [path for path in files if not path.exists()]
    if missing:
        raise SystemExit("missing Sentinel-2 raster files: " + ", ".join(str(path) for path in missing[:5]))
    return files


def read_window(source, row: int, col: int, patch_size: int):
    import rasterio
    from rasterio.windows import Window

    window = Window(col, row, patch_size, patch_size)
    if hasattr(source, "read"):
        return source.read(window=window)
    with rasterio.open(source) as src:
        return src.read(window=window)


def read_patch_stack(sources, patch: dict[str, str]):
    import numpy as np

    row = int(patch["row"])
    col = int(patch["col"])
    patch_size = int(patch["patch_size"])
    arrays = [read_window(source, row, col, patch_size) for source in sources]
    return np.stack(arrays, axis=0)


def pixel_features(stack, feature_mode: str = "raw"):
    import numpy as np

    # stack: time, bands, height, width -> pixels, flattened time-band features.
    raw = np.moveaxis(stack, (0, 1), (-2, -1)).reshape(-1, stack.shape[0] * stack.shape[1]).astype("float32")
    if feature_mode == "raw":
        return raw
    if feature_mode != "raw_temporal":
        raise ValueError(f"unknown feature mode: {feature_mode}")

    summaries = []
    for reducer in (np.nanmean, np.nanstd, np.nanmin, np.nanmax):
        reduced = reducer(stack.astype("float32", copy=False), axis=0)
        summaries.append(np.moveaxis(reduced, 0, -1).reshape(-1, stack.shape[1]))
    return np.concatenate([raw, *summaries], axis=1).astype("float32", copy=False)


def valid_label_mask(labels):
    import numpy as np

    return np.isfinite(labels) & (labels >= 0) & (labels <= 4)


def balanced_indices(y_all, valid, pixels_per_patch: int, rng):
    import numpy as np

    classes = np.unique(y_all[valid])
    if classes.size == 0:
        return valid[:0]
    base = max(pixels_per_patch // classes.size, 1)
    remainder = pixels_per_patch - base * classes.size
    chosen_blocks = []
    for offset, label in enumerate(rng.permutation(classes)):
        candidates = valid[y_all[valid] == label]
        count = min(candidates.size, base + (1 if offset < remainder else 0))
        if count:
            chosen_blocks.append(rng.choice(candidates, size=count, replace=False))
    chosen = np.concatenate(chosen_blocks) if chosen_blocks else valid[:0]
    if chosen.size < min(pixels_per_patch, valid.size):
        missing = min(pixels_per_patch, valid.size) - chosen.size
        remaining = np.setdiff1d(valid, chosen, assume_unique=False)
        if remaining.size:
            chosen = np.concatenate([chosen, rng.choice(remaining, size=min(missing, remaining.size), replace=False)])
    rng.shuffle(chosen)
    return chosen


def sample_patch_pixels(stack, labels, pixels_per_patch: int, rng, sampling: str, feature_mode: str):
    import numpy as np

    x_all = pixel_features(stack, feature_mode)
    y_all = labels.reshape(-1).astype("int64")
    valid = np.flatnonzero(valid_label_mask(y_all))
    if valid.size == 0:
        return x_all[:0], y_all[:0]
    count = min(pixels_per_patch, valid.size)
    if sampling == "class_balanced":
        chosen = balanced_indices(y_all, valid, count, rng)
    elif sampling == "uniform":
        chosen = rng.choice(valid, size=count, replace=False)
    else:
        raise ValueError(f"unknown sampling mode: {sampling}")
    return x_all[chosen], y_all[chosen]


def collect_samples(
    data_dir: Path,
    raster_sources,
    label_source,
    label_name: str,
    split_name: str,
    patch_limit: int,
    pixels_per_patch: int,
    max_pixels: int,
    random_state: int,
    sampling: str,
    feature_mode: str,
):
    import numpy as np

    split_path = data_dir / split_name
    rows = read_csv_rows(split_path)
    require_split_columns(rows, split_path)
    rng = np.random.default_rng(random_state)
    rng.shuffle(rows)
    if patch_limit:
        rows = rows[:patch_limit]

    label_path = data_dir / f"{label_name}.tif"
    if not label_path.exists():
        raise SystemExit(f"missing label raster: {label_path}")

    feature_blocks = []
    label_blocks = []
    patches_read = 0
    for patch in rows:
        stack = read_patch_stack(raster_sources, patch)
        labels = read_window(label_source, int(patch["row"]), int(patch["col"]), int(patch["patch_size"]))[0]
        x_patch, y_patch = sample_patch_pixels(stack, labels, pixels_per_patch, rng, sampling, feature_mode)
        if x_patch.size:
            feature_blocks.append(x_patch)
            label_blocks.append(y_patch)
        patches_read += 1
        if feature_blocks and sum(block.shape[0] for block in feature_blocks) >= max_pixels:
            break

    if not feature_blocks:
        raise SystemExit(f"no labeled pixels sampled from {split_name}")
    x = np.concatenate(feature_blocks, axis=0)
    y = np.concatenate(label_blocks, axis=0)
    if x.shape[0] > max_pixels:
        chosen = rng.choice(x.shape[0], size=max_pixels, replace=False)
        x = x[chosen]
        y = y[chosen]
    return x, y, patches_read


def accuracy_pm1(y_true, y_pred) -> float:
    import numpy as np

    return float(np.mean(np.abs(y_true - y_pred) <= 1))


def make_model(model_name: str, random_state: int):
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline

    if model_name == "extra_trees":
        estimator = ExtraTreesClassifier(
            n_estimators=300,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=-1,
        )
    else:
        estimator = HistGradientBoostingClassifier(random_state=random_state)
    return make_pipeline(SimpleImputer(strategy="median"), estimator)


def train_command(args: argparse.Namespace) -> None:
    import numpy as np
    import rasterio
    from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error

    raster_files = metadata_files(args.data_dir)
    label_path = args.data_dir / f"{args.label_name}.tif"
    with ExitStack() as stack:
        raster_sources = [stack.enter_context(rasterio.open(path)) for path in raster_files]
        label_source = stack.enter_context(rasterio.open(label_path))
        x_train, y_train, train_patches = collect_samples(
            args.data_dir,
            raster_sources,
            label_source,
            args.label_name,
            args.train_split,
            args.patch_limit,
            args.pixels_per_patch,
            args.max_train_pixels,
            args.random_state,
            args.sampling,
            args.feature_mode,
        )
        x_val, y_val, val_patches = collect_samples(
            args.data_dir,
            raster_sources,
            label_source,
            args.label_name,
            args.val_split,
            args.val_patch_limit,
            args.pixels_per_patch,
            max(args.pixels_per_patch, min(args.max_train_pixels // 4, 50000)),
            args.random_state + 1,
            args.sampling,
            args.feature_mode,
        )

    model = make_model(args.model, args.random_state)
    model.fit(x_train, y_train)
    val_pred = np.clip(model.predict(x_val).astype("int64"), 0, 4)

    report = {
        "model": args.model,
        "label_name": args.label_name,
        "sampling": args.sampling,
        "feature_mode": args.feature_mode,
        "train_split": args.train_split,
        "val_split": args.val_split,
        "train_patches_read": train_patches,
        "val_patches_read": val_patches,
        "train_pixels": int(x_train.shape[0]),
        "val_pixels": int(x_val.shape[0]),
        "feature_count": int(x_train.shape[1]),
        "exact_accuracy": float(accuracy_score(y_val, val_pred)),
        "accuracy_pm1": accuracy_pm1(y_val, val_pred),
        "mean_absolute_error": float(mean_absolute_error(y_val, val_pred)),
        "label_counts_train": {str(int(k)): int(v) for k, v in zip(*np.unique(y_train, return_counts=True))},
        "label_counts_val": {str(int(k)): int(v) for k, v in zip(*np.unique(y_val, return_counts=True))},
        "confusion_matrix": confusion_matrix(y_val, val_pred, labels=[0, 1, 2, 3, 4]).astype(int).tolist(),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.out_dir / "model.pkl"
    with model_path.open("wb") as file:
        pickle.dump(
            {
                "model": model,
                "raster_count": len(raster_files),
                "feature_mode": args.feature_mode,
                "sampling": args.sampling,
                "report": report,
            },
            file,
        )
    metrics_path = args.out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote {model_path}")
    print(f"Wrote {metrics_path}")


def png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(payload, checksum)
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", checksum & 0xFFFFFFFF)


def grayscale_png(width: int, height: int, values) -> bytes:
    import numpy as np

    array = np.asarray(values, dtype="uint8")
    if array.shape != (height, width):
        raise ValueError(f"expected mask shape {(height, width)}, got {array.shape}")
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    rows = [bytes([0]) + array[row].tobytes() for row in range(height)]
    raw = b"".join(rows)
    return signature + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(raw, level=9)) + png_chunk(b"IEND", b"")


def infer_command(args: argparse.Namespace) -> None:
    import numpy as np
    import rasterio

    raster_files = metadata_files(args.data_dir)
    split_path = args.data_dir / args.split
    rows = read_csv_rows(split_path)
    require_split_columns(rows, split_path)
    if args.limit:
        rows = rows[: args.limit]

    with args.model_path.open("rb") as file:
        payload = pickle.load(file)
    model = payload["model"]
    feature_mode = args.feature_mode or payload.get("feature_mode", "raw")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        raster_sources = [stack.enter_context(rasterio.open(path)) for path in raster_files]
        with zipfile.ZipFile(args.out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for index, patch in enumerate(rows, start=1):
                patch_size = int(patch["patch_size"])
                stack_array = read_patch_stack(raster_sources, patch)
                x = pixel_features(stack_array, feature_mode)
                prediction = np.clip(model.predict(x).astype("uint8"), 0, 4).reshape(patch_size, patch_size)
                zf.writestr(f"{patch['patch_id']}.png", grayscale_png(patch_size, patch_size, prediction))
                if index % 50 == 0:
                    print(f"predicted {index}/{len(rows)}")
    print(f"Wrote {args.out} with {len(rows)} PNG mask(s)")


def main() -> None:
    args = parse_args()
    if args.command == "train":
        train_command(args)
    elif args.command == "infer":
        infer_command(args)
    else:
        raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
