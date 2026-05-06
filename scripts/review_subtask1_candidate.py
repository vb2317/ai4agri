#!/usr/bin/env python3
"""Review a Subtask 1 vision run before CodaBench submission."""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
import sys
import zipfile
import zlib
from collections import Counter
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_submission_zip import iter_png_ints, prediction_file_names, root_file_names, unfilter_scanlines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Vision run id under results/subtask1/vision_runs.")
    parser.add_argument("--out-root", type=Path, default=Path("results/subtask1"))
    parser.add_argument("--data-dir", type=Path, default=Path("data/subtask1"))
    parser.add_argument("--zip-path", type=Path, default=None, help="Candidate ZIP; defaults to submissions/<run-id>.zip.")
    parser.add_argument("--expected-ids-file", type=Path, default=None, help="Defaults to <data-dir>/test.csv when present.")
    parser.add_argument("--min-visuals", type=int, default=1, help="Minimum visuals required for each review prefix.")
    parser.add_argument("--min-class", type=int, default=1, help="Minimum raw submission class id.")
    parser.add_argument("--max-class", type=int, default=5, help="Maximum raw submission class id.")
    parser.add_argument("--allow-missing-extremes", action="store_true", help="Warn instead of failing if min or max class is absent.")
    parser.add_argument("--max-flat-fraction", type=float, default=0.10, help="Fail if more than this fraction of PNG masks contain one class.")
    parser.add_argument("--report-json", type=Path, default=None, help="Optional path for machine-readable audit output.")
    return parser.parse_args()


def load_json(path: Path) -> Optional[dict[str, object]]:
    if not path.exists():
        return None
    with path.open() as handle:
        return json.load(handle)


def count_visuals(visual_dir: Path) -> dict[str, int]:
    return {
        "train_sample": len(list(visual_dir.glob("train_sample_*.png"))),
        "val_pred": len(list(visual_dir.glob("val_pred_*.png"))),
        "test_pred": len(list(visual_dir.glob("test_pred_*.png"))),
    }


def validate_zip(zip_path: Path, expected_ids_file: Path | None, min_class: int, max_class: int) -> tuple[int, str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "validate_submission_zip.py"),
        "--zip-path",
        str(zip_path),
        "--subtask1-codabench",
        "--check-class-values",
        "--min-class",
        str(min_class),
        "--max-class",
        str(max_class),
    ]
    if expected_ids_file and expected_ids_file.exists():
        command.extend(["--expected-ids-file", str(expected_ids_file)])
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode, output


def zip_class_presence(zip_path: Path) -> tuple[Counter[int], int]:
    class_presence: Counter[int] = Counter()
    prediction_count = 0
    with zipfile.ZipFile(zip_path) as zf:
        names = prediction_file_names(root_file_names(zf))
        for name in names:
            if Path(name).suffix.lower() != ".png":
                continue
            prediction_count += 1
            values = set(iter_png_ints(zf.read(name)))
            for value in values:
                class_presence[int(value)] += 1
    return class_presence, prediction_count


def iter_png_pixels(payload: bytes) -> list[int]:
    try:
        from PIL import Image
        import numpy as np
        from io import BytesIO

        with Image.open(BytesIO(payload)) as image:
            return [int(value) for value in np.asarray(image).reshape(-1)]
    except ImportError:
        return [int(value) for value in grayscale_png_pixels(payload)]


def grayscale_png_pixels(payload: bytes) -> bytes:
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
        raise ValueError("Pillow and numpy are required for non-8-bit-grayscale PNG pixel summaries")

    raw = zlib.decompress(b"".join(idat_parts))
    return unfilter_scanlines(raw, width, height)


def zip_pixel_summary(zip_path: Path) -> dict[str, object]:
    pixel_counts: Counter[int] = Counter()
    unique_counts: Counter[int] = Counter()
    flat_examples: list[str] = []
    prediction_count = 0
    with zipfile.ZipFile(zip_path) as zf:
        names = prediction_file_names(root_file_names(zf))
        for name in names:
            if Path(name).suffix.lower() != ".png":
                continue
            prediction_count += 1
            pixels = iter_png_pixels(zf.read(name))
            values = Counter(pixels)
            unique_counts[len(values)] += 1
            if len(values) == 1 and len(flat_examples) < 20:
                flat_examples.append(f"{name}:{next(iter(values))}")
            pixel_counts.update(values)

    total_pixels = sum(pixel_counts.values())
    fractions = {
        str(value): (count / total_pixels if total_pixels else 0.0)
        for value, count in sorted(pixel_counts.items())
    }
    return {
        "pixel_counts": dict(sorted(pixel_counts.items())),
        "pixel_fractions": fractions,
        "unique_classes_per_png": dict(sorted(unique_counts.items())),
        "flat_png_count": unique_counts.get(1, 0),
        "flat_png_fraction": unique_counts.get(1, 0) / prediction_count if prediction_count else 0.0,
        "flat_png_examples": flat_examples,
    }


