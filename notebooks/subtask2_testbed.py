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
# # AI4Agri Subtask 2 Test Bed
#
# Exploratory notebook for DACIA5 inspection artifacts, manifest/features review, and small patch visualizations. Use scripts for manifest creation, feature extraction, training, and submission packaging.

# %%
from pathlib import Path
import json
import sys

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path.cwd()
if not (REPO_ROOT / "scripts").exists():
    raise RuntimeError("Run this notebook from the ai4agri repository root")
sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "data" / "subtask2"
RESULTS_DIR = REPO_ROOT / "results" / "subtask2"
INSPECTION_PATH = RESULTS_DIR / "inspection" / "subtask2_inspection.json"
MANIFEST_PATH = RESULTS_DIR / "manifest.csv"
FEATURES_PATH = RESULTS_DIR / "features" / "subtask2_features.csv"

plt.rcParams["figure.figsize"] = (9, 5)


# %% [markdown]
# ## Question
#
# What does the extracted DACIA5 dataset look like, and do the cached artifacts make sense before training?

# %%
if INSPECTION_PATH.exists():
    inspection = json.loads(INSPECTION_PATH.read_text())
    display(
        {
            "total_files": inspection.get("total_files"),
            "suffix_counts": inspection.get("suffix_counts"),
            "years_seen": inspection.get("years_seen_in_paths"),
        }
    )
else:
    inspection = {}
    print(f"Inspection artifact not found: {INSPECTION_PATH}")


# %%
if inspection:
    groups = pd.DataFrame(
        [
            {"group": name, "count": details.get("count", 0)}
            for name, details in inspection.get("groups", {}).items()
        ]
    ).sort_values("count", ascending=False)
    display(groups)
    groups.head(12).plot.barh(x="group", y="count", legend=False)
    plt.title("Top DACIA5 file groups")
    plt.xlabel("files")
    plt.gca().invert_yaxis()


# %% [markdown]
# ## Manifest Review
#
# The manifest is produced by `scripts/subtask2_baseline.py manifest`. This notebook only reviews it.

# %%
if MANIFEST_PATH.exists():
    manifest = pd.read_csv(MANIFEST_PATH)
    display(manifest.head())
    display(manifest.groupby(["problem", "split", "label_status"]).size().to_frame("rows"))
else:
    manifest = pd.DataFrame()
    print(f"Manifest not found: {MANIFEST_PATH}")


# %%
if not manifest.empty:
    date_counts = (
        manifest.assign(date=pd.to_datetime(manifest["date"].astype(str), errors="coerce"))
        .dropna(subset=["date"])
        .groupby(["problem", "split", pd.Grouper(key="date", freq="ME")])
        .size()
        .reset_index(name="rows")
    )
    for (problem, split), frame in date_counts.groupby(["problem", "split"]):
        plt.plot(frame["date"], frame["rows"], marker="o", label=f"{problem}/{split}")
    plt.title("Patch counts by month")
    plt.ylabel("patches")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()


# %% [markdown]
# ## Feature Review
#
# The feature table is produced by `scripts/subtask2_baseline.py features`. Use this section to inspect missing values, feature scales, and obvious extraction failures.

# %%
if FEATURES_PATH.exists():
    features = pd.read_csv(FEATURES_PATH)
    print(features.shape)
    display(features[["problem", "split", "array_shape", "label_status", "feature_error"]].head())
    display(features.groupby(["problem", "split", "array_shape"]).size().to_frame("rows"))
else:
    features = pd.DataFrame()
    print(f"Feature table not found: {FEATURES_PATH}")


# %%
if not features.empty:
    feature_cols = [col for col in features.columns if col.startswith("b") and col.endswith("_mean")]
    display(features[feature_cols].describe().T.head(12))
    features[feature_cols[:6]].hist(figsize=(12, 8), bins=40)
    plt.suptitle("First six band mean distributions")
    plt.tight_layout()


# %% [markdown]
# ## Patch Visualization
#
# Load one patch TIFF directly when data is available. This is for visual sanity checks only.

# %%
if not manifest.empty and DATA_DIR.exists():
    import rasterio

    sample_path = Path(manifest.iloc[0]["path"])
    with rasterio.open(sample_path) as src:
        patch = src.read()
    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    for band_index, ax in enumerate(axes.ravel(), start=1):
        if band_index <= patch.shape[0]:
            ax.imshow(patch[band_index - 1], cmap="viridis")
            ax.set_title(f"band {band_index}")
        ax.axis("off")
    fig.suptitle(sample_path.name)
    fig.tight_layout()
else:
    print("Patch visualization waits for both data/subtask2 and a manifest artifact.")
