#!/usr/bin/env python3
"""Inspect DACIA5 label masks and their relationship to patch TIFFs."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


PATCH_RE = re.compile(r"^patch_(?P<date>\d{8})_(?P<parcel_id>\d+)_(?P<patch_index>\d+)\.tif$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path, help="Extracted DACIA5 dataset root.")
    parser.add_argument("--out-dir", type=Path, default=Path("results/subtask2/inspection"))
    parser.add_argument("--sample-limit", type=int, default=20)
    return parser.parse_args()


def image_unique_values(path: Path, max_values: int = 20) -> dict[str, object]:
    import numpy as np
    from PIL import Image

    with Image.open(path) as image:
        array = np.asarray(image)
    flat = array.reshape(-1, array.shape[-1]) if array.ndim == 3 else array.reshape(-1, 1)
    unique, counts = np.unique(flat, axis=0, return_counts=True)
    ordered = sorted(zip(unique.tolist(), counts.tolist()), key=lambda item: item[1], reverse=True)
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "unique_count": int(len(unique)),
        "top_values": [
            {"value": [int(part) for part in value], "count": int(count)}
            for value, count in ordered[:max_values]
        ],
    }


def mat_summary(path: Path) -> dict[str, object]:
    try:
        import numpy as np
        from scipy.io import loadmat
    except Exception as exc:
        return {"error": f"scipy unavailable: {exc}"}

    try:
        data = loadmat(path)
    except Exception as exc:
        return {"error": str(exc)}

    arrays: dict[str, object] = {}
    for key, value in data.items():
        if key.startswith("__") or not hasattr(value, "shape"):
            continue
        unique = np.unique(value)
        arrays[key] = {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "unique_count": int(len(unique)),
            "unique_values": [int(item) for item in unique[:30] if np.isfinite(item)],
        }
    return arrays


def infer_problem(parts: tuple[str, ...]) -> str | None:
    lowered = [part.lower() for part in parts]
    if "problem1" in lowered:
        return "problem1"
    if "problem2" in lowered:
        return "problem2"
    return None


def infer_split(parts: tuple[str, ...]) -> str | None:
    lowered = [part.lower() for part in parts]
    if any(part == "training" or part.startswith("training_") or part == "train" for part in lowered):
        return "training"
    if any(part == "test" or part.startswith("test_") or part == "testing" for part in lowered):
        return "test"
    return None


def patch_mask_path(data_dir: Path, year: str, parcel_id: str, patch_index: str) -> Path:
    return data_dir / "Dataset" / "32x32_patches" / "32x32_RGB_patches" / f"patches_{year}" / f"mask_{year}_{parcel_id}_{patch_index}.png"


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    full_masks: dict[str, object] = {}
    for path in sorted((args.data_dir / "Dataset" / "Masks_and_legend").glob("Sentinel2_*/*")):
        if path.suffix.lower() == ".png" and "Labels_mask" in path.name:
            full_masks[str(path.relative_to(args.data_dir))] = image_unique_values(path)
        elif path.suffix.lower() == ".mat" and "Labels_mask" in path.name:
            full_masks[str(path.relative_to(args.data_dir))] = mat_summary(path)

    patch_rows = []
    match_counts: Counter[tuple[str, str, str]] = Counter()
    examples: list[dict[str, object]] = []
    for path in sorted(args.data_dir.rglob("*.tif")):
        rel = path.relative_to(args.data_dir)
        if "patches_tiff" not in {part.lower() for part in rel.parts}:
            continue
        match = PATCH_RE.match(path.name)
        problem = infer_problem(rel.parts) or "unknown_problem"
        split = infer_split(rel.parts) or "unknown_split"
        if not match:
            match_counts[(problem, split, "unparsed")] += 1
            continue
        year = match.group("date")[:4]
        mask_path = patch_mask_path(args.data_dir, year, match.group("parcel_id"), match.group("patch_index"))
        status = "mask_found" if mask_path.exists() else "mask_missing"
        match_counts[(problem, split, status)] += 1
        if len(examples) < args.sample_limit:
            record: dict[str, object] = {
                "patch": str(rel),
                "problem": problem,
                "split": split,
                "mask": str(mask_path.relative_to(args.data_dir)),
                "status": status,
            }
            if mask_path.exists():
                record["mask_values"] = image_unique_values(mask_path, max_values=10)
            examples.append(record)
        patch_rows.append((problem, split, status))

    report = {
        "source": str(args.data_dir),
        "full_label_masks": full_masks,
        "patch_mask_matches": {"/".join(key): int(value) for key, value in sorted(match_counts.items())},
        "examples": examples,
        "notes": [
            "Patch filenames appear to use the final token as a patch index, not a crop label.",
            "Per-patch RGB mask files may provide class information if their color-to-class mapping is confirmed.",
        ],
    }
    out_path = args.out_dir / "subtask2_label_inspection.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
