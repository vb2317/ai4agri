# AI4Agri Competition Execution Plan

Last updated: 2026-05-05

## Goal

Produce valid, reproducible AI4Agri 2026 submissions before the May 7, 2026 competition deadline, then prepare the May 28 notebook/report materials.

Current strategy:

1. Treat Subtask 1 score `50.63` as the current submitted floor.
2. Spend remaining Subtask 1 submissions only on candidates with a credible path above `50.63`.
3. Prefer inference-only postprocessing of the submitted ResNet/FPN checkpoint before more retraining.
4. Keep HGB and smaller U-Net runs as fallback/ensemble evidence, not as the main optimization path.
5. Submit only after ZIP validation, candidate audit, visual review, and non-collapsed prediction checks pass.

Related docs:

- `ARCHITECTURE.md`: local/remote topology, pipeline layout, and artifact policy.
- `REMOTE_PROVIDER.md`: current RunPod state and pending remote operating steps.
- `HANDOFF_STRATEGY.md`: ownership rules for VB, Codex, and Claude.

## Today Strategy: 2026-05-05

The full-data TinyViT lane produced the new submitted floor `50.63`. The immediate goal is now disciplined submission management: keep the floor, try only low-risk improvements, and stop idle RunPod spend when no training or inference is active.

### Priority Order

1. Confirm remaining CodaBench daily/total submission budget.
2. Stop any idle RunPod pod if no command is actively running.
3. Try one inference-only postprocess candidate from `l40s_resnet_fpn_summary_e30/best.pt`.
4. Submit only if the candidate audit passes and visual review does not show an obvious regression.
5. Record every upload score immediately in `Next.md` and this plan.
6. Keep the targeted HGB suite only as fallback/ensemble evidence:
   ```bash
   python scripts/run_subtask1_experiments.py \
     --data-dir data/subtask1 \
     --suite targeted \
     --infer-best \
     --validate-best
   ```

### Submission Gate

Do not submit a new Subtask 1 ZIP unless:

- ZIP validation passes with `--subtask1-codabench`, expected ids, and class-value checks.
- The producing run has saved metrics and a reproducible config under `results/subtask1/vision_runs/`.
- Visual panels exist for training samples, validation predictions/error maps, and test predictions.
- The candidate is not just a duplicate of the already-submitted `50.63` full-data TinyViT baseline.
- `scripts/review_subtask1_candidate.py --run-id <run_id> --data-dir data/subtask1` passes, or any failure is explicitly accepted by VB.
- VB records the CodaBench score immediately after submission.

### VB Quick Instructions

1. Use `Next.md` as the short operating checklist.
2. Keep `50.63` as the floor.
3. Before any upload, run or request the candidate audit and visually review `results/subtask1/visuals/<run_id>/`.
4. If the pod is idle, stop it.
5. Record each new score immediately.

### Transformer Information Runs

Started on the L40S at `2026-05-05T12:07:21Z` and finished at `2026-05-05T12:32:32Z`.

Goal: collect transformer validation probabilities and visuals for ensemble analysis while VB reviews existing artifacts. These are not submission candidates until metrics, visuals, and audit evidence say otherwise.

- `l40s_tiny_vit_summary_soft_p1536_v256_s52`: TinyViT, summary features, soft ordinal CE, seed `52`, validation Accuracy +/- 1 `0.75066`.
- `l40s_tiny_vit_seasonal_soft_p1536_v256_s53`: TinyViT, seasonal features, soft ordinal CE, seed `53`, validation Accuracy +/- 1 `0.74500`.
- `l40s_tiny_vit_summary_wce_p1536_v256_s54`: TinyViT, summary features, weighted CE, seed `54`, validation Accuracy +/- 1 `0.72038`.

Interpretation: none is a standalone submit candidate against the `50.63` floor. The weighted-CE TinyViT is the most useful ensemble-diversity probe because it recovers class 4 recall `0.5405` and class 2 recall `0.0782`, while the soft-CE variants mostly miss class 2.

## Current State

### Access And Remote

