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
# # AI4Agri Subtask 1 Test Bed
#
# Exploratory notebook for AgriPotential metadata, sample geometry, and visual sanity checks. Use scripts for pipeline execution; keep this notebook for investigation and presentation-ready evidence.

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

DATA_DIR = REPO_ROOT / "data" / "subtask1"
RESULTS_DIR = REPO_ROOT / "results" / "subtask1"
INSPECTION_PATH = RESULTS_DIR / "inspection" / "subtask1_inspection.json"

plt.rcParams["figure.figsize"] = (9, 5)


# %% [markdown]
# ## Question
#
# What does the Subtask 1 metadata reveal about patch layout, split sizes, and readiness for raster smoke reads?

# %%
from scripts.inspect_subtask1 import read_csv_rows

metadata = pd.DataFrame(read_csv_rows(None, "metadata.csv"))
splits = {name: pd.DataFrame(read_csv_rows(None, f"{name}.csv")) for name in ["train", "val", "test"]}

{
    "metadata_rows": len(metadata),
    "metadata_columns": list(metadata.columns),
    "split_rows": {name: len(frame) for name, frame in splits.items()},
}


# %%
display(metadata.head())
display(splits["train"].head())


# %% [markdown]
# ## Patch Geometry
#
# This plots where each split samples the source raster. It is a quick way to spot obvious split or coordinate issues before model work.

# %%
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharex=True, sharey=True)
for ax, (name, frame) in zip(axes, splits.items()):
    plot_frame = frame.assign(row=lambda x: x["row"].astype(int), col=lambda x: x["col"].astype(int))
    ax.scatter(plot_frame["col"], plot_frame["row"], s=3, alpha=0.35)
    ax.set_title(f"{name}: {len(plot_frame)} patches")
    ax.set_xlabel("col")
    ax.invert_yaxis()
axes[0].set_ylabel("row")
fig.tight_layout()


# %%
patch_summary = []
for split, frame in splits.items():
    numeric = frame[["patch_size", "n_annotated", "row", "col"]].astype(int)
    patch_summary.append(
        {
            "split": split,
            "rows": len(frame),
            "patch_size_values": sorted(numeric["patch_size"].unique().tolist()),
            "annotated_min": int(numeric["n_annotated"].min()) if "n_annotated" in numeric else None,
            "annotated_median": float(numeric["n_annotated"].median()) if "n_annotated" in numeric else None,
            "annotated_max": int(numeric["n_annotated"].max()) if "n_annotated" in numeric else None,
        }
    )
pd.DataFrame(patch_summary)


# %% [markdown]
# ## Existing Inspection Artifact
#
# Load the script-produced JSON if it exists. This notebook does not create it; run `scripts/inspect_subtask1.py` separately when the artifact needs refreshing.

# %%
if INSPECTION_PATH.exists():
    inspection = json.loads(INSPECTION_PATH.read_text())
    display(
        {
            "source": inspection.get("source"),
            "label_name": inspection.get("label_name"),
            "split_rows": {name: details.get("rows") for name, details in inspection.get("splits", {}).items()},
        }
    )
else:
    print(f"Inspection artifact not found: {INSPECTION_PATH}")


# %% [markdown]
# ## Raster Smoke View
#
# When Subtask 1 rasters exist locally or on RunPod, use this cell to inspect one small window manually. It stays disabled until `SAMPLE_RASTER` points at a real file.

# %%
SAMPLE_RASTER = None

if SAMPLE_RASTER:
    import rasterio
    from rasterio.windows import Window

    sample = splits["train"].iloc[0]
    with rasterio.open(SAMPLE_RASTER) as src:
        window = Window(int(sample["col"]), int(sample["row"]), int(sample["patch_size"]), int(sample["patch_size"]))
        arr = src.read(1, window=window)
    plt.imshow(arr, cmap="viridis")
    plt.title(Path(SAMPLE_RASTER).name)
    plt.colorbar()
else:
    print("Set SAMPLE_RASTER to a local GeoTIFF path for a manual smoke view.")
