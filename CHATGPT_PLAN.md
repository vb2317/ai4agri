# AI4Agri Competition Execution Plan

Last updated: 2026-05-04

## Goal

Produce valid, reproducible AI4Agri 2026 submissions before the May 7, 2026 competition deadline, then prepare the May 28 notebook/report materials.

Current strategy:

1. Focus Subtask 1 first until the sampled-pixel model ZIP is submitted and feedback is recorded.
2. Use the constant ZIP result as the floor score while the sampled-pixel baseline is trained and validated.
3. Use RunPod for data, feature extraction, training, inference, and anything that touches the full datasets.
4. Use local for code edits, review, result sync, documentation, commits, and submission prep.

Related docs:

- `ARCHITECTURE.md`: local/remote topology, pipeline layout, and artifact policy.
- `REMOTE_PROVIDER.md`: current RunPod state and pending remote operating steps.
- `HANDOFF_STRATEGY.md`: ownership rules for VB, Codex, and Claude.

## Current State

### Access And Remote

- ImageCLEF/CLEF registration: confirmed by VB.
- Subtask 1 CodaBench access: confirmed by VB.
- Remote provider: RunPod.
- RunPod Pod ID: `vit08hc86csllk`.
- Remote project path: `/workspace/ai4agri`.
- Remote data path: `/workspace/ai4agri/data`.
- Remote results path: `/workspace/ai4agri/results`.
- Budget ceiling: `$75`.
- Current listed RunPod cost: `$0.71/hr`.
- Remote environment: PyTorch CUDA verified; project validator verified.

### Subtask 1: AgriPotential

- Data source: Hugging Face `m-sakka/agripotential`.
- Metadata inspection is complete from remote URLs.
- Split counts:
  - train: `6329`
  - val: `781`
  - test: `800`
- Patch size: `128 x 128`.
- Input metadata: `34` Sentinel-2 image rows.
- Confirmed CodaBench format: ZIP root contains PNG masks named `<patch_id>.png`; values are class ids `0..4`; optional method PDF must be named `report.pdf`.
- Added downloader can fetch CSVs, label rasters, and optional Sentinel-2 image rasters into `data/subtask1`.
- Constant-mask CodaBench ZIP has been generated and validated locally:
  - `results/subtask1/submissions/constant_class_2.zip`
  - `800` root-level PNG masks
  - exact `test.csv` patch ids matched
  - grayscale class values checked without requiring Pillow
- Constant-mask CodaBench submission completed:
  - score: `39.52`
  - daily submissions: `10`
  - total submissions: `100`
  - scoring: immediate
- RunPod Subtask 1 data state:
  - path: `/workspace/ai4agri/data/subtask1`
  - CSVs present: `metadata.csv`, `train.csv`, `val.csv`, `test.csv`
  - label raster present: `viticulture.tif`
  - Sentinel-2 image rasters downloaded
  - disk usage reported by VB: `185G`
  - label smoke-read succeeded for train/val/test samples.
- Still needed: smoke train sampled-pixel baseline, run full sampled-pixel baseline, infer ZIP, validate ZIP, submit to CodaBench.
- Latest sampled-pixel smoke run:
  - model: `hist_gradient_boosting`
  - train patches: `20`
  - validation patches: `5`
  - train pixels: `5000`
  - validation pixels: `1250`
  - feature count: `340`
  - exact accuracy: `0.5648`
  - Accuracy +/- 1: `0.9136`
  - MAE: `0.5768`
  - caveat: validation sample only contains classes `0` and `1`, so this is a pipeline smoke test, not a representative score.

### Subtask 2: DACIA5

- Data is downloaded and extracted on RunPod under `data/subtask2`.
- Inspection output is pulled locally at `results/subtask2/inspection/subtask2_inspection.json`.
- File counts:
  - total files: `18043`
  - TIFF: `8874`
  - MAT: `8707`
  - PNG: `455`
  - full Sentinel-2 GeoTIFFs: `172`
- Patch TIFF groups:
  - problem 1 training: `5436`
  - problem 1 test: `1017`
  - problem 2 training: `1176`
  - problem 2 test: `1073`