- ImageCLEF/CLEF registration: confirmed by VB.
- Subtask 1 CodaBench access: confirmed by VB.
- Remote provider: RunPod.
- Last known RunPod Pod ID: `vit08hc86csllk`.
- Existing pod is recorded in `.env`; Claude's L40S pod is recorded in `.env.l40s.claude`.
- RunPod helpers accept `--env-file PATH`; do not overwrite `.env` when configuring Claude's L40S pod.
- Replacement pod migration has two supported modes:
  - Mode A: attach existing `/workspace` volume and verify `data/subtask1` before running.
  - Mode B: start without data, redownload Subtask 1, then smoke-read images/labels before running.
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
- Sampled-pixel baseline CodaBench submission completed:
  - file: `results/subtask1/submissions/subtask1_baseline.zip`
  - score: `39.74`
  - improvement over constant baseline: `+0.22`
  - note: confirm whether this ZIP was produced by the older script version or the optimized class-balanced/raw-temporal version.
- Overnight uniform raw-temporal HGB CodaBench submission completed:
  - file: `results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip`
  - score: `40.16`
  - improvement over previous sampled-pixel baseline: `+0.42`
  - improvement over constant baseline: `+0.64`
  - conclusion: validation signal was directionally useful; uniform sampling is currently preferred over class-balanced sampling for this baseline family.
- RunPod Subtask 1 data state:
  - path: `/workspace/ai4agri/data/subtask1`
  - CSVs present: `metadata.csv`, `train.csv`, `val.csv`, `test.csv`
  - label raster present: `viticulture.tif`
  - Sentinel-2 image rasters downloaded
  - disk usage reported by VB: `185G`
  - label smoke-read succeeded for train/val/test samples.
- L40S vision lane status:
  - GPU: `NVIDIA L40S`, CUDA PyTorch available.
  - `data/subtask1` present, reported size `185G`.
  - ResNet/FPN smoke completed with run id `l40s_smoke_resnet_fpn_summary_random`.
  - TinyViT smoke completed with run id `l40s_smoke_tiny_vit_summary_retry`.
  - Full ResNet/FPN run `l40s_resnet_fpn_summary_e30` completed with best validation Accuracy +/- 1 `0.78984`.
  - ZIP generated and validated: `results/subtask1/submissions/l40s_resnet_fpn_summary_e30.zip`.
  - Candidate audit passed with all classes present, class 4 pixel fraction `0.01236`, and `28/800` flat PNGs.
- L40S ResNet/FPN CodaBench submission completed:
  - file: `results/subtask1/submissions/l40s_resnet_fpn_summary_e30.zip`
  - score: `47.6`
  - improvement over previous `40.16` floor: `+7.44`
- Full-data TinyViT CodaBench submission completed:
  - file: `results/subtask1/submissions/l40s_tiny_vit_summary_soft_full_e30_s52.zip`
  - score: `50.63`
  - improvement over previous `47.6` floor: `+3.03`
- Still needed: decide whether to spend remaining Subtask 1 submissions on ensemble/postprocess attempts above the `50.63` floor.
- Overnight experiment suite completed on RunPod:
  - run root: `results/subtask1/experiments/20260504T180650Z/overnight`
  - best validation run by Accuracy +/- 1: `hgb_uniform_temporal_200k_s43`
  - best validation metrics: Accuracy +/- 1 `0.72604`, exact accuracy `0.5524`, MAE `0.97296`
  - best ZIP: `results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip`
  - inference return code: `0`
  - validation return code: `0`
  - interpretation: uniform sampling beat class-balanced sampling on validation; raw-temporal features beat raw for comparable HGB runs.
  - CodaBench score: `40.16`.
  - next action: plan a targeted follow-up around the winning configuration.
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
- Confirmed Subtask 2 final deliverable format: Google Colab notebook or zipped source folder with README, plus a max 3-page technical report, submitted by email.
- Still needed: confirmed Sentinel-2 band order before vegetation indices.

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
- [X] After sampled-pixel Subtask 1 ZIP validates, submit it to CodaBench and record score/errors:
  - score: `39.74`
