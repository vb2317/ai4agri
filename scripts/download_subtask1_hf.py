#!/usr/bin/env python3
"""Download AgriPotential files from Hugging Face."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen


DEFAULT_BASE_URL = "https://huggingface.co/datasets/m-sakka/agripotential/resolve/main/"
CSV_FILES = ("metadata.csv", "train.csv", "val.csv", "test.csv")
LABEL_FILES = ("viticulture.tif", "market.tif", "field.tif")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("data/subtask1"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--metadata-only", action="store_true", help="Download only CSV metadata.")
    parser.add_argument("--skip-images", action="store_true", help="Download CSVs and label rasters, but not Sentinel-2 images.")
    parser.add_argument("--label-name", action="append", choices=["viticulture", "market", "field"], default=[])
    parser.add_argument("--limit-images", type=int, default=0, help="Optional max Sentinel-2 images for smoke tests.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    return parser.parse_args()


def download_file(url: str, out_path: Path, timeout: int, overwrite: bool) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 0 and not overwrite:
        print(f"exists {out_path}")
        return

    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    start = time.time()
    with urlopen(url, timeout=timeout) as response, tmp_path.open("wb") as file:
        total = response.headers.get("Content-Length")
        total_int = int(total) if total and total.isdigit() else None
        read = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            file.write(chunk)
            read += len(chunk)
            if total_int and read % (100 * 1024 * 1024) < 1024 * 1024:
                pct = 100.0 * read / total_int
                print(f"{out_path.name}: {pct:.1f}% ({read}/{total_int})", file=sys.stderr)
    tmp_path.replace(out_path)
    elapsed = max(time.time() - start, 0.001)
    print(f"downloaded {out_path} ({out_path.stat().st_size} bytes, {elapsed:.1f}s)")


def read_metadata_filenames(path: Path) -> list[str]:
    with path.open(newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "filename" not in reader.fieldnames:
            raise SystemExit(f"{path} must contain a filename column")
        return [row["filename"] for row in reader if row.get("filename")]


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for name in CSV_FILES:
        download_file(urljoin(args.base_url, name), args.out_dir / name, args.timeout, args.overwrite)

    if args.metadata_only:
        return

    labels = args.label_name or ["viticulture"]
    for label in labels:
        name = f"{label}.tif"
        download_file(urljoin(args.base_url, name), args.out_dir / name, args.timeout, args.overwrite)

    if args.skip_images:
        return

    filenames = read_metadata_filenames(args.out_dir / "metadata.csv")
    if args.limit_images:
        filenames = filenames[: args.limit_images]
    for filename in filenames:
        download_file(urljoin(args.base_url, filename), args.out_dir / filename, args.timeout, args.overwrite)


if __name__ == "__main__":
    main()