- Patch array smoke-read: `12 x 32 x 32`, `uint16`.
- Full Sentinel-2 GeoTIFF smoke-read: `12 x 800 x 450`, `uint16`.
- Label source: confirmed from `Legend_crops.pdf`; patch filename middle token is APIA crop code, final token is patch index.
- Current leakage-free baselines:
  - Problem 1, HistGradientBoosting, 2023 holdout: `Q=0.6655`, `OA=0.7442`, `AA=0.5867`.
  - Problem 2, ExtraTrees, 2024 holdout: `Q=0.8102`, `OA=0.8308`, `AA=0.7896`.
- Tabular baseline implementation is complete locally.
- Still needed: confirmed Sentinel-2 band order before vegetation indices and confirmed final Subtask 2 notebook/report/submission artifact expectations.

## Active Assignments

### VB

- [X] Submit Subtask 1 constant baseline ZIP to CodaBench and record score/errors:
  - `results/subtask1/submissions/constant_class_2.zip`
- [X] Confirm Subtask 1 CodaBench submission limits and evaluation timing:
  - daily cap: `10`
  - total cap: `100`
  - scoring: immediate
- [X] Confirm RunPod global networking status:
  - pod location: `EU-RO-1`
  - global networking: off
  - public internet downloads nevertheless succeeded.
- [ ] Keep the RunPod Pod running while Subtask 1 training/inference is active; stop it when idle.
- [ ] After sampled-pixel Subtask 1 ZIP validates, submit it to CodaBench and record score/errors.
- [ ] Defer Subtask 2 review decisions until Subtask 1 sampled-pixel submission is complete.

### Codex

- [X] Commit and push the current Subtask 2 inspection JSON and parser update.
- [X] Add canonical Subtask 2 baseline workflow in `scripts/subtask2_baseline.py`:
  - [X] Parse problem, split, date, field/parcel id, and unverified label candidates from file paths/names.
  - [X] Load patch arrays through `rasterio`.
  - [X] Create a CSV manifest under `results/subtask2/`.
  - [X] Per-band mean, std, min, max.
  - [X] Selected percentiles.
  - [X] Cache features under remote `results/subtask2/features/`.
  - [X] ExtraTreesClassifier.
  - [X] HistGradientBoostingClassifier.
  - [X] Overall accuracy, average class accuracy, and `Q = 0.5 * OA + 0.5 * AA`.
  - [X] Save metrics, confusion matrices, predictions, and run metadata.
- [X] Keep `scripts/train_subtask2_baseline.py` as a direct experimental trainer; use only after DACIA5 filename label semantics are confirmed.
- [X] Add exploratory test-bed notebooks for both subtasks:
  - [X] `notebooks/subtask1_testbed.ipynb`
  - [X] `notebooks/subtask2_testbed.ipynb`
- [X] Pair notebooks with `.py:percent` files using `nbpair`; keep them synced with `nbsync`.
- [X] Run Subtask 2 manifest and feature extraction on RunPod:
  - [X] Manifest: `8702` rows.
  - [X] Features: `8702 x 124`, `0` extraction errors.
- [X] Confirm DACIA5 label source before running training with labels:
  - [X] `Legend_crops.pdf` maps APIA codes to crop labels/colors.
  - [X] Filename token 2 is APIA crop code.
  - [X] Filename token 3 is patch index and is not a label.
- [X] Train first leakage-free Subtask 2 tabular baselines.
- [ ] Add simple vegetation indices only after band order is confirmed.
- [X] Add Subtask 1 downloader that includes `test.csv` and optional label/image raster downloads.
- [X] Download Subtask 1 CSV metadata/test files on RunPod.
- [X] Implement a Subtask 1 smoke-read command against local/remote rasters once actual files are available.
- [X] Run Subtask 1 sampled-pixel smoke training on RunPod.
- [ ] While full Subtask 1 training runs:
  - [ ] Receive completion output from VB.
  - [ ] Check whether validation class coverage is representative enough for a first submission decision.
  - [ ] If full training fails from I/O/runtime, revise `scripts/subtask1_baseline.py` to keep raster datasets open across patches and rerun with bounded samples.