- [ ] Keep Subtask 1 leaderboard work as the active priority.
- [ ] When new RunPod is ready, update `.env` with `scripts/configure_runpod_env.sh --test`.
- [ ] Choose migration Mode A or Mode B from `REMOTE_PROVIDER.md` based on whether `data/subtask1` exists on the attached volume.
- [ ] Start the targeted Subtask 1 suite after data checks pass.
- [ ] Submit the next Subtask 1 candidate only after validation passes and metrics suggest a plausible improvement.
- [ ] Resume Subtask 2 review decisions after the next Subtask 1 leaderboard-improvement pass.

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
- [X] First full Subtask 1 training/inference/submission path completed:
  - [X] Model-based ZIP submitted to CodaBench.
  - [X] CodaBench score recorded: `39.74`.
- [ ] Run the next Subtask 1 leaderboard candidate:
  - [X] Confirm RunPod has current experiment runner.
  - [X] Run `scripts/run_subtask1_experiments.py --data-dir data/subtask1 --suite overnight --infer-best --validate-best`.
  - [X] Review log output from `results/subtask1/experiments/20260504T180650Z/overnight/summary.csv`.
  - [X] Inspect `results/subtask1/experiments/20260504T180650Z/overnight/best_inference.json`.
  - [ ] Pull `summary.csv`, `summary.json`, `best_inference.json`, and the best candidate ZIP locally.
  - [X] Submit `results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip` to CodaBench:
    - score: `40.16`
- [ ] While RunPod is starting/running, prepare the next code improvement candidate:
  - [X] Add targeted HGB uniform raw-temporal suite with larger pixel budgets and multiple seeds.
  - [ ] Add a postprocessing or calibration path only after the targeted summary identifies the failure mode.
  - [X] Keep changes compatible with `scripts/run_subtask1_experiments.py`.
- [ ] If sampled-pixel score underperforms constant baseline:
  - [X] Add class-balanced pixel sampling.
  - [ ] Try `--model extra_trees`.
  - [ ] Consider median/majority post-processing only after a valid model ZIP exists.
- [X] Implement a Subtask 1 constant-mask ZIP writer for CodaBench packaging smoke tests.
- [X] Implement a Subtask 1 Hugging Face downloader for CSVs, labels, and image rasters.
- [X] Keep `README.md`, `REMOTE_PROVIDER.md`, notebooks, and this plan aligned after latest local tooling changes.

### Claude

- [ ] Subtask 1 today: provide one concise leaderboard-improvement memo focused on AgriPotential:
  - [X] Which low-risk non-neural moves are most likely to improve Accuracy +/- 1 today?
  - [X] Whether ordinal rounding/calibration or spatial smoothing is defensible for suitability masks.
  - [X] Whether the official AgriPotential examples imply any preprocessing, normalization, nodata handling, or band/time ordering we are missing.
  - [X] Keep recommendations implementable by Codex in under 2 hours.
  - Memo: `claude_handoffs/subtask1_leaderboard_memo_20260505.md`.
- [X] Verify DACIA5 file-name label interpretation from examples like `patch_20240716_9748_3.tif`; confirm which token is crop label and whether `9748`/`3017` are field or parcel ids.
- [ ] Confirm Sentinel-2 band order for the 12-band patch TIFFs so Codex can safely add NDVI/NDWI/red-edge features.
- [X] Find or infer expected Subtask 2 prediction artifact format from ImageCLEF/DACIA5 materials:
  - notebook-only evaluation,
  - CSV prediction file,
  - or zipped source plus report.
- [X] Review `results/subtask2/inspection/subtask2_baseline_summary.json` and recommend whether the leakage-free tabular baseline is acceptable for the first report/notebook pass.
- [X] Provide one compact Subtask 2 neural baseline recommendation only if it can realistically improve on:
  - Problem 1 HGB `Q=0.6655`
  - Problem 2 ExtraTrees `Q=0.8102`
- [X] For Subtask 1, verify whether official package examples include a direct raster download command that includes `test.csv`.
  - Repo downloader `scripts/download_subtask1_hf.py` is the current canonical path and includes `test.csv`.
  - Detailed Phase 1 findings are in `claude_handoffs/findings_phase1.md`.

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

