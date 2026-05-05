# AI4Agri 2026 Subtask 2 Technical Report Draft

## Title

Leakage-Free Tabular Baselines for DACIA5 Crop Identification

## Abstract

We address AI4Agri 2026 Subtask 2 on crop identification from the DACIA5 Sentinel time series near Brasov, Romania. The current system is a reproducible baseline designed for fast validation and clear reporting rather than maximum accuracy. It parses DACIA5 patch filenames, derives class labels from the confirmed APIA crop-code token, extracts simple per-band statistics from each 32x32 multispectral patch, and trains classical tabular classifiers. On local year-aware holdout validation, the best Challenge 1 baseline is HistGradientBoosting with `Q=0.6655`, and the best Challenge 2 baseline is ExtraTrees with `Q=0.8102`.

## Data And Tasks

DACIA5 contains full-scene Sentinel-2 GeoTIFFs and 32x32 multispectral patch TIFFs for 2020-2024. The inspected patch TIFFs have shape `12 x 32 x 32` and dtype `uint16`. Challenge 1 predicts seven crop classes for the 2024 setting after training from historical data. Challenge 2 performs early crop identification for winter wheat versus alfalfa using early-season imagery.

The extracted dataset contains:

- Problem 1 training patches: `5436`
- Problem 1 test patches: `1017`
- Problem 2 training patches: `1176`
- Problem 2 test patches: `1073`

Labels are derived from the middle filename token in names such as `patch_20240716_9748_3.tif`. The token `9748` is an APIA crop code, while the final token is only a patch index. The mapping currently used is:

- Wheat: `101`, `1010`
- Corn: `108`, `131`
- Peas: `151`
- Rapeseed: `202`
- Potato: `253`, `254`, `255`, `2557`
- Sugarbeet: `3017`
- Alfalfa: `9747`, `9748`

Unmapped APIA codes are excluded from training.

## Method

The workflow is implemented in `scripts/subtask2_baseline.py` and has three stages:

1. Manifest creation: discover patch TIFFs, parse problem, split, date, year, APIA code, and patch index.
2. Feature extraction: read each patch with `rasterio` and compute per-band mean, standard deviation, min, max, and percentiles.
3. Training: fit ExtraTreesClassifier and HistGradientBoostingClassifier on confirmed labels, excluding APIA code, parcel id, and patch index from model features.

This design avoids leakage from identifiers while keeping the run fast enough for iteration on remote compute. Vegetation indices are intentionally not included yet because the Sentinel-2 12-band order has not been confirmed in the public materials or tracked dataset metadata.

## Validation

The current validation uses year-aware holdouts:

- Problem 1: hold out 2023 from training rows.
- Problem 2: hold out 2024 from training rows.

Current results from `results/subtask2/inspection/subtask2_baseline_summary.json`:

| Problem | Best model | Split | OA | AA | Q |
|---|---|---|---:|---:|---:|
| Problem 1 | HistGradientBoosting | 2023 holdout | `0.7442` | `0.5867` | `0.6655` |
| Problem 2 | ExtraTrees | 2024 holdout | `0.8308` | `0.7896` | `0.8102` |

The Problem 1 validation set is imbalanced and has no Rapeseed examples and only `13` Potato examples. These metrics should therefore be presented as leakage-controlled baselines rather than optimized final performance. Problem 2 is stronger but is also based on a small validation set of `130` rows.

## Reproducibility

Run the following from a RunPod checkout with the DACIA5 archive available:

```bash
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/inspect_subtask2_labels.py --data-dir data/subtask2
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2 --label-mode apia-code
python scripts/subtask2_baseline.py features
python scripts/subtask2_baseline.py label-features
python scripts/summarize_subtask2_features.py
python scripts/subtask2_baseline.py train --problem problem1
python scripts/subtask2_baseline.py train --problem problem2
```

Package the current source/report bundle with:

```bash
python scripts/package_subtask2_submission.py
```

## Limitations And Next Work

The largest unresolved technical blocker is confirmed Sentinel-2 band order. Once confirmed, the next low-risk feature pass is to add NDVI, NDWI, red-edge, and SWIR ratio features. A compact neural model is not currently recommended before the notebook/report package is complete, because the tabular baseline is reproducible and already provides defensible first-pass results.
