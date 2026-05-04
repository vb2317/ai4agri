#!/usr/bin/env python3
"""Validate a candidate AI4Agri submission ZIP.

Subtask 1 CodaBench submissions are root-level PNG masks named after test
``patch_id`` values, with integer class ids 0..4. An optional ``report.pdf`` is
accepted.
"""

from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
import zipfile
import zlib
from io import BytesIO
from pathlib import Path
from typing import Iterable


DEFAULT_IGNORED_PREFIXES = ("__MACOSX/",)
DEFAULT_IGNORED_NAMES = (".DS_Store",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip-path", required=True, type=Path, help="Submission ZIP to validate.")
    parser.add_argument(
        "--subtask1-codabench",
        action="store_true",
        help="Apply confirmed AgriPotential CodaBench rules: root PNGs named by patch_id, optional report.pdf.",
    )
    parser.add_argument(
        "--expected-file",
        action="append",
        default=[],
        help="Required root-level file name. Repeat for multiple files.",
    )
    parser.add_argument(
        "--allowed-ext",
        action="append",
        default=[],
        help="Allowed root-level extension such as .csv, .txt, or .npy. Repeat for multiple extensions.",
    )
    parser.add_argument("--min-class", type=int, default=0, help="Minimum allowed class id.")
    parser.add_argument("--max-class", type=int, default=4, help="Maximum allowed class id.")
    parser.add_argument(
        "--expected-count",
        type=int,
        default=None,
        help="Expected number of prediction files. For Subtask 1 this is 800 PNGs.",
    )
    parser.add_argument(
        "--expected-ids-file",
        type=Path,
        default=None,
        help="CSV containing expected patch_id values; use with Subtask 1 test.csv.",
    )
    parser.add_argument(
        "--check-class-values",
        action="store_true",
        help="Parse supported files/images and verify integer classes are within [min-class, max-class].",
    )
    return parser.parse_args()


def root_file_names(zf: zipfile.ZipFile) -> list[str]:
    names: list[str] = []
    for info in zf.infolist():
        name = info.filename
        if info.is_dir():
            continue
        if name.startswith(DEFAULT_IGNORED_PREFIXES):
            continue
        if Path(name).name in DEFAULT_IGNORED_NAMES:
            continue
        names.append(name)
    return names


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_root_layout(names: Iterable[str]) -> None:
    nested = [name for name in names if "/" in name.strip("/")]
    if nested:
        fail("all submission files must be at ZIP root; nested files found: " + ", ".join(nested[:10]))


def validate_expected_files(names: set[str], expected_files: list[str]) -> None:
    missing = sorted(set(expected_files) - names)
    if missing:
        fail("missing expected root-level files: " + ", ".join(missing))


def validate_allowed_extensions(names: Iterable[str], allowed_exts: list[str]) -> None:
    if not allowed_exts:
        return
    normalized = {ext if ext.startswith(".") else f".{ext}" for ext in allowed_exts}
    bad = [name for name in names if Path(name).suffix not in normalized]
    if bad:
        fail("files with disallowed extensions found: " + ", ".join(bad[:10]))


def prediction_file_names(names: Iterable[str]) -> list[str]:
    return [name for name in names if Path(name).name != "report.pdf"]


def validate_subtask1_codabench(names: list[str], expected_count: int | None) -> None:
    bad = []
    for name in names:
        path = Path(name)
        if path.name == "report.pdf":
            continue
        if path.suffix.lower() != ".png":
            bad.append(name)
    if bad:
        fail("Subtask 1 CodaBench ZIP may contain only PNG predictions and optional report.pdf: " + ", ".join(bad[:10]))

    predictions = prediction_file_names(names)
    if expected_count is not None and len(predictions) != expected_count:
        print(f"WARN: expected {expected_count} PNG predictions, found {len(predictions)}.")


def read_expected_ids(path: Path) -> set[str]:
    if not path.exists():
        fail(f"expected ids file does not exist: {path}")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "patch_id" not in reader.fieldnames:
            fail(f"expected ids file must be a CSV with a patch_id column: {path}")
        return {row["patch_id"].strip() for row in reader if row.get("patch_id", "").strip()}


def validate_expected_ids(names: Iterable[str], expected_ids_file: Path) -> None:
    expected_ids = read_expected_ids(expected_ids_file)
    found_ids = {Path(name).stem for name in prediction_file_names(names) if Path(name).suffix.lower() == ".png"}
    missing = sorted(expected_ids - found_ids)
    extra = sorted(found_ids - expected_ids)
    if missing:
        fail("missing PNG predictions for patch_id values: " + ", ".join(missing[:10]))
    if extra:
        fail("PNG predictions not present in expected patch_id list: " + ", ".join(extra[:10]))


def iter_csv_ints(payload: str) -> Iterable[int]:
    reader = csv.reader(payload.splitlines())
    for row in reader:
        for cell in row:
            value = cell.strip()
            if not value:
                continue
            try:
                yield int(value)
            except ValueError:
                continue


def iter_text_ints(payload: str) -> Iterable[int]:
    for token in payload.replace(",", " ").split():
        try:
            yield int(token)
        except ValueError:
            continue


def iter_json_ints(payload: str) -> Iterable[int]:
    def walk(obj: object) -> Iterable[int]:
        if isinstance(obj, bool):
            return
        if isinstance(obj, int):
            yield obj
            return
        if isinstance(obj, list):
            for item in obj:
                yield from walk(item)
            return
        if isinstance(obj, dict):
            for item in obj.values():
                yield from walk(item)

    yield from walk(json.loads(payload))


def iter_png_ints(payload: bytes) -> Iterable[int]:
    try:
        from PIL import Image
    except ImportError:
        yield from iter_grayscale_png_ints(payload)
        return

    try:
        import numpy as np
    except ImportError:
        yield from iter_grayscale_png_ints(payload)
        return

    with Image.open(BytesIO(payload)) as image:
        array = np.asarray(image)
    for value in np.unique(array):
        yield int(value)


def paeth_predictor(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def unfilter_scanlines(raw: bytes, width: int, height: int) -> bytes:
    stride = width
    rows = []
    offset = 0
    previous = bytes(stride)
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        current = bytearray(raw[offset : offset + stride])
        offset += stride
        for index, value in enumerate(current):
            left = current[index - 1] if index > 0 else 0
            above = previous[index]
            upper_left = previous[index - 1] if index > 0 else 0
            if filter_type == 0:
                reconstructed = value
            elif filter_type == 1:
                reconstructed = value + left
            elif filter_type == 2:
                reconstructed = value + above
            elif filter_type == 3:
                reconstructed = value + ((left + above) // 2)
            elif filter_type == 4:
                reconstructed = value + paeth_predictor(left, above, upper_left)
            else:
                raise ValueError(f"unsupported PNG filter type: {filter_type}")
            current[index] = reconstructed & 0xFF
        rows.append(bytes(current))
        previous = rows[-1]
    return b"".join(rows)


def iter_grayscale_png_ints(payload: bytes) -> Iterable[int]:
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("invalid PNG signature")

    offset = 8
    width = height = bit_depth = color_type = interlace = None
    idat_parts: list[bytes] = []
    while offset < len(payload):
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        offset += 4
        chunk_type = payload[offset : offset + 4]
        offset += 4
        chunk_payload = payload[offset : offset + length]
        offset += length + 4
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk_payload)
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_payload)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or bit_depth is None or color_type is None or interlace is None:
        raise ValueError("PNG missing IHDR")
    if bit_depth != 8 or color_type != 0 or interlace != 0:
        raise ValueError("Pillow or numpy is required for non-8-bit-grayscale PNG checks")

    raw = zlib.decompress(b"".join(idat_parts))
    for value in sorted(set(unfilter_scanlines(raw, width, height))):
        yield int(value)


def validate_class_values(zf: zipfile.ZipFile, names: Iterable[str], min_class: int, max_class: int) -> None:
    checked_files = 0
    checked_values = 0
    bad_values: list[tuple[str, int]] = []

    for name in names:
        suffix = Path(name).suffix.lower()
        if suffix not in {".csv", ".txt", ".json", ".png"}:
            continue

        raw_payload = zf.read(name)
        if suffix == ".csv":
            payload = raw_payload.decode("utf-8")
            values = iter_csv_ints(payload)
        elif suffix == ".json":
            payload = raw_payload.decode("utf-8")
            values = iter_json_ints(payload)
        elif suffix == ".png":
            values = iter_png_ints(raw_payload)
        else:
            payload = raw_payload.decode("utf-8")
            values = iter_text_ints(payload)

        file_value_count = 0
        for value in values:
            file_value_count += 1
            checked_values += 1
            if value < min_class or value > max_class:
                bad_values.append((name, value))
                if len(bad_values) >= 10:
                    break
        if file_value_count:
            checked_files += 1

    if bad_values:
        details = ", ".join(f"{name}:{value}" for name, value in bad_values)
        fail(f"class values outside [{min_class}, {max_class}]: {details}")

    if checked_files == 0:
        print("WARN: no supported text/CSV/JSON prediction files were parsed for class values.")
    else:
        print(f"Checked {checked_values} class-like integer values across {checked_files} files.")


def main() -> None:
    args = parse_args()
    if not args.zip_path.exists():
        fail(f"ZIP does not exist: {args.zip_path}")
    if not zipfile.is_zipfile(args.zip_path):
        fail(f"not a valid ZIP file: {args.zip_path}")

    with zipfile.ZipFile(args.zip_path) as zf:
        names = root_file_names(zf)
        if not names:
            fail("ZIP contains no submission files.")

        validate_root_layout(names)
        validate_expected_files(set(names), args.expected_file)
        validate_allowed_extensions(names, args.allowed_ext)
        if args.subtask1_codabench:
            validate_subtask1_codabench(names, args.expected_count if args.expected_count is not None else 800)
        if args.expected_ids_file:
            validate_expected_ids(names, args.expected_ids_file)

        if args.check_class_values:
            validate_class_values(zf, names, args.min_class, args.max_class)

    print(f"OK: {args.zip_path} contains {len(names)} root-level submission file(s).")


if __name__ == "__main__":
    main()