Priority: parked while Subtask 1 leaderboard work is active.

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

- [X] Confirm Subtask 2 submission artifact expectations.
- [ ] Confirm Sentinel-2 band order before vegetation indices.
- [X] Decide whether current tabular baseline is enough for the first notebook/report pass or whether to run a neural attempt.

### Phase 3: Subtask 1 Valid Baseline

Priority: active leaderboard-improvement loop.

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
- [X] Full sampled-pixel baseline training/inference/submission:
  - Status: submitted to CodaBench.
  ```bash
  python scripts/subtask1_baseline.py train --data-dir data/subtask1
  ```
  - CodaBench score: `39.74`.
  - Improvement over constant baseline `39.52`: `+0.22`.
- [ ] Review local/remote full-run metrics if available:
  - [ ] Capture exact accuracy, Accuracy +/- 1, MAE, label counts, confusion matrix, model path, metrics path.
  - [ ] Confirm validation covers more than the smoke-run classes `0` and `1`.
  - [ ] Use the metrics to decide whether the optimized candidate deserves a CodaBench submission.
- [X] Implement constant test inference writer for `800` PNG masks.
- [X] Implement model-based test inference writer for `800` PNG masks.
- [X] Validate constant candidate ZIP with `scripts/validate_submission_zip.py`.
- [X] Infer model-based ZIP:
  ```bash
  python scripts/subtask1_baseline.py infer --data-dir data/subtask1
  ```
- [X] Validate model-based ZIP:
  ```bash
  python scripts/validate_submission_zip.py \
    --zip-path results/subtask1/submissions/subtask1_baseline.zip \
    --subtask1-codabench \
    --expected-ids-file data/subtask1/test.csv \
    --check-class-values
  ```
- [X] VB submits `results/subtask1/submissions/subtask1_baseline.zip` and records score/errors:
  - score: `39.74`
- [ ] Pull metrics/submission locally if not already synced.

### Phase 4: Model Improvement

Active for Subtask 1 because it has leaderboard feedback.

- [X] Add Subtask 1 class-balanced sampling.
- [X] Add overnight Subtask 1 experiment runner for HGB/ExtraTrees, uniform/class-balanced sampling, raw/raw-temporal features, and larger pixel budgets.
- [X] Run overnight Subtask 1 experiment suite on RunPod and inspect ranked validation log.
- [X] Submit `hgb_uniform_temporal_200k_s43` candidate:
  - ZIP: `results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip`
  - validation return code: `0`
- [ ] Next targeted candidate:
  - [ ] Stay near the winning setup: HGB, uniform sampling, raw-temporal features.
  - [X] Add targeted suite with larger pixel budgets and multiple seeds before switching model family.
  - [ ] Run targeted suite on RunPod and submit only if the best ZIP validates and metrics are plausible.
- [ ] Add simple spatial smoothing or class-prior calibration only after a valid optimized ZIP exists.
- [ ] Try Subtask 1 ensemble or lightweight neural model only if the pixel baseline pipeline is stable.
- [ ] Tune Subtask 2 tabular models after Subtask 1 leaderboard loop has a stronger candidate or stalls.

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

Run the targeted Subtask 1 follow-up suite:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/run_subtask1_experiments.py \
  --data-dir data/subtask1 \
  --suite targeted \
  --infer-best \
  --validate-best
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

### 2026-05-05

- Full TinyViT run completed on L40S:
  - Run id: `l40s_tiny_vit_summary_soft_full_e30_s52`.
  - Command: `source .venv/bin/activate && python scripts/run_subtask1_vision.py train --data-dir data/subtask1 --run-id l40s_tiny_vit_summary_soft_full_e30_s52 --model tiny_vit --temporal-mode summary --epochs 30 --batch-size 8 --patience 6 --visual-limit 20 --loss soft_ce --median-size 3 --seed 52 --num-workers 4 --write-test-visuals --test-visual-limit 20`.
  - Scope: full `train.csv` and full `val.csv`; no train or validation patch limit.
  - Best epoch `6`; full-val Accuracy +/- 1 `0.76609`, exact `0.46752`, MAE `0.93469`.
  - CodaBench score: `50.63`, current submitted floor.
  - Per-class recall: class 0 `0.7391`, class 1 `0.2301`, class 2 `0.0438`, class 3 `0.5843`, class 4 `0.0245`.
  - Pulled local artifacts include checkpoint/metrics, validation probabilities, visual panels, and `results/subtask1/submissions/l40s_tiny_vit_summary_soft_full_e30_s52.zip`.
  - Interpretation: useful class-3-heavy transformer ensemble member, but class 4 recall is too weak to treat as an automatic standalone submission.
