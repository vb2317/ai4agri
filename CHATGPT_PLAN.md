# AI4Agri Competition Execution Plan

Last updated: 2026-05-04

## Goal

Produce valid, reproducible submissions for AI4Agri 2026 with the fastest possible feedback loop before the May 7, 2026 competition deadline, then prepare the May 28 notebook/report materials.

This plan is intentionally operational. Expect it to change as we learn:

- Whether registration and CodaBench access are fully working.
- How quickly the 200GB AgriPotential data can be read remotely.
- Which baseline gets a valid leaderboard score first.
- Whether Subtask 2 validation splits correlate with expected test performance.

## Roles

### VB

Owns external accounts, credentials, final submissions, and choices that require judgment outside the repo.

### Codex

Owns local repo implementation, scripts, packaging, validation checks, and this plan. Codex should create runnable code and update docs as experiments settle.

### Claude

Owns parallel research and experiment support. Claude should work from explicit handoff prompts and return concise findings, candidate commands, or patch suggestions. Claude should not be asked to make final submission decisions unless VB explicitly delegates that.

## Execution Venues

### Local

Use for repo editing, lightweight tests, submission packaging, result inspection, and report/notebook cleanup.

Do not depend on local storage for the full Subtask 1 dataset.

### Remote

Use for data download, feature extraction, training, inference, and any job that needs large disk or GPU.

Recommended minimum remote machine:

- 300-500GB SSD for Subtask 1.
- 32-64GB RAM.
- 1 GPU if training CNN/U-Net/temporal models; CPU is acceptable for feature extraction and boosted trees.

Good candidates: RunPod, Vast.ai, Lambda Labs, Paperspace, AWS, GCP, Azure, Colab Pro, or Kaggle notebooks.

## Operating Rules

1. Get a valid baseline submission before chasing model quality.
2. Prefer fast tabular baselines until full data loading is proven.
3. Save intermediate features so expensive imagery reads are not repeated.
4. Track every run with enough metadata to reproduce it.
5. Keep remote commands copy-pasteable from this repo.
6. Update this file whenever the active strategy changes.
7. Do not commit raw data, generated model weights, or large feature matrices unless explicitly intended.

## Phase 0: Access And Environment

### VB / Local

- [X] Confirm ImageCLEF/CLEF registration status.
- [X] Confirm CodaBench access for Subtask 1.
- [X] Confirm Subtask 1 CodaBench file naming rules and ZIP structure.
- [ ] Confirm Subtask 1 CodaBench submission limits and evaluation timing.
- [ ] Create or confirm Lambda Cloud account for remote compute.
- [ ] Launch recommended Lambda Cloud 1x NVIDIA A10 instance, or report capacity/quota blocker.
- [ ] Confirm budget ceiling; Codex recommends $75 for the initial deadline push unless VB chooses otherwise.
- [ ] Share only necessary access tokens through secure local environment variables, not committed files.

### Codex / Local

- [X] Add `.env.example` if scripts need environment variables.
- [X] Add `scripts/` or `src/common/` helpers if needed for reproducible setup.
- [X] Add a `runs/` or `results/runs.csv` convention for experiment tracking.
- [X] Create validation scripts for prediction file shape, class range, and ZIP structure.
- [X] Keep `README.md`, `Next.md`, and this plan aligned as decisions change.
- [X] Research remote compute providers and document VB subscription/setup instructions.

### Claude / Local Or Remote Research

- [X] Review official CodaBench instructions and summarize required output file names and ZIP layout.
- [ ] Review AgriPotential package examples and summarize the fastest way to stream or download data. Prompt tightened in `claude_handoffs/phase0.md`.
- [ ] Review DACIA5 file structure from Zenodo documentation and summarize labels, splits, and expected prediction format. Prompt tightened in `claude_handoffs/phase0.md`.
- [ ] Produce fast baseline recommendation memo for both subtasks. Prompt added in `claude_handoffs/phase0.md`.

## Phase 1: Data Acquisition

### VB / Remote

- [ ] Start Subtask 1 data access on the Lambda A10 remote machine with enough disk.
- [ ] Start Subtask 2 Zenodo download locally or remotely.
- [ ] Record exact data source URLs, download commands, and local paths.
- [ ] Confirm checksums or file counts where available.

### Codex / Local

- [ ] Create data inspection scripts:
  - [ ] Subtask 1: list patches, tensor shapes, label shapes, class distribution.
  - [ ] Subtask 2: list files, patch shapes, crop labels, year/month metadata.
