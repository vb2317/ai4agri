#!/usr/bin/env python3
"""Create a valid constant-mask AgriPotential CodaBench ZIP."""

from __future__ import annotations

import argparse
import csv
import struct
import zlib
import zipfile
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen


DEFAULT_BASE_URL = "https://huggingface.co/datasets/m-sakka/agripotential/resolve/main/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Local AgriPotential directory containing test.csv. If omitted, reads from Hugging Face.",
    )
    parser.add_argument(
        "--split-csv",
        type=str,
        default="test.csv",
        help="Split CSV name, local path, or URL. Defaults to test.csv.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/subtask1/submissions/constant_class_2.zip"),
        help="Output ZIP path.",
    )
    parser.add_argument("--class-id", type=int, default=2, help="Constant class id to write, expected 0..4.")
    parser.add_argument("--patch-id-column", default="patch_id")
    parser.add_argument("--patch-size-column", default="patch_size")
    parser.add_argument("--default-patch-size", type=int, default=128)
    parser.add_argument("--limit", type=int, default=0, help="Optional max masks for smoke tests.")
    return parser.parse_args()


def split_ref(data_dir: Path | None, split_csv: str) -> str:
    if split_csv.startswith(("http://", "https://")):
        return split_csv
    path = Path(split_csv)
    if path.is_absolute() or path.exists():
        return str(path)
    if data_dir:
        return str(data_dir / split_csv)
    return urljoin(DEFAULT_BASE_URL, split_csv)


def read_split_rows(ref: str) -> list[dict[str, str]]:
    if ref.startswith(("http://", "https://")):
        with urlopen(ref, timeout=60) as response:
            lines = [line.decode("utf-8") for line in response]
    else:
        lines = Path(ref).read_text().splitlines()
    return list(csv.DictReader(lines))


def png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(payload, checksum)
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", checksum & 0xFFFFFFFF)


def grayscale_png(width: int, height: int, value: int) -> bytes:
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid PNG size: {width}x{height}")
    if not 0 <= value <= 255:
        raise ValueError(f"PNG grayscale value must be 0..255, got {value}")

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    scanline = bytes([0]) + bytes([value]) * width
    raw = scanline * height
    return signature + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(raw, level=9)) + png_chunk(b"IEND", b"")


def main() -> None:
    args = parse_args()
    if not 0 <= args.class_id <= 4:
        raise SystemExit("--class-id must be in the confirmed AgriPotential range 0..4")

    ref = split_ref(args.data_dir, args.split_csv)
    rows = read_split_rows(ref)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        raise SystemExit(f"no rows found in split CSV: {ref}")

    first = rows[0]
    if args.patch_id_column not in first:
        raise SystemExit(f"split CSV is missing patch id column: {args.patch_id_column}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for row in rows:
            patch_id = row[args.patch_id_column].strip()
            if not patch_id:
                raise SystemExit("encountered blank patch_id")
            patch_size_text = row.get(args.patch_size_column, "").strip()
            patch_size = int(patch_size_text) if patch_size_text else args.default_patch_size
            zf.writestr(f"{patch_id}.png", grayscale_png(patch_size, patch_size, args.class_id))

    print(f"Wrote {args.out} with {len(rows)} PNG mask(s) from {ref}")


if __name__ == "__main__":
    main()
