# Claude Handoffs: Phase 1

Use this while Codex continues implementation and packaging.

## Current Codex Findings

- DACIA5 patch filenames are `patch_YYYYMMDD_<APIA code>_<patch index>.tif`.
- The included `Dataset/Masks_and_legend/Legend_crops.pdf` confirms the middle token is the APIA crop code.
- The final filename token ranges from `1` to `52`; it is a patch index, not a crop label.
- All multispectral patch TIFFs have matching per-patch RGB masks:
  - Problem 1 test: `1017 / 1017`
  - Problem 1 training: `5436 / 5436`
  - Problem 2 test: `1073 / 1073`
  - Problem 2 training: `1176 / 1176`
- Current leakage-free tabular metrics:
  - Problem 1, HistGradientBoosting, 2023 holdout: `Q=0.6655`, `OA=0.7442`, `AA=0.5867`.
  - Problem 2, ExtraTrees, 2024 holdout: `Q=0.8102`, `OA=0.8308`, `AA=0.7896`.
- Leakage control: APIA code is used only to derive labels and is excluded from model features along with patch index.

Tracked evidence:

- `results/subtask2/inspection/subtask2_label_inspection.json`
- `results/subtask2/inspection/subtask2_feature_summary.json`
- `results/subtask2/inspection/subtask2_baseline_summary.json`

## Needed From Claude

```text
Project: AI4Agri 2026 Subtask 2 DACIA5.

Task:
Now that Codex has a leakage-free tabular baseline, verify the remaining report/submission and feature-improvement assumptions.

Needed output:
- Confirm expected Subtask 2 final deliverable format for ImageCLEF 2026: notebook-only, ZIP/source, CSV predictions, report, or a combination.
- Confirm Sentinel-2 12-band order for the patch TIFFs so Codex can safely add NDVI, NDWI, red-edge, and SWIR indices.
- Review whether grouping APIA codes as implemented is defensible:
  - 101 and 1010 -> Wheat
  - 108 and 131 -> Corn
  - 151 -> Peas
  - 202 -> Rapeseed
  - 253/254/255/2557 -> Potato
  - 3017 -> Sugarbeet
  - 9747/9748 -> Alfalfa
- Recommend one compact neural baseline only if it is likely to improve beyond the current tabular metrics within the remaining time.

Constraints:
- Do not ask Codex to train anything until band order and deliverable format are confirmed.
- Keep answer concise and cite the exact source or file used.
```
