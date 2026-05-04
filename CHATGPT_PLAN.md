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
- [X] Create or confirm RunPod account for remote compute.
- [X] Launch recommended RunPod On-Demand GPU Pod, or report capacity/billing blocker.
- [X] Confirm budget ceiling; current ceiling is $75.
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
- [X] Review AgriPotential package examples and summarize the fastest way to stream or download data. Findings in `claude_handoffs/findings_phase0.md`.
- [X] Review DACIA5 file structure from Zenodo documentation and summarize labels, splits, and expected prediction format. Findings in `claude_handoffs/findings_phase0.md`.
- [X] Produce fast baseline recommendation memo for both subtasks. Findings in `claude_handoffs/findings_phase0.md`.

## Phase 1: Data Acquisition

### VB / Remote

- [ ] Start Subtask 1 data access on the RunPod remote machine with enough disk.
- [ ] Start Subtask 2 Zenodo download locally or remotely.
- [ ] Record exact data source URLs, download commands, and local paths.
- [ ] Confirm checksums or file counts where available.
- [ ] Send Codex RunPod global networking status from the Connect/details tab.
- [X] Place repo files on RunPod at `/workspace/ai4agri`.

### Codex / Local

- [X] Create data inspection scripts:
  - [X] Subtask 1: list patches, tensor shapes, label shapes, class distribution.
  - [X] Subtask 2: list files, patch shapes, crop labels, year/month metadata.
- [X] Make scripts accept `--data-dir` and `--out-dir` so they work on remote and local paths.
- [X] Add small smoke-test mode: `--limit N`.

### Codex / Remote

- [X] Run inspection scripts on actual data.
- [X] Save inspection outputs under `results/subtask*/inspection/`.
- [X] Bring small metadata outputs back to local repo.
- [X] Verify remote Python/PyTorch/CUDA environment and validator script.
- [X] Finish remote dependency install after latest `requirements.txt` sync.

### Claude / Parallel

- [X] Identify any known baseline notebooks, papers, or package tutorials for AgriPotential.
- [X] Identify strong DACIA5 feature baselines from crop classification literature that are implementable within one day.
- [X] Return a short ranked list of feature sets and model choices.

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

Use these as the current RunPod copy-paste baseline. Update this section when data paths or training scripts change.

- [X] Environment setup command:

```bash
scripts/runpod_sync.sh push
scripts/runpod_exec.sh 'bash scripts/runpod_bootstrap.sh'
```

- [ ] Data download command.

Subtask 1 needs the official AgriPotential package or direct Hugging Face dataset access. Start with metadata inspection before pulling all imagery.

Subtask 2 source file:

```bash
cd /workspace/ai4agri
mkdir -p data/subtask2
source .venv/bin/activate
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
```

- [X] Data inspection command:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/inspect_subtask1.py --splits train val test
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
```

- [ ] Feature extraction command.
- [ ] Train command.
- [ ] Inference command.
- [X] Package submission validation command:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/example.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

- [X] Result sync command:

```bash
scripts/runpod_sync.sh pull-results
```

## Daily Decision Log

### 2026-05-04

- Current repo contains scaffolding only.
- No data, code, notebooks, or results are present yet.
- Strategy: get valid baselines first; use remote resources for data-heavy work; prioritize Subtask 2 quick iteration and Subtask 1 valid CodaBench upload.
- VB added logged-in ImageCLEF/CodaBench handoffs under `vb_handoffs/`.
- Confirmed Subtask 1 CodaBench format: ZIP root contains PNG masks named `<patch_id>.png` for `test.csv`; target count is 800; values are integer classes `0..4`; optional method PDF must be `report.pdf`; extraneous files are ignored by scorer.
- Submission limits and evaluation timing remain unconfirmed.
- Codex Phase 0 local scaffolding is complete: `.env.example`, `results/runs.csv`, `scripts/validate_submission_zip.py`, `scripts/README.md`, Claude handoff prompts, README updates, and handoff strategy docs.
- Remote provider changed to RunPod after Lambda Cloud billing setup was blocked. Use a RunPod On-Demand GPU Pod with 500-750GB persistent volume. Recommended initial budget ceiling is $75.
- VB launched RunPod Pod: ID `vit08hc86csllk`, Secure cloud, 1x RTX PRO 4500, 28 vCPU, 62GB RAM, `runpod-torch-v240`, 20GB container disk, 450GB `/workspace` volume, JupyterLab at `https://vit08hc86csllk-8888.proxy.runpod.net/lab`, direct SSH `ssh root@213.173.107.6 -p 34365 -i ~/.ssh/id_ed25519`, total price $0.71/hr, budget ceiling $75.
- GitHub HTTPS clone from the Pod failed because password authentication is not supported. Use SSH clone with a GitHub deploy/account key, or rsync the repo from local over direct SSH.
- GitHub SSH from the Pod now authenticates successfully for `vb2317`. Prefer `git clone git@github.com:vb2317/ai4agri.git ai4agri`.
- Local-to-Pod `rsync` failed because `rsync` is not installed on the Pod. Install `rsync` on the Pod or use `scp` fallback.
- Repo files are now present on RunPod at `/workspace/ai4agri` after corrected sync/copy. Directory contains planning docs, scripts, notebooks, results, source folders, and handoff folders.
- RunPod environment check passed: `torch==2.4.1+cu124`, CUDA available, and `scripts/validate_submission_zip.py --help` works.
- `REMOTE_PROVIDER.md` was reduced to current RunPod state, next commands, sync command, local `.env`, and operating rules only.
- Claude Phase 0 research handoffs 2-4 are complete in `claude_handoffs/findings_phase0.md`.
- Added local/remote inspection scripts: `scripts/inspect_subtask1.py` and `scripts/inspect_subtask2.py`.
- Codex reviewed Claude's Phase 0 updates and syntax-checked all operational scripts with `py_compile`.
- Added RunPod operations scripts for sync, SSH execution, bootstrap, status checks, and Subtask 2 Zenodo download/extract.
- RunPod inspection scripts completed and wrote `results/subtask1/inspection/subtask1_inspection.json` and `results/subtask2/inspection/subtask2_inspection.json` on the remote machine.
- Pulled inspection JSONs back to local repo. Subtask 1 metadata is usable: 34 image rows, train/val/test counts 6329/781/800, and 128x128 patches. Subtask 2 inspection found `total_files: 0`, so the Zenodo archive still needs to be downloaded/extracted under `/workspace/ai4agri/data/subtask2` or the inspection command needs the corrected extracted path.

## Open Questions

- [ ] Is ImageCLEF registration complete despite the listed April 23 registration close date?
- [X] What is the exact CodaBench ZIP/file format for Subtask 1?
- [ ] What are the Subtask 1 CodaBench submission limits and evaluation timing?
- [ ] Are Subtask 2 test labels hidden, or is this primarily notebook/report evaluation?
- [X] Which remote provider will be used?
- [X] What max budget will VB approve for remote jobs before May 7?
- [X] Did RunPod SSH and Jupyter access work?
- [X] What are the RunPod Pod ID, cloud type/location, SSH command, and JupyterLab URL?
- [ ] Is RunPod global networking enabled?
- [ ] Should Subtask 1 or Subtask 2 be prioritized if time becomes constrained?
