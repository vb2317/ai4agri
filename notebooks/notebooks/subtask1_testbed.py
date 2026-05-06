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


# %% [markdown]
# ## Vision Run Review
#
# Scripts write all neural-model artifacts under `results/subtask1/`. Set `RUN_ID` to a U-Net, ResNet/FPN, or TinyViT run and use these cells for the human-in-the-loop gate before any CodaBench submission.

# %%
import numpy as np
from PIL import Image

RUN_ID = ""  # e.g. "20260505T120000Z_unet_summary"
VISION_RUN_DIR = RESULTS_DIR / "vision_runs" / RUN_ID if RUN_ID else None
VISION_VISUAL_DIR = RESULTS_DIR / "visuals" / RUN_ID if RUN_ID else None
VISION_VAL_PROBS = RESULTS_DIR / "val_preds" / f"{RUN_ID}_val_probs.npz" if RUN_ID else None

if RUN_ID and VISION_RUN_DIR and VISION_RUN_DIR.exists():
    config = json.loads((VISION_RUN_DIR / "config.json").read_text())
    metrics = json.loads((VISION_RUN_DIR / "metrics.json").read_text())
    display({"run_id": RUN_ID, "config": config, "metrics": metrics})
else:
    print("Set RUN_ID to an existing vision run to load config and metrics.")


# %% [markdown]
# ## Training Samples
#
# These are exported before augmentation so VB can inspect Sentinel composites and label masks without rerunning training inside the notebook.

# %%
def show_image_grid(paths, title, columns=4, figsize=(16, 10)):
    paths = list(paths)
    if not paths:
        print(f"No images found for {title}.")
        return
    rows = int(np.ceil(len(paths) / columns))
    fig, axes = plt.subplots(rows, columns, figsize=figsize)
    axes = np.atleast_1d(axes).reshape(rows, columns)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, path in zip(axes.ravel(), paths):
        ax.imshow(Image.open(path))
        ax.set_title(path.stem, fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    plt.show()


if RUN_ID and VISION_VISUAL_DIR:
    show_image_grid(sorted(VISION_VISUAL_DIR.glob("train_sample_*.png"))[:8], "Training Samples")


# %% [markdown]
# ## Validation Predictions and Error Maps
#
# Use this panel to reject runs with collapsed predictions, implausible edges, or missing extreme classes before spending a submission.

# %%
if RUN_ID and VISION_VISUAL_DIR:
    show_image_grid(sorted(VISION_VISUAL_DIR.glob("val_pred_*.png"))[:20], "Validation Prediction Panels", columns=2, figsize=(16, 24))

if RUN_ID and VISION_VAL_PROBS and VISION_VAL_PROBS.exists():
    val_payload = np.load(VISION_VAL_PROBS, allow_pickle=True)
    pred = val_payload["y_pred"]
    true = val_payload["y_true"]
    print("Validation payload:", {key: val_payload[key].shape for key in val_payload.files if hasattr(val_payload[key], "shape")})
    print("Predicted class counts:", dict(zip(*np.unique(pred, return_counts=True))))
    print("Truth class counts:", dict(zip(*np.unique(true, return_counts=True))))


# %% [markdown]
# ## Test Predictions
#
# Test panels are generated by `scripts/run_subtask1_vision.py infer` or by training with `--write-test-visuals`.

# %%
if RUN_ID and VISION_VISUAL_DIR:
    show_image_grid(sorted(VISION_VISUAL_DIR.glob("test_pred_*.png"))[:20], "Test Prediction Panels", columns=2, figsize=(16, 24))


# %% [markdown]
# ## HGB Floor vs Vision Candidate
#
# Place the current HGB floor ZIP beside a vision ZIP and compare the same patch IDs. This is qualitative only; production inference stays in scripts.

# %%
import zipfile

HGB_ZIP = RESULTS_DIR / "submissions" / "20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip"
VISION_ZIP = RESULTS_DIR / "submissions" / f"{RUN_ID}.zip" if RUN_ID else None


def read_png_from_zip(zip_path, patch_id):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(f"{patch_id}.png") as handle:
            return np.asarray(Image.open(handle))


def compare_submission_masks(hgb_zip, vision_zip, patch_ids):
    if not hgb_zip.exists() or not vision_zip or not vision_zip.exists():
        print("Set HGB_ZIP and VISION_ZIP to existing submission files.")
        return
    fig, axes = plt.subplots(len(patch_ids), 3, figsize=(10, 3 * len(patch_ids)))
    axes = np.atleast_2d(axes)
    for row, patch_id in enumerate(patch_ids):
        hgb = read_png_from_zip(hgb_zip, patch_id)
        vision = read_png_from_zip(vision_zip, patch_id)
        diff = np.abs(hgb.astype("int16") - vision.astype("int16"))
        for ax, arr, title in zip(axes[row], [hgb, vision, diff], ["HGB floor", "Vision", "|diff|"]):
            ax.imshow(arr, cmap="viridis", vmin=0, vmax=4)
            ax.set_title(f"{patch_id}: {title}", fontsize=9)
            ax.axis("off")
    fig.tight_layout()
    plt.show()


if RUN_ID and VISION_ZIP and VISION_ZIP.exists():
    candidate_ids = [path.stem.replace("test_pred_", "", 1).split("_", 1)[1] for path in sorted(VISION_VISUAL_DIR.glob("test_pred_*.png"))[:5]]
    if candidate_ids:
        compare_submission_masks(HGB_ZIP, VISION_ZIP, candidate_ids)
    else:
        print("No exported test prediction panels found for this run.")
else:
    print("Run vision inference first to compare submission masks.")