- [ ] After full Subtask 1 training completes:
  - [ ] Pull `results/subtask1/baseline/metrics.json` and model metadata locally.
  - [ ] Summarize exact accuracy, Accuracy +/- 1, MAE, label counts, confusion matrix, train/val pixels, and model type.
  - [ ] Run model-based inference on RunPod.
  - [ ] Validate `results/subtask1/submissions/subtask1_baseline.zip`.
  - [ ] Pull the validated ZIP locally for VB submission.
- [ ] If sampled-pixel score underperforms constant baseline:
  - [X] Add class-balanced pixel sampling.
  - [ ] Try `--model extra_trees`.
  - [ ] Consider median/majority post-processing only after a valid model ZIP exists.
- [X] Implement a Subtask 1 constant-mask ZIP writer for CodaBench packaging smoke tests.
- [X] Implement a Subtask 1 Hugging Face downloader for CSVs, labels, and image rasters.
- [X] Keep `README.md`, `REMOTE_PROVIDER.md`, notebooks, and this plan aligned after latest local tooling changes.

### Claude

- [X] Verify DACIA5 file-name label interpretation from examples like `patch_20240716_9748_3.tif`; confirm which token is crop label and whether `9748`/`3017` are field or parcel ids.
- [ ] Confirm Sentinel-2 band order for the 12-band patch TIFFs so Codex can safely add NDVI/NDWI/red-edge features.
- [ ] Find or infer expected Subtask 2 prediction artifact format from ImageCLEF/DACIA5 materials:
  - notebook-only evaluation,
  - CSV prediction file,
  - or zipped source plus report.
- [ ] Review `results/subtask2/inspection/subtask2_baseline_summary.json` and recommend whether the leakage-free tabular baseline is acceptable for the first report/notebook pass.
- [ ] Provide one compact Subtask 2 neural baseline recommendation only if it can realistically improve on:
  - Problem 1 HGB `Q=0.6655`
  - Problem 2 ExtraTrees `Q=0.8102`
- [X] For Subtask 1, verify whether official package examples include a direct raster download command that includes `test.csv`.
  - Repo downloader `scripts/download_subtask1_hf.py` is the current canonical path and includes `test.csv`.

## Phase Tracker

### Phase 0: Access And Environment

- [X] Confirm registration and CodaBench access.
- [X] Confirm Subtask 1 CodaBench ZIP structure.
- [X] Launch RunPod and record details.
- [X] Sync repo to RunPod.
- [X] Install remote dependencies.
- [X] Verify CUDA and validator script.
- [X] Add remote management scripts.

Remaining:

- [X] Confirm CodaBench submission limits and evaluation timing.
- [X] Confirm RunPod global networking status.

### Phase 1: Data Acquisition And Inspection

- [X] Inspect Subtask 1 metadata.
- [X] Download Subtask 1 CSV files on RunPod, including `test.csv`.
- [X] Download/extract Subtask 2 data.
- [X] Inspect Subtask 2 data.
- [X] Pull inspection JSONs locally.
- [X] Fix Subtask 2 split parsing in inspection script.

Remaining:

- [X] Smoke-read Subtask 1 labels from actual label raster.
- [X] Download Subtask 1 label/image rasters on RunPod.
- [X] Add reproducible Subtask 1 downloader for remote `data/subtask1`.
- [X] Record exact Subtask 1 raster storage path once available on RunPod: `/workspace/ai4agri/data/subtask1`.
- [ ] Smoke-read one Subtask 1 image raster window together with labels if not already included in the latest inspection.

### Phase 2: Subtask 2 Fast Baseline

Priority: parked until Subtask 1 sampled-pixel CodaBench submission is complete.

- [X] Build manifest/feature/training scripts for patch TIFF folders.
- [X] Add notebook cells that showcase data, artifact summaries, visual checks, and feature distributions without running the workflow.
- [X] Add notebook alias routine: `nbopen`, `nbpair`, `nbsync`, `nbrun` when data is available.
- [X] Run manifest from patch TIFF folders on RunPod.
- [X] Extract cached tabular features on RunPod.
- [X] Derive labels from APIA crop-code token and `Legend_crops.pdf`.
- [X] Train baseline models after label source is confirmed.
- [X] Save remote validation metrics and confusion matrices.
- [X] Generate candidate predictions/artifacts for review.