- Subtask 1 declared active priority because CodaBench leaderboard feedback is immediate and current model score `39.74` only slightly improves on constant baseline `39.52`.
- Replacement RunPod strategy documented with two migration modes:
  - Mode A: reuse existing `/workspace` volume and verify `data/subtask1`.
  - Mode B: redownload Subtask 1 and smoke-read images/labels before training.
- Today strategy set: run the overnight Subtask 1 experiment suite, validate the best inferred ZIP, and submit only one plausible improvement candidate first.
- VB handoff updated for pod setup, migration-mode choice, experiment start, and submission gate.
- Claude handoff updated to focus on Subtask 1 low-risk leaderboard improvements implementable by Codex in under 2 hours.
- Subtask 2 remains parked except for background research because it lacks immediate leaderboard feedback.
- Overnight Subtask 1 experiment suite finished successfully:
  - `hgb_uniform_temporal_200k_s43`: Accuracy +/- 1 `0.72604`, exact `0.5524`, MAE `0.97296`.
  - `extra_cb_temporal_150k_s46`: Accuracy +/- 1 `0.68595`, exact `0.40253`, MAE `1.09979`.
  - `hgb_cb_temporal_400k_s45`: Accuracy +/- 1 `0.68396`, exact `0.38606`, MAE `1.13622`.
  - uniform sampling was the strongest validation signal.
- Best overnight ZIP generated and validated successfully:
  - `results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip`
  - inference return code `0`, validation return code `0`.

### 2026-05-04

- Strategy set: valid baselines first; use RunPod for data-heavy work; prioritize Subtask 2 fast iteration while keeping Subtask 1 packaging path open.
- RunPod selected after Lambda billing setup was blocked.
- RunPod Pod launched and verified with CUDA.
- Subtask 1 CodaBench ZIP format confirmed from VB handoffs.
- Claude completed Phase 0 research on AgriPotential, DACIA5, and fast baseline options.
- Added validators, inspection scripts, remote sync/exec/bootstrap/status helpers, and Subtask 2 download/extract helpers.
- Subtask 1 metadata inspection confirmed `6329/781/800` train/val/test patches.
- Subtask 1 constant class `2` ZIP submitted to CodaBench and scored `39.52`.
- Subtask 1 sampled-pixel baseline ZIP submitted to CodaBench and scored `39.74`.
- CodaBench limits confirmed: `10` daily submissions, `100` total submissions, immediate scoring.
- Subtask 1 full RunPod data downloaded under `/workspace/ai4agri/data/subtask1`; reported disk usage `185G`.
- Subtask 2 data downloaded, extracted, inspected, and pulled locally.
- Subtask 2 patch TIFF counts confirmed: problem 1 train/test `5436/1017`; problem 2 train/test `1176/1073`.
- Subtask 2 APIA-code labels confirmed from `Legend_crops.pdf`; first leakage-free tabular baselines trained.

## Open Questions

- [X] What are the Subtask 1 CodaBench submission limits and evaluation timing?
- [X] Is RunPod global networking enabled?
- [ ] Did the replacement RunPod attach the existing `/workspace` volume, or do we need Mode B redownload?
- [ ] Are Subtask 2 test labels hidden, or is this primarily notebook/report evaluation?
- [X] What is the exact Subtask 2 prediction/submission artifact format?
- [ ] What is the confirmed Sentinel-2 band order for DACIA5 12-band patch TIFFs?
- [X] What is the confirmed label token in DACIA5 patch filenames?