- [ ] Make scripts accept `--data-dir` and `--out-dir` so they work on remote and local paths.
- [ ] Add small smoke-test mode: `--limit N`.

### Codex / Remote

- [ ] Run inspection scripts on actual data.
- [ ] Save inspection outputs under `results/subtask*/inspection/`.
- [ ] Bring small metadata outputs back to local repo.

### Claude / Parallel

- [ ] Identify any known baseline notebooks, papers, or package tutorials for AgriPotential.
- [ ] Identify strong DACIA5 feature baselines from crop classification literature that are implementable within one day.
- [ ] Return a short ranked list of feature sets and model choices.

## Phase 2: Subtask 2 Fast Baseline

Subtask 2 is smaller and should produce useful results quickly. Prioritize it for an early complete pipeline.

### Codex / Local

- [ ] Implement dataset loader for DACIA5 patches.
- [ ] Implement deterministic train/validation split:
  - [ ] Challenge 1: train on 2020-2022 or 2020-2023 depending available labels, validate on a held-out year.
  - [ ] Challenge 2: validate March-only winter wheat vs alfalfa with a year-aware split.
- [ ] Implement feature extraction:
  - [ ] Per-band mean and standard deviation.
  - [ ] Per-band min, max, and selected percentiles.
  - [ ] NDVI, NDWI, red-edge indices where bands are available.
  - [ ] SAR VV/VH features if Sentinel-1 patches are available.
  - [ ] Temporal aggregates by month or acquisition index.
- [ ] Implement baseline models:
  - [ ] Logistic regression or linear SVM.
  - [ ] Random forest or extra trees.
  - [ ] Histogram gradient boosting.
  - [ ] Optional LightGBM/XGBoost/CatBoost if dependencies are acceptable.
- [ ] Implement metric calculation:
  - [ ] Overall accuracy.
  - [ ] Average class accuracy.
  - [ ] Q score for Challenge 1.
  - [ ] Balanced two-class score for Challenge 2.

### Codex / Remote

- [ ] Run full feature extraction.
- [ ] Train baseline models.
- [ ] Save predictions, confusion matrices, metrics, and model metadata.
- [ ] Export candidate submission artifacts.

### Claude / Parallel

- [ ] Propose a compact neural baseline for Subtask 2:
  - [ ] Patch CNN over spatial dimensions.
  - [ ] Temporal pooling or small GRU/Transformer.
  - [ ] Class-balanced loss.
- [ ] Estimate implementation risk and runtime.
- [ ] If useful, draft model architecture in pseudocode for Codex to implement.

### VB / Local

- [ ] Review validation scores and confusion matrices.
- [ ] Choose whether to spend time on neural Subtask 2 models or freeze tabular baseline.
- [ ] Preserve best generated artifacts in `results/subtask2/`.

## Phase 3: Subtask 1 Valid Baseline

Subtask 1 has a large dataset and CodaBench feedback, so the first objective is a valid upload.

### Codex / Local

- [ ] Implement or adapt AgriPotential loader smoke test.
- [ ] Implement sampled training pipeline:
  - [ ] Sample pixels from training patches.
  - [ ] Extract temporal summary features.
  - [ ] Train ordinal-aware baseline.
- [ ] Implement metrics:
  - [ ] Exact accuracy.
  - [ ] Accuracy within +/- 1 class.
  - [ ] Mean absolute class error.
- [ ] Implement inference writer matching CodaBench format.
- [ ] Implement ZIP packaging validator.

### Codex / Remote

- [ ] Run data smoke test.
- [ ] Train sampled baseline.
- [ ] Run validation inference.
- [ ] Run test inference.
- [ ] Package first valid CodaBench ZIP.
- [ ] Copy submission ZIP and run metadata to local `results/subtask1/submissions/`.

### Claude / Parallel

- [ ] Verify output format from CodaBench instructions.
- [ ] Search for AgriPotential baseline code in the official package/tutorial.
- [ ] Suggest ordinal modeling options that are low risk:
  - [ ] Regression rounded to class.
  - [ ] Classifier with ordinal post-processing.
  - [ ] CORAL-style ordinal head only if time allows.

### VB / Local

- [ ] Submit first valid Subtask 1 ZIP to CodaBench.
- [ ] Record leaderboard/private feedback if available.
- [ ] Share score and any submission errors back into this plan.

## Phase 4: Model Improvement

Only start this after a valid baseline exists for the relevant subtask.

### Subtask 1 Improvements

#### Codex / Remote

