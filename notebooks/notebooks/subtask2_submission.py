# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # AI4Agri 2026 Subtask 2 Submission Notebook
#
# This notebook reviews the tracked DACIA5 inspection and baseline artifacts. Operational steps are implemented in `scripts/`; this notebook is intentionally lightweight so it can be submitted or adapted for Colab without requiring raw data in the repository.

# %%
from pathlib import Path
import json

REPO_ROOT = Path.cwd()
INSPECTION_DIR = REPO_ROOT / "results" / "subtask2" / "inspection"
BASELINE_SUMMARY_PATH = INSPECTION_DIR / "subtask2_baseline_summary.json"
FEATURE_SUMMARY_PATH = INSPECTION_DIR / "subtask2_feature_summary.json"
REPORT_PATH = REPO_ROOT / "reports" / "subtask2_technical_report.md"

for path in (BASELINE_SUMMARY_PATH, FEATURE_SUMMARY_PATH, REPORT_PATH):
    print(path, "OK" if path.exists() else "MISSING")

# %% [markdown]
# ## Baseline Results

# %%
baseline = json.loads(BASELINE_SUMMARY_PATH.read_text())
rows = []
for problem, details in baseline["problems"].items():
    for model_name, metrics in details["models"].items():
        rows.append(
            {
                "problem": problem,
                "model": model_name,
                "split_method": details["split_method"],
                "q_score": metrics["q_score"],
                "overall_accuracy": metrics["overall_accuracy"],
                "average_accuracy": metrics["average_accuracy"],
            }
        )

for row in sorted(rows, key=lambda item: (item["problem"], -item["q_score"])):
    print(json.dumps(row, indent=2))

# %% [markdown]
# ## Data And Feature Summary

# %%
feature_summary = json.loads(FEATURE_SUMMARY_PATH.read_text())
manifest_summary = feature_summary["manifest"]
feature_table_summary = feature_summary["features"]

{
    "manifest_rows": manifest_summary["rows"],
    "feature_rows": feature_table_summary["rows"],
    "feature_columns": feature_table_summary["feature_columns"],
    "feature_errors": feature_table_summary["feature_errors"],
    "years": manifest_summary["year_range"]["unique"],
}

# %% [markdown]
# ## Leakage Controls
#
# - APIA crop code is used only to derive labels from the confirmed legend mapping.
# - APIA code, parcel id, and patch index are excluded from model features.
# - The final filename token is treated as patch index, not as crop label.
# - Unmapped APIA codes are excluded from training.
# - Vegetation indices are intentionally deferred until Sentinel-2 band order is confirmed.

# %% [markdown]
# ## Reproduction Commands
#
# Run these commands from the repository root on a machine with the extracted DACIA5 data:
#
# ```bash
# python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
# python scripts/inspect_subtask2_labels.py --data-dir data/subtask2
# python scripts/subtask2_baseline.py manifest --data-dir data/subtask2 --label-mode apia-code
# python scripts/subtask2_baseline.py features
# python scripts/subtask2_baseline.py label-features
# python scripts/summarize_subtask2_features.py
# python scripts/subtask2_baseline.py train --problem problem1
# python scripts/subtask2_baseline.py train --problem problem2
# ```

# %% [markdown]
# ## Package For Review
#
# ```bash
# python scripts/package_subtask2_submission.py
# ```
#
# Review `results/subtask2/submissions/subtask2_source_bundle.zip` before email submission.
