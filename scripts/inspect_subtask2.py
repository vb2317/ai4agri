#!/usr/bin/env python3
"""Inspect DACIA5 directory/file layout for AI4Agri Subtask 2."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


PROBLEM1_LABELS = {
    0: "Wheat",
    1: "Corn",
    2: "Peas",
    3: "Rapeseed",
    4: "Potato",
    5: "Sugarbeet",
    6: "Alfalfa",
}
PROBLEM2_LABELS = {
    0: "Winter Wheat",
    1: "Alfalfa",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path, help="Extracted DACIA5 dataset root.")
    parser.add_argument("--out-dir", type=Path, default=Path("results/subtask2/inspection"))
    parser.add_argument("--limit", type=int, default=5, help="Number of example files to keep per group.")
    parser.add_argument(
        "--read-arrays",
        action="store_true",
        help="Read up to --limit TIFF arrays per challenge/split/format group when rasterio is available.",
    )
    return parser.parse_args()


def infer_year(text: str) -> str | None:
    match = re.search(r"20[0-2][0-9]", text)
    return match.group(0) if match else None


def infer_problem(parts: tuple[str, ...]) -> str | None:
    lowered = [part.lower() for part in parts]
    if "problem1" in lowered:
        return "problem1"
    if "problem2" in lowered:
        return "problem2"
    return None


def infer_split(parts: tuple[str, ...]) -> str | None:
    lowered = [part.lower() for part in parts]
    if "training" in lowered or "train" in lowered:
        return "training"
    if "test" in lowered or "testing" in lowered:
        return "test"
    return None


def infer_format(parts: tuple[str, ...], suffix: str) -> str:
    lowered = [part.lower() for part in parts]
    if any("mat" in part for part in lowered) or suffix == ".mat":
        return "mat"
    if any("tiff" in part or "geotiff" in part for part in lowered) or suffix in {".tif", ".tiff"}:
        return "tiff"
    if suffix == ".png":
        return "png"
    return suffix.lstrip(".") or "unknown"


def read_tiff_shape(path: Path) -> dict[str, object]:
    import rasterio

    with rasterio.open(path) as src:
        return {
            "shape": [src.count, src.height, src.width],
            "dtype": src.dtypes[0] if src.dtypes else None,
            "crs": str(src.crs) if src.crs else None,
        }


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    files = [path for path in args.data_dir.rglob("*") if path.is_file()]
    suffix_counts = Counter(path.suffix.lower() or "<none>" for path in files)
    top_dirs = Counter(path.relative_to(args.data_dir).parts[0] for path in files if path.relative_to(args.data_dir).parts)

    groups: dict[str, dict[str, object]] = defaultdict(lambda: {"count": 0, "examples": []})
    years = Counter()
    array_reads: list[dict[str, object]] = []

    for path in files:
        rel = path.relative_to(args.data_dir)
        parts = rel.parts
        problem = infer_problem(parts) or "unknown_problem"
        split = infer_split(parts) or "unknown_split"
        fmt = infer_format(parts, path.suffix.lower())
        year = infer_year(str(rel))
        if year:
            years[year] += 1
        key = f"{problem}/{split}/{fmt}"
        groups[key]["count"] += 1
        if len(groups[key]["examples"]) < args.limit:
            groups[key]["examples"].append(str(rel))

    if args.read_arrays:
        read_counts: Counter[str] = Counter()
        for path in files:
            rel = path.relative_to(args.data_dir)
            parts = rel.parts
            problem = infer_problem(parts) or "unknown_problem"
            split = infer_split(parts) or "unknown_split"
            fmt = infer_format(parts, path.suffix.lower())
            key = f"{problem}/{split}/{fmt}"
            if fmt != "tiff" or read_counts[key] >= args.limit:
                continue
            try:
                details = read_tiff_shape(path)
            except Exception as exc:
                details = {"error": str(exc)}
            details["file"] = str(rel)
            details["group"] = key
            array_reads.append(details)
            read_counts[key] += 1

    report = {
        "source": str(args.data_dir),
        "total_files": len(files),
        "top_level_dirs": dict(sorted(top_dirs.items())),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "years_seen_in_paths": dict(sorted(years.items())),
        "problem1_labels": PROBLEM1_LABELS,
        "problem2_labels": PROBLEM2_LABELS,
        "groups": dict(sorted(groups.items())),
        "array_reads": array_reads,
        "notes": [
            "Problem 1 challenge: train on 2020-2023 and test on 2024.",
            "Problem 2 ImageCLEF 2026 challenge: March-only winter wheat vs alfalfa.",
            "Zenodo v1 text describes Sentinel-2 32x32x12 patches; inspect actual extracted files for naming details.",
        ],
    }

    out_path = args.out_dir / "subtask2_inspection.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