- [ ] Increase sampled pixel count.
- [ ] Add class-balanced sampling.
- [ ] Add spatial context features from small windows if cheap.
- [ ] Try lightweight CNN/U-Net on patch tensors if data pipeline is stable.
- [ ] Try temporal frame selection or seasonal aggregation to reduce memory.
- [ ] Ensemble top 2-3 baselines by median/rounded average class.

#### Claude / Parallel

- [ ] Review validation errors and propose targeted fixes.
- [ ] Suggest augmentation strategy for Sentinel-2 time series that avoids label leakage.

### Subtask 2 Improvements

#### Codex / Remote

- [ ] Tune boosted-tree hyperparameters.
- [ ] Use class weights or balanced sampling for Q metric.
- [ ] Try model ensembling across feature sets.
- [ ] Add neural baseline only if tabular models plateau.

#### Claude / Parallel

- [ ] Review class confusion and suggest feature additions by crop phenology.
- [ ] Suggest a compact ablation table for the final report.

### VB / Local

- [ ] Decide when to freeze each subtask.
- [ ] Submit improved candidates only when validation or sanity checks justify it.

## Phase 5: Packaging And Report

### Codex / Local

- [ ] Create final reproducible notebook for Subtask 2.
- [ ] Ensure notebook works from clean environment or Colab.
- [ ] Write or scaffold 3-page report:
  - [ ] Data preprocessing.
  - [ ] Model description.
  - [ ] Validation protocol.
  - [ ] Results table.
  - [ ] Limitations.
- [ ] Add commands to reproduce final predictions.

### Claude / Parallel

- [ ] Draft report prose from final experiment notes.
- [ ] Check report for missing methodological details.
- [ ] Suggest concise figure/table captions.

### VB / Local

- [ ] Review final notebook/report.
- [ ] Submit materials by May 28, 2026.

## Two-Agent Handoff Pattern

Use this pattern when assigning work to Claude while Codex continues implementation.

### Claude Handoff Template

```text
Project: AI4Agri 2026 repo.

Task:
[Specific research or implementation-support question.]

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

### Good Claude Tasks

- Verify CodaBench submission format.
- Summarize AgriPotential package usage.
- Find DACIA5 label/split details.
- Propose compact feature sets for crop classification.
- Draft report text after final metrics exist.

### Good Codex Tasks

- Implement loaders and validators.
- Write training and inference scripts.
- Package submissions.
- Run local smoke tests.
- Update repo documentation.

## Remote Command Checklist

Prepare these once scripts exist.

- [ ] Environment setup command.
- [ ] Data download command.
- [ ] Data inspection command.
- [ ] Feature extraction command.
- [ ] Train command.
- [ ] Inference command.
- [ ] Package submission command.
- [ ] Result sync command.

## Daily Decision Log

### 2026-05-04

- Current repo contains scaffolding only.
- No data, code, notebooks, or results are present yet.
- Strategy: get valid baselines first; use remote resources for data-heavy work; prioritize Subtask 2 quick iteration and Subtask 1 valid CodaBench upload.
- VB added logged-in ImageCLEF/CodaBench handoffs under `vb_handoffs/`.
- Confirmed Subtask 1 CodaBench format: ZIP root contains PNG masks named `<patch_id>.png` for `test.csv`; target count is 800; values are integer classes `0..4`; optional method PDF must be `report.pdf`; extraneous files are ignored by scorer.
- Submission limits and evaluation timing remain unconfirmed.
- Codex Phase 0 local scaffolding is complete: `.env.example`, `results/runs.csv`, `scripts/validate_submission_zip.py`, `scripts/README.md`, Claude handoff prompts, README updates, and handoff strategy docs.
- Remote provider recommendation documented in `REMOTE_PROVIDER.md`: use Lambda Cloud 1x NVIDIA A10 by default; use RunPod as fallback if Lambda capacity/quota blocks launch. Recommended initial budget ceiling is $75.

## Open Questions

- [ ] Is ImageCLEF registration complete despite the listed April 23 registration close date?
- [X] What is the exact CodaBench ZIP/file format for Subtask 1?
- [ ] What are the Subtask 1 CodaBench submission limits and evaluation timing?
- [ ] Are Subtask 2 test labels hidden, or is this primarily notebook/report evaluation?
- [X] Which remote provider will be used?
- [ ] What max budget will VB approve for remote jobs before May 7?
- [ ] Did Lambda Cloud have A10 capacity and account quota for launch?
- [ ] Should Subtask 1 or Subtask 2 be prioritized if time becomes constrained?