Remaining:

- [ ] Confirm Subtask 2 submission artifact expectations.
- [ ] Confirm Sentinel-2 band order before vegetation indices.
- [ ] Decide whether current tabular baseline is enough for the first notebook/report pass or whether to run a neural attempt.

### Phase 3: Subtask 1 Valid Baseline

Priority: active now.

- [X] VB submits validated constant ZIP: `results/subtask1/submissions/constant_class_2.zip`.
- [X] Record constant baseline CodaBench score: `39.52`.
- [X] Download Subtask 1 CSVs and `viticulture.tif` on RunPod with `scripts/download_subtask1_hf.py --skip-images`.
- [X] Smoke-read labels from one patch.
- [X] Download full Sentinel-2 image rasters if RunPod disk/time budget allows.
- [ ] Smoke-read image rasters and labels together.
- [X] Implement sampled-pixel ordinal baseline trainer.
- [X] Implement sampled-pixel baseline improvements for next run:
  - [X] Keep all Sentinel-2 rasters open across patches for train/infer.
  - [X] Shuffle split rows before sampling.
  - [X] Default to class-balanced pixel sampling.
  - [X] Add raw plus temporal summary features via `--feature-mode raw_temporal`.
  - [X] Remove unused inference temp directory.
  - Note: the full run already triggered by VB used the previous script version unless RunPod was updated before launch.
- [X] Run sampled-pixel smoke training:
  ```bash
  python scripts/subtask1_baseline.py train \
    --data-dir data/subtask1 \
    --patch-limit 20 \
    --val-patch-limit 5 \
    --pixels-per-patch 256 \
    --max-train-pixels 5000
  ```
  - Result: exact `0.5648`, Accuracy +/- 1 `0.9136`, MAE `0.5768`.
  - Caveat: validation sample covered only classes `0` and `1`.
- [ ] Full sampled-pixel baseline training:
  - Status: running on RunPod.
  ```bash
  python scripts/subtask1_baseline.py train --data-dir data/subtask1
  ```
  - Capture on completion: exact accuracy, Accuracy +/- 1, MAE, label counts, confusion matrix, model path, metrics path.
- [ ] Review full-run metrics:
  - [ ] Confirm validation covers more than the smoke-run classes `0` and `1`.
  - [ ] Compare Accuracy +/- 1 against constant baseline score `39.52`.
  - [ ] Decide whether to submit immediately or do one quick improvement pass.
- [X] Implement constant test inference writer for `800` PNG masks.
- [X] Implement model-based test inference writer for `800` PNG masks.
- [X] Validate constant candidate ZIP with `scripts/validate_submission_zip.py`.
- [ ] Infer model-based ZIP:
  ```bash
  python scripts/subtask1_baseline.py infer --data-dir data/subtask1
  ```
- [ ] Validate model-based ZIP:
  ```bash
  python scripts/validate_submission_zip.py \
    --zip-path results/subtask1/submissions/subtask1_baseline.zip \
    --subtask1-codabench \
    --expected-ids-file data/subtask1/test.csv \
    --check-class-values
  ```
- [ ] Pull metrics/submission locally.
- [ ] VB submits `results/subtask1/submissions/subtask1_baseline.zip` and records score/errors.

### Phase 4: Model Improvement

Start only after a valid baseline exists for the relevant subtask.

- [ ] Tune Subtask 2 tabular models.
- [ ] Add Subtask 2 neural baseline only if tabular results plateau.
- [X] Add Subtask 1 class-balanced sampling.
- [ ] Try Subtask 1 `extra_trees` if the current sampled-pixel model underperforms.
- [ ] Try Subtask 1 ensemble or lightweight neural model only if the data pipeline is stable.

### Phase 5: Packaging And Report

- [ ] Create final reproducible notebook for Subtask 2.
- [ ] Draft 3-page technical report.
- [ ] Add commands to reproduce final predictions.
- [ ] VB reviews and submits by May 28, 2026.

