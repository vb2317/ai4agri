#!/usr/bin/env python3
"""Inspect AgriPotential metadata and optionally smoke-read small samples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen


DEFAULT_BASE_URL = "https://huggingface.co/datasets/m-sakka/agripotential/resolve/main/"
SPLITS = ("train", "val", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Local AgriPotential directory. If omitted, reads CSV metadata from Hugging Face URLs.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/subtask1/inspection"))
    parser.add_argument("--splits", nargs="+", default=list(SPLITS), choices=SPLITS)
    parser.add_argument("--label-name", default="viticulture", choices=["viticulture", "market", "field"])
    parser.add_argument("--limit", type=int, default=0, help="Number of samples per split to smoke-read.")
    parser.add_argument(
        "--read-pixels",
        action="store_true",
        help="Read Sentinel-2 windows for --limit samples. This is expensive on remote URLs.",
    )
    parser.add_argument(
        "--read-labels",
        action="store_true",
        help="Read label windows for --limit samples when the label GeoTIFF is available.",
    )
    return parser.parse_args()


def data_ref(data_dir: str | None, name: str) -> str:
    if data_dir:
        return str(Path(data_dir) / name)
    return urljoin(DEFAULT_BASE_URL, name)


def existing_local_ref(data_dir: str | None, name: str) -> str | None:
    if not data_dir:
        return data_ref(None, name)
    path = Path(data_dir) / name
    return str(path) if path.exists() else None


def read_csv_rows(data_dir: str | None, name: str) -> list[dict[str, str]]:
    ref = data_ref(data_dir, name)
    if ref.startswith("http"):
        with urlopen(ref, timeout=60) as response:
            lines = [line.decode("utf-8") for line in response]
    else:
        lines = Path(ref).read_text().splitlines()
    return list(csv.DictReader(lines))


def summarize_split(rows: list[dict[str, str]]) -> dict[str, object]:
    columns = list(rows[0].keys()) if rows else []
    summary: dict[str, object] = {
        "rows": int(len(rows)),
        "columns": columns,
    }
    for column in ("patch_size", "n_annotated"):
        values = [int(row[column]) for row in rows if row.get(column, "").strip()]
        if values:
            summary[column] = {
                "min": min(values),
                "max": max(values),
                "unique": sorted(set(values))[:20],
            }
    if {"row", "col"}.issubset(columns) and rows:
        row_values = [int(row["row"]) for row in rows]
        col_values = [int(row["col"]) for row in rows]
        summary["row_range"] = [min(row_values), max(row_values)]
        summary["col_range"] = [min(col_values), max(col_values)]
    if "patch_id" in columns:
        summary["patch_id_examples"] = [str(row["patch_id"]) for row in rows[:5]]
    return summary


def read_window(path: str, row: int, col: int, patch_size: int) -> np.ndarray:
    import numpy as np
    import rasterio
    from rasterio.windows import Window

    with rasterio.open(path) as src:
        return src.read(window=Window(col, row, patch_size, patch_size))


def sample_stats(
    data_dir: str | None,
    metadata: list[dict[str, str]],
    patches: list[dict[str, str]],
    label_name: str,
    limit: int,
    read_pixels: bool,
    read_labels: bool,
) -> list[dict[str, object]]:
    if limit <= 0 or not (read_pixels or read_labels):
        return []

    import numpy as np

    records: list[dict[str, object]] = []
    sentinel_files = [str(row["filename"]) for row in metadata if row.get("filename")]
    label_ref = existing_local_ref(data_dir, f"{label_name}.tif")

    for patch in patches[:limit]:
        row = int(patch["row"])
        col = int(patch["col"])
        patch_size = int(patch["patch_size"])
        record: dict[str, object] = {
            "patch_id": str(patch["patch_id"]),
            "row": row,
            "col": col,
            "patch_size": patch_size,
        }

        if read_pixels:
            arrays = []
            for filename in sentinel_files:
                arrays.append(read_window(data_ref(data_dir, filename), row, col, patch_size))
            data = np.stack(arrays, axis=0)
            record["data_shape"] = list(data.shape)
            record["data_dtype"] = str(data.dtype)
            record["data_min"] = float(np.nanmin(data))
            record["data_max"] = float(np.nanmax(data))
            record["data_mean"] = float(np.nanmean(data))

        if read_labels and label_ref:
            label = read_window(label_ref, row, col, patch_size)[0].astype(np.uint8)
            values, counts = np.unique(label, return_counts=True)
            record["label_shape"] = list(label.shape)
            record["label_dtype"] = str(label.dtype)
            record["label_counts"] = {str(int(v)): int(c) for v, c in zip(values, counts)}
        elif read_labels:
            record["label_error"] = f"{label_name}.tif not found"

        records.append(record)
    return records


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    metadata = read_csv_rows(args.data_dir, "metadata.csv")
    metadata_columns = list(metadata[0].keys()) if metadata else []
    report: dict[str, object] = {
        "source": args.data_dir or DEFAULT_BASE_URL,
        "label_name": args.label_name,
        "metadata": {
            "rows": int(len(metadata)),
            "columns": metadata_columns,
            "filename_examples": [str(row["filename"]) for row in metadata[:5] if row.get("filename")],
        },
        "splits": {},
    }

    for split in args.splits:
        try:
            patches = read_csv_rows(args.data_dir, f"{split}.csv")
        except Exception as exc:
            report["splits"][split] = {"error": str(exc)}
            continue

        split_report = summarize_split(patches)
        split_report["samples"] = sample_stats(
            args.data_dir,
            metadata,
            patches,
            args.label_name,
            args.limit,
            args.read_pixels,
            args.read_labels,
        )
        report["splits"][split] = split_report

    out_path = args.out_dir / "subtask1_inspection.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
