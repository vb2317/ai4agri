# Claude Findings: Phase 1

Last updated: 2026-05-04

## Subtask 2 Deliverable Format

Status: Done.

Sources:

- ImageCLEF 2026 AI4Agri page: https://www.imageclef.org/2026/ai4agri
- Zenodo DACIA5 record: https://zenodo.org/records/14915950

Findings:

- Subtask 2 is not a CodaBench-style prediction CSV upload.
- ImageCLEF states that Subtask 2 code should be shared as either a Google Colab notebook or a zipped source folder with clear execution instructions in a README.
- A technical report or extended abstract is required, maximum 3 pages.
- Optional supplementary materials may include visualizations, tables, diagrams, or a short video pitch.
- Materials are submitted by email to `ai4agri.imageclef2026@gmail.com`.
- If submitting both DACIA5 tracks, prepare separate submissions or clearly separated files for:
  - `Crop identification: Past_vs_present`
  - `Early crop identification`

Codex implementation notes:

- Prioritize a clean Subtask 2 notebook/report package over a hidden-test prediction artifact.
- Keep generated prediction CSVs and confusion matrices as reproducibility/report artifacts, not as the primary official deliverable unless organizers later request them.

## DACIA5 Label Grouping

Status: Done.

Sources:

- `vb_handoffs/Legend_crops.pdf`
- `results/subtask2/inspection/subtask2_label_inspection.json`
- `scripts/subtask2_baseline.py`
- ImageCLEF 2026 AI4Agri page: https://www.imageclef.org/2026/ai4agri

Findings:

- The implemented APIA-code grouping is defensible for the ImageCLEF class definitions:
  - `101`, `1010` -> Wheat
  - `108`, `131` -> Corn
  - `151` -> Peas
  - `202` -> Rapeseed
  - `253`, `254`, `255`, `2557` -> Potato
  - `3017` -> Sugarbeet
  - `9747`, `9748` -> Alfalfa
- The leakage control is sound: APIA code is only used to derive labels, while APIA code, parcel id, and patch index are excluded from model features.
- Unmapped APIA codes should remain unlabeled and excluded from training unless the report explicitly broadens the class mapping.

## Baseline Review

Status: Done.

Sources:

- `results/subtask2/inspection/subtask2_baseline_summary.json`
- `results/subtask2/inspection/subtask2_feature_summary.json`

Findings:

- The leakage-free tabular baseline is acceptable for the first notebook/report pass.
- Problem 1 best current model is HistGradientBoosting on a 2023 holdout: `Q=0.6655`, `OA=0.7442`, `AA=0.5867`.
- Problem 2 best current model is ExtraTrees on a 2024 holdout: `Q=0.8102`, `OA=0.8308`, `AA=0.7896`.
- Problem 1 still has weak per-class balance: the validation support has no Rapeseed examples and only `13` Potato examples, so the report should present this as a fast, leakage-controlled baseline rather than a final optimized classifier.
- Problem 2 is a stronger baseline, but the validation set is small: `130` rows, with `108` winter wheat and `22` alfalfa.

Recommendation:

- Use these results in the first Subtask 2 notebook/report skeleton.
- Do not spend the next local cycle on neural training while Subtask 1 full baseline is still active and DACIA5 band order is not confirmed.

## Sentinel-2 Band Order

Status: Blocked pending dataset metadata inspection on RunPod.

Sources checked:

- ImageCLEF 2026 AI4Agri page: https://www.imageclef.org/2026/ai4agri
- Zenodo DACIA5 record: https://zenodo.org/records/14915950
- `results/subtask2/inspection/subtask2_inspection.json`
- `results/subtask2/inspection/subtask2_feature_summary.json`

Findings:

- Public task and dataset pages confirm Sentinel-2 images and patches have `12` bands, but do not state band names/order.
- Existing local inspection confirms the arrays are `12 x 32 x 32` for patches and `12 x 800 x 450` for full Sentinel-2 GeoTIFFs, but it did not capture band descriptions or per-band tags.
- The band statistics are consistent with the common Sentinel-2 12-band L2A order excluding cirrus, likely `B01, B02, B03, B04, B05, B06, B07, B08, B8A, B09, B11, B12`; this is an inference, not a confirmed source-backed fact.

Next action:

- Re-run `scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays` on RunPod after the inspector update, then check `descriptions`, `band_tags`, and `dataset_tags` in `results/subtask2/inspection/subtask2_inspection.json`.
- Add NDVI/NDWI/red-edge/SWIR index features only if the tags/descriptions confirm band order or VB obtains confirmation from the organizers.

## Neural Baseline Recommendation

Status: Done.

Recommendation:

- Skip neural training for now.
- If there is spare RunPod time after Subtask 1 submission, the only compact neural attempt worth considering is a small patch-level temporal CNN/MLP over the `12 x 32 x 32` optical patch tensor with balanced sampling and heavy regularization.
- Do not implement it before the Subtask 2 notebook/report skeleton is complete; the current tabular baseline is reproducible, fast, and already strong enough for a first pass.
