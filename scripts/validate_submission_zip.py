#!/usr/bin/env python3
"""Validate a candidate AI4Agri submission ZIP.

The exact CodaBench file names still need to be confirmed from the logged-in
competition page. This checker therefore validates the invariants we know are
safe now and supports stricter options once filenames are confirmed.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import zipfile
from pathlib import Path
from typing import Iterable


DEFAULT_IGNORED_PREFIXES = ("__MACOSX/",)
DEFAULT_IGNORED_NAMES = (".DS_Store",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip-path", required=True, type=Path, help="Submission ZIP to validate.")
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
        "--check-class-values",
        action="store_true",
        help="Parse supported files and verify integer classes are within [min-class, max-class].",
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


def validate_class_values(zf: zipfile.ZipFile, names: Iterable[str], min_class: int, max_class: int) -> None:
    checked_files = 0
    checked_values = 0
    bad_values: list[tuple[str, int]] = []

    for name in names:
        suffix = Path(name).suffix.lower()
        if suffix not in {".csv", ".txt", ".json"}:
            continue

        payload = zf.read(name).decode("utf-8")
        if suffix == ".csv":
            values = iter_csv_ints(payload)
        elif suffix == ".json":
            values = iter_json_ints(payload)
        else:
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

        if args.check_class_values:
            validate_class_values(zf, names, args.min_class, args.max_class)

    print(f"OK: {args.zip_path} contains {len(names)} root-level submission file(s).")


if __name__ == "__main__":
    main()
