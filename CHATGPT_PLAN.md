# AI4Agri Competition Execution Plan

Last updated: 2026-05-04

## Goal

Produce valid, reproducible AI4Agri 2026 submissions before the May 7, 2026 competition deadline, then prepare the May 28 notebook/report materials.

Current strategy:

1. Build Subtask 2 first because the data is now local on RunPod, small enough for fast iteration, and has clear patch folders.
2. Keep Subtask 1 moving in parallel toward a valid CodaBench ZIP; do not wait for a high-quality model before proving packaging.
3. Use RunPod for data, feature extraction, training, inference, and anything that touches the full datasets.
4. Use local for code edits, review, result sync, documentation, commits, and submission prep.

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
- Still needed: local or remote access to actual image/label rasters for smoke-read, training, validation, and test inference.
- CSV files are now downloaded on RunPod under `data/subtask1/agripotential`, including `test.csv`.

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

## Active Assignments

### VB

- [ ] Confirm Subtask 1 CodaBench submission limits and evaluation timing.
- [ ] Confirm whether RunPod global networking is enabled in the Pod Connect/details tab.
- [ ] Keep the RunPod Pod running while Codex builds/runs Subtask 2 baseline; stop it when idle.
- [ ] After Codex produces first Subtask 2 metrics, review confusion matrices and decide whether to freeze tabular baseline or allow one neural attempt.
- [ ] Once Codex produces first Subtask 1 ZIP, submit to CodaBench and report score/errors.

### Codex

- [ ] Commit and push the current Subtask 2 inspection JSON and parser update.
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
- [ ] Implement a Subtask 1 smoke-read command against local/remote rasters once actual files are available.
- [ ] Keep `README.md`, `REMOTE_PROVIDER.md`, notebooks, and this plan aligned after each material change.

### Claude

- [X] Verify DACIA5 file-name label interpretation from examples like `patch_20240716_9748_3.tif`; confirm which token is crop label and whether `9748`/`3017` are field or parcel ids.
- [ ] Confirm Sentinel-2 band order for the 12-band patch TIFFs so Codex can safely add NDVI/NDWI/red-edge features.
- [ ] Find or infer expected Subtask 2 prediction artifact format from ImageCLEF/DACIA5 materials:
  - notebook-only evaluation,
  - CSV prediction file,
  - or zipped source plus report.
- [ ] Provide one compact Subtask 2 neural baseline recommendation only after tabular baseline metrics exist.
- [ ] For Subtask 1, verify whether official package examples include a direct raster download command that includes `test.csv`.

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

- [ ] Confirm CodaBench submission limits and evaluation timing.
- [ ] Confirm RunPod global networking status.

### Phase 1: Data Acquisition And Inspection

- [X] Inspect Subtask 1 metadata.
- [X] Download Subtask 1 CSV files on RunPod, including `test.csv`.
- [X] Download/extract Subtask 2 data.
- [X] Inspect Subtask 2 data.
- [X] Pull inspection JSONs locally.
- [X] Fix Subtask 2 split parsing in inspection script.

Remaining:

- [ ] Smoke-read Subtask 1 actual image and label rasters.
- [ ] Download Subtask 1 label/image rasters on RunPod when VB approves storage/time.
- [ ] Record exact Subtask 1 raster storage path once available on RunPod.

### Phase 2: Subtask 2 Fast Baseline

Priority: active now.

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

Priority: parallel but behind Subtask 2 until raster access is confirmed.

- [ ] Smoke-read rasters and labels.
- [ ] Train sampled-pixel ordinal baseline.
- [ ] Implement test inference writer for `800` PNG masks.
- [ ] Validate candidate ZIP with `scripts/validate_submission_zip.py`.
- [ ] Submit first valid ZIP through VB.

### Phase 4: Model Improvement

Start only after a valid baseline exists for the relevant subtask.

- [ ] Tune Subtask 2 tabular models.
- [ ] Add Subtask 2 neural baseline only if tabular results plateau.
- [ ] Add Subtask 1 class-balanced sampling.
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
python scripts/inspect_subtask1.py --splits train val test
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2
python scripts/subtask2_baseline.py features
# After the DACIA5 crop-label source is confirmed and labels are present:
python scripts/subtask2_baseline.py train --problem problem1
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
- Subtask 2 data downloaded, extracted, inspected, and pulled locally.
- Subtask 2 patch TIFF counts confirmed: problem 1 train/test `5436/1017`; problem 2 train/test `1176/1073`.

## Open Questions

- [ ] What are the Subtask 1 CodaBench submission limits and evaluation timing?
- [ ] Is RunPod global networking enabled?
- [ ] Are Subtask 2 test labels hidden, or is this primarily notebook/report evaluation?
- [ ] What is the exact Subtask 2 prediction/submission artifact format?
- [ ] What is the confirmed Sentinel-2 band order for DACIA5 12-band patch TIFFs?
- [ ] What is the confirmed label token in DACIA5 patch filenames?
