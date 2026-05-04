#!/usr/bin/env python3
"""Download AgriPotential Subtask 1 files from Hugging Face."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests


BASE_URL = "https://huggingface.co/datasets/m-sakka/agripotential/resolve/main/"
CSV_FILES = ["train.csv", "val.csv", "test.csv", "metadata.csv"]
LABEL_FILES = ["viticulture.tif", "market.tif", "field.tif"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("data/subtask1/agripotential"))
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--labels", action="store_true", help="Download label GeoTIFFs.")
    parser.add_argument("--images", action="store_true", help="Download all Sentinel-2 image GeoTIFFs listed in metadata.csv.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    return parser.parse_args()


def download_file(url: str, path: Path, force: bool) -> None:
    if path.exists() and not force:
        print(f"exists {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".part")
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with tmp_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    tmp_path.replace(path)
    print(f"wrote {path}")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for name in CSV_FILES:
        download_file(urljoin(args.base_url, name), args.out_dir / name, args.force)

    if args.labels:
        for name in LABEL_FILES:
            download_file(urljoin(args.base_url, name), args.out_dir / name, args.force)

    if args.images:
        metadata = pd.read_csv(args.out_dir / "metadata.csv")
        for name in metadata["filename"]:
            download_file(urljoin(args.base_url, name), args.out_dir / str(name), args.force)


if __name__ == "__main__":
    main()
