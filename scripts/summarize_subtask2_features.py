#!/usr/bin/env python3
"""Summarize cached DACIA5 Subtask 2 manifest/features for review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/subtask2/manifest.csv"))
    parser.add_argument("--features", type=Path, default=Path("results/subtask2/features/subtask2_features.csv"))
    parser.add_argument("--out", type=Path, default=Path("results/subtask2/inspection/subtask2_feature_summary.json"))
    return parser.parse_args()


def value_counts(frame, columns: list[str]) -> dict[str, int]:
    if frame.empty:
        return {}
    counts = frame.groupby(columns, dropna=False).size()
    return {"/".join(str(part) for part in key if str(part) != "nan"): int(value) for key, value in counts.items()}


def numeric_range(frame, column: str) -> dict[str, object]:
    values = frame[column].dropna()
    if values.empty:
        return {"min": None, "max": None, "unique": []}
    return {
        "min": int(values.min()),
        "max": int(values.max()),
        "unique": [int(value) for value in sorted(values.unique())[:30]],
    }


def main() -> None:
    import pandas as pd

    args = parse_args()
    manifest = pd.read_csv(args.manifest)
    features = pd.read_csv(args.features)
    feature_columns = [column for column in features.columns if column.startswith("b")]
    mean_columns = [column for column in feature_columns if column.endswith("_mean")]
    errors = features["feature_error"].fillna("").astype(str) != ""

    summary: dict[str, object] = {
        "manifest": {
            "path": str(args.manifest),
            "rows": int(len(manifest)),
            "problem_split_label_status": value_counts(manifest, ["problem", "split", "label_status"]),
            "year_range": numeric_range(manifest, "year"),
            "month_range": numeric_range(manifest, "month"),
            "candidate_label_counts": {
                str(key): int(value)
                for key, value in manifest["label_candidate"].value_counts(dropna=False).sort_index().items()
            },
            "parse_failures": int((manifest["filename_parse_ok"].astype(str) != "1").sum()),
        },
        "features": {
            "path": str(args.features),
            "rows": int(len(features)),
            "columns": int(len(features.columns)),
            "feature_columns": int(len(feature_columns)),
            "band_mean_columns": int(len(mean_columns)),
            "feature_errors": int(errors.sum()),
            "problem_split_shape_status": value_counts(features, ["problem", "split", "array_shape", "label_status"]),
        },
        "notes": [
            "label_candidate is parsed from the final filename token and is only a patch index.",
            "Training labels are derived from the APIA crop-code token using the included Legend_crops.pdf mapping.",
            "Band-derived vegetation indices remain blocked until Sentinel-2 band order is confirmed.",
        ],
    }

    if mean_columns:
        stats = features[mean_columns].describe().T[["mean", "std", "min", "max"]]
        summary["features"]["band_mean_stats"] = {
            column: {key: float(value) for key, value in row.items()} for column, row in stats.iterrows()
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