def add_check(checks: list[dict[str, object]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": ok, "detail": detail})


def main() -> None:
    args = parse_args()
    run_dir = args.out_root / "vision_runs" / args.run_id
    visual_dir = args.out_root / "visuals" / args.run_id
    val_probs = args.out_root / "val_preds" / f"{args.run_id}_val_probs.npz"
    zip_path = args.zip_path or (args.out_root / "submissions" / f"{args.run_id}.zip")
    expected_ids_file = args.expected_ids_file or (args.data_dir / "test.csv")

    checks: list[dict[str, object]] = []
    metrics = load_json(run_dir / "metrics.json")
    config = load_json(run_dir / "config.json")

    add_check(checks, "run_dir", run_dir.exists(), str(run_dir))
    add_check(checks, "config_json", config is not None, str(run_dir / "config.json"))
    add_check(checks, "metrics_json", metrics is not None, str(run_dir / "metrics.json"))
    add_check(checks, "best_checkpoint", (run_dir / "best.pt").exists(), str(run_dir / "best.pt"))
    add_check(checks, "train_log", (run_dir / "train.log").exists(), str(run_dir / "train.log"))
    add_check(checks, "val_probs", val_probs.exists(), str(val_probs))

    visual_counts = count_visuals(visual_dir)
    for prefix, count in visual_counts.items():
        add_check(checks, f"visuals_{prefix}", count >= args.min_visuals, f"{count} file(s) in {visual_dir}")

    zip_validation_output = ""
    class_presence: Counter[int] = Counter()
    prediction_count = 0
    pixel_summary: dict[str, object] = {}
    if zip_path.exists():
        returncode, zip_validation_output = validate_zip(zip_path, expected_ids_file, args.min_class, args.max_class)
        add_check(checks, "zip_validation", returncode == 0, zip_validation_output)
        class_presence, prediction_count = zip_class_presence(zip_path)
        present_classes = sorted(class_presence)
        add_check(checks, "zip_not_collapsed", len(present_classes) >= 2, f"classes present: {present_classes}")
        extremes_ok = args.min_class in class_presence and args.max_class in class_presence
        add_check(
            checks,
            "zip_extreme_classes",
            extremes_ok or args.allow_missing_extremes,
            f"class presence by PNG: {dict(sorted(class_presence.items()))}",
        )
        pixel_summary = zip_pixel_summary(zip_path)
        pixel_counts = pixel_summary["pixel_counts"]
        expected_classes = set(range(args.min_class, args.max_class + 1))
        actual_classes = set(pixel_counts)
        out_of_range = actual_classes - expected_classes
        add_check(
            checks,
            "zip_pixel_classes",
            len(out_of_range) == 0,
            f"pixel counts: {pixel_counts}" + (f"; OUT OF RANGE values: {sorted(out_of_range)}" if out_of_range else ""),
        )
        flat_fraction = float(pixel_summary["flat_png_fraction"])
        add_check(
            checks,
            "zip_flat_png_fraction",
            flat_fraction <= args.max_flat_fraction,
            f"{pixel_summary['flat_png_count']} flat PNG(s), fraction {flat_fraction:.4f}",
        )
    else:
        add_check(checks, "candidate_zip", False, str(zip_path))

    summary = {
        "run_id": args.run_id,
        "run_dir": str(run_dir),
        "visual_dir": str(visual_dir),
        "zip_path": str(zip_path),
        "metrics": metrics,
        "config": config,
        "visual_counts": visual_counts,
        "prediction_count": prediction_count,
        "class_presence_by_png": dict(sorted(class_presence.items())),
        "pixel_summary": pixel_summary,
        "zip_validation_output": zip_validation_output,
        "checks": checks,
        "ok": all(bool(check["ok"]) for check in checks),
    }

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))
    if not summary["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
