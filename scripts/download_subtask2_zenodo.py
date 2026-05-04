#!/usr/bin/env python3
"""Download the DACIA5/AI4Agri Subtask 2 Zenodo archive.

This intentionally uses only the Python standard library so it can run on a
fresh RunPod before project dependencies are installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


ZENODO_RECORD_API = "https://zenodo.org/api/records/14283243"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("data/subtask2/downloads"))
    parser.add_argument("--record-api", default=ZENODO_RECORD_API)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    parser.add_argument("--force", action="store_true", help="Redownload even if the file already exists.")
    return parser.parse_args()


def fetch_json(url: str) -> dict:
    with urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def choose_archive(record: dict) -> dict:
    files = record.get("files", [])
    candidates = [
        file
        for file in files
        if str(file.get("key", "")).lower().endswith(".zip")
        and ("ai4agri" in str(file.get("key", "")).lower() or "sentinel" in str(file.get("key", "")).lower())
    ]
    if not candidates:
        candidates = [file for file in files if str(file.get("key", "")).lower().endswith(".zip")]
    if not candidates:
        raise SystemExit("No ZIP archive found in Zenodo record metadata.")
    return candidates[0]


def md5_file(path: Path, chunk_size: int) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, path: Path, chunk_size: int) -> None:
    with urlopen(url, timeout=60) as response, path.open("wb") as handle:
        total = int(response.headers.get("Content-Length", "0") or 0)
        done = 0
        for chunk in iter(lambda: response.read(chunk_size), b""):
            handle.write(chunk)
            done += len(chunk)
            if total:
                pct = 100.0 * done / total
                print(f"\rDownloaded {done / (1024 ** 2):.1f} MiB / {total / (1024 ** 2):.1f} MiB ({pct:.1f}%)", end="")
            else:
                print(f"\rDownloaded {done / (1024 ** 2):.1f} MiB", end="")
    print()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    record = fetch_json(args.record_api)
    archive = choose_archive(record)
    key = archive["key"]
    links = archive.get("links", {})
    url = links.get("self") or links.get("download")
    if not url:
        raise SystemExit(f"No download URL found for {key}")

    out_path = args.out_dir / key
    checksum = str(archive.get("checksum", ""))
    expected_md5 = checksum.split(":", 1)[1] if checksum.startswith("md5:") else None

    if out_path.exists() and not args.force:
        print(f"Already exists: {out_path}")
    else:
        print(f"Downloading: {key}")
        print(f"URL: {url}")
        download(url, out_path, args.chunk_size)

    if expected_md5:
        actual_md5 = md5_file(out_path, args.chunk_size)
        print(f"md5 expected: {expected_md5}")
        print(f"md5 actual:   {actual_md5}")
        if actual_md5 != expected_md5:
            raise SystemExit("Checksum mismatch.")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