## Remote Commands

Push local scripts/docs to RunPod:

```bash
scripts/runpod_sync.sh push
```

Run a remote command:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Bootstrap remote environment:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_bootstrap.sh'
```

Inspect data on RunPod:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/inspect_subtask1.py --data-dir data/subtask1 --splits train val test --limit 1 --read-labels
python scripts/inspect_subtask1.py --data-dir data/subtask1 --splits train val test --limit 1 --read-pixels --read-labels
python scripts/create_subtask1_constant_zip.py
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2 --label-mode apia-code
python scripts/subtask2_baseline.py features
python scripts/subtask2_baseline.py label-features
python scripts/subtask2_baseline.py train --problem problem1
```

Train and validate the active Subtask 1 sampled-pixel baseline on RunPod:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/subtask1_baseline.py train \
  --data-dir data/subtask1 \
  --patch-limit 20 \
  --val-patch-limit 5 \
  --pixels-per-patch 256 \
  --max-train-pixels 5000
python scripts/subtask1_baseline.py train --data-dir data/subtask1
python scripts/subtask1_baseline.py infer --data-dir data/subtask1
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/subtask1_baseline.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

Experimental direct Subtask 2 trainer, only after filename labels are confirmed:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/train_subtask2_baseline.py --data-dir data/subtask2 --problem 1
python scripts/train_subtask2_baseline.py --data-dir data/subtask2 --problem 2
```

Download/extract Subtask 2 on RunPod:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
```

Pull results or inspection outputs:

```bash
scripts/runpod_sync.sh pull-results
scripts/runpod_sync.sh pull-inspection
```

Validate a Subtask 1 CodaBench ZIP:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/example.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

## Handoff Template

Use this when assigning a bounded question to Claude while Codex continues implementation.

```text
Project: AI4Agri 2026 repo.

Task:
[Specific research or implementation-support question.]

Current known state:
[Relevant data paths, counts, or scripts.]

Constraints:
- Return concise findings.
- Include exact links or file names if relevant.
- Prefer low-risk methods that can be implemented in under one day.
- Do not assume raw data is available unless stated.

Needed output:
- Findings.
- Recommended next action.
- Any command or code sketch that Codex can adapt.
```

## Decision Log

### 2026-05-04

- Strategy set: valid baselines first; use RunPod for data-heavy work; prioritize Subtask 2 fast iteration while keeping Subtask 1 packaging path open.
- RunPod selected after Lambda billing setup was blocked.
- RunPod Pod launched and verified with CUDA.
- Subtask 1 CodaBench ZIP format confirmed from VB handoffs.
- Claude completed Phase 0 research on AgriPotential, DACIA5, and fast baseline options.
- Added validators, inspection scripts, remote sync/exec/bootstrap/status helpers, and Subtask 2 download/extract helpers.
- Subtask 1 metadata inspection confirmed `6329/781/800` train/val/test patches.
- Subtask 1 constant class `2` ZIP submitted to CodaBench and scored `39.52`.
- CodaBench limits confirmed: `10` daily submissions, `100` total submissions, immediate scoring.
- Subtask 1 full RunPod data downloaded under `/workspace/ai4agri/data/subtask1`; reported disk usage `185G`.
- Subtask 2 data downloaded, extracted, inspected, and pulled locally.
- Subtask 2 patch TIFF counts confirmed: problem 1 train/test `5436/1017`; problem 2 train/test `1176/1073`.
- Subtask 2 APIA-code labels confirmed from `Legend_crops.pdf`; first leakage-free tabular baselines trained.

## Open Questions

- [X] What are the Subtask 1 CodaBench submission limits and evaluation timing?
- [X] Is RunPod global networking enabled?
- [ ] Are Subtask 2 test labels hidden, or is this primarily notebook/report evaluation?
- [ ] What is the exact Subtask 2 prediction/submission artifact format?
- [ ] What is the confirmed Sentinel-2 band order for DACIA5 12-band patch TIFFs?
- [X] What is the confirmed label token in DACIA5 patch filenames?
