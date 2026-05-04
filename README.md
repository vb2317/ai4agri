# AI4Agri — ImageCLEF 2026

Competition entry for [ImageCLEF 2026 AI4Agri](https://www.imageclef.org/2026/ai4agri).

## Tasks

### Subtask 1: AgriPotential (Viticulture)
Predict land suitability for grapevine cultivation from multi-temporal Sentinel-2 imagery.

- **Input:** 34 Sentinel-2 timeframes (2017–2019), 10 bands, 5m resolution
- **Output:** 5-class ordinal label per pixel (very low → very high suitability)
- **Metric:** Accuracy±1 (predictions within one class count as correct)
- **Data:** HuggingFace [`m-sakka/agripotential`](https://huggingface.co/datasets/m-sakka/agripotential) (~200GB)
- **Platform:** [CodaBench](https://www.codabench.org/competitions/12055/)

### Subtask 2: DACIA5 (Crop Identification)
Identify crop types from Sentinel-2 optical + Sentinel-1 SAR time series near Brașov, Romania.

**Challenge 1 — Past vs Present:** Train on 2020–2023, predict 7 crop types in 2024.
**Challenge 2 — Early Detection:** Classify winter wheat vs alfalfa using March imagery only.

- **Metric:** Q = 0.5×AA + 0.5×OA
- **Data:** [Zenodo 14283243](https://zenodo.org/records/14283243) (3.4GB)
- **Submit:** Colab notebook or zipped source + 3-page technical report

## Key Dates

| Milestone | Date |
|---|---|
| Submission deadline | May 7, 2026 |
| Notebook submission | May 28, 2026 |
| Conference | Sep 21–24, 2026 (Jena, Germany) |

## Structure

```
data/
  subtask1/       # AgriPotential patches (HuggingFace)
  subtask2/       # DACIA5 patches (Zenodo)
notebooks/
  subtask1_testbed.ipynb  # Exploration/test bed
  subtask2_testbed.ipynb
src/
  subtask1/       # Training and inference scripts
  subtask2/
results/
  subtask1/       # Submission ZIPs
  subtask2/       # Predictions + report
  runs.csv        # Experiment/run tracking
scripts/          # Operational utilities
claude_handoffs/  # Parallel research prompts for Claude
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

For Subtask 1 data:
```bash
python -m pip install git+https://github.com/MohammadElSakka/agripotential
```

`agripotential` is intentionally not listed as an installable package in `requirements.txt` because it is not published on PyPI. Install it from GitHub after the base requirements.

Copy the environment template before running local or remote jobs:

```bash
cp .env.example .env
```

Fill only the values needed for the current machine. Do not commit `.env`.

## Current Execution Plan

The detailed working plan is in [`CHATGPT_PLAN.md`](CHATGPT_PLAN.md). It separates tasks by:

- **VB:** registrations, account access, remote compute choices, final submissions
- **Codex:** repo implementation, scripts, validators, packaging, reproducibility
- **Claude:** parallel research handoffs for data formats, baseline ideas, and report support
- **Local vs remote:** local for code and packaging; remote for large data, feature extraction, training, and inference

Primary strategy:

1. Get valid baseline submissions before optimizing model quality.
2. Use remote resources for Subtask 1 because the dataset is ~200GB.
3. Prioritize Subtask 2 for fast iteration because the dataset is much smaller.
4. Save reusable features and track every meaningful run in `results/runs.csv`.
5. Update the plan as access, data format, validation scores, and submission feedback become clear.

The handoff operating model is in [`HANDOFF_STRATEGY.md`](HANDOFF_STRATEGY.md). Use it to decide what belongs with VB, Codex, or Claude, and when a task is blocked versus ready for implementation.

The remote compute recommendation and VB subscription instructions are in [`REMOTE_PROVIDER.md`](REMOTE_PROVIDER.md). Current default: RunPod On-Demand GPU Pod.

Current RunPod Pod recorded there: ID `vit08hc86csllk`, 1x RTX PRO 4500, 28 vCPU, 62GB RAM, `runpod-torch-v240`, 450GB `/workspace` volume, JupyterLab URL recorded, direct SSH recorded, total listed price $0.71/hr.

## Current Status

Current branch: `codex/phase1-inspection-scripts`.

Ready for VB:

- Submit Subtask 1 constant baseline ZIP: `results/subtask1/submissions/constant_class_2.zip`.
- This ZIP was generated from `test.csv`, contains `800` root-level PNG masks, matches expected patch ids, and passes class-value validation.

Implemented tooling:

- Subtask 1 CodaBench ZIP validator, including grayscale PNG value checks without requiring Pillow.
- Subtask 1 constant-mask ZIP writer.
- Subtask 1 Hugging Face downloader for CSVs, labels, and optional image rasters.
- Subtask 1 sampled-pixel train/inference baseline script.
- Subtask 2 data inspection, manifest, feature extraction, and tabular baseline scripts.
- RunPod sync/exec/bootstrap/status helpers.

Blocked or waiting:

- VB: confirm CodaBench submission limits and evaluation timing.
- VB: submit `results/subtask1/submissions/constant_class_2.zip` and report score/errors.
- VB/remote: confirm RunPod global networking status and run data-heavy commands there.
- Claude/VB: confirm DACIA5 label source and Sentinel-2 band order before training/enhancing Subtask 2.
- Codex remote run: train Subtask 1 sampled-pixel baseline once actual rasters are available.

## Notebooks

Keep notebooks as exploratory test beds, not workflow runners. Scripts own operational steps such as download, inspection refresh, manifest creation, feature extraction, training, validation, and packaging.

- [`notebooks/subtask1_testbed.ipynb`](notebooks/subtask1_testbed.ipynb): AgriPotential metadata summaries, patch geometry charts, existing inspection artifact review, and optional manual raster smoke view.
- [`notebooks/subtask2_testbed.ipynb`](notebooks/subtask2_testbed.ipynb): DACIA5 inspection artifact review, manifest/feature table summaries, date distributions, feature histograms, and optional patch visualization.

Notebook sync workflow:

```bash
source .venv/bin/activate
nbpair notebooks/subtask1_testbed.ipynb notebooks/subtask2_testbed.ipynb
nbsync notebooks/subtask1_testbed.ipynb notebooks/subtask2_testbed.ipynb
```

Use `nbopen` for interactive edits and `nbrun <notebook.ipynb>` for smoke execution when the needed local or RunPod data is available. Commit both the `.ipynb` and paired `.py` files. When a script changes a major artifact shape, update the matching notebook review cell in the same commit.

## Phase 0 Status

Phase 0 is about access and environment setup.

Already scaffolded in this repo:

- `.env.example` for local/remote configuration
- `results/runs.csv` for experiment tracking
- `scripts/validate_submission_zip.py` for configurable submission ZIP checks
- `scripts/README.md` for script conventions
- `claude_handoffs/phase0.md` for Claude research prompts

Confirmed from VB logged-in handoffs:

- Subtask 1 CodaBench expects one ZIP with root-level PNG masks.
- Each PNG must be named exactly as the corresponding `test.csv` `patch_id`.
- Target is all 800 test PNGs; fewer are accepted but hurt the score.
- PNG values must be integer class ids `0` through `4`.
- Optional method PDF must be named exactly `report.pdf` at ZIP root.

Still needs confirmation before Phase 1:

- CodaBench submission limits and evaluation timing
- RunPod global networking status
- Final data locations for Subtask 1 and Subtask 2

## Useful Commands

Push local repo scripts/docs to RunPod:

```bash
scripts/runpod_sync.sh push
```

Run a one-off command on RunPod:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Bootstrap the RunPod environment:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_bootstrap.sh'
```

Pull remote results back:

```bash
scripts/runpod_sync.sh pull-results
```

Inspect AgriPotential CSV metadata without downloading imagery:

```bash
python scripts/inspect_subtask1.py --splits train val test
```

Download AgriPotential CSVs and the viticulture label raster:

```bash
python scripts/download_subtask1_hf.py --out-dir data/subtask1 --skip-images
```

On a remote machine with local data, smoke-read one patch:

```bash
python scripts/inspect_subtask1.py \
  --data-dir data/subtask1/agripotential \
  --splits train val test \
  --limit 1 \
  --read-pixels \
  --read-labels
```

Inspect extracted DACIA5 data:

```bash
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
python scripts/inspect_subtask2.py \
  --data-dir data/subtask2 \
  --read-arrays
```

Train first DACIA5 tabular baselines on RunPod:

```bash
python scripts/train_subtask2_baseline.py --data-dir data/subtask2 --problem 1
python scripts/train_subtask2_baseline.py --data-dir data/subtask2 --problem 2
```

Validate a candidate Subtask 1 CodaBench ZIP once predictions exist:

```bash
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/example.zip \
  --subtask1-codabench \
  --check-class-values
```

Create a packaging-smoke baseline ZIP with constant class masks:

```bash
python scripts/create_subtask1_constant_zip.py
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/constant_class_2.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

Train and run the sampled-pixel Subtask 1 baseline once local rasters are available:

```bash
python scripts/subtask1_baseline.py train --data-dir data/subtask1
python scripts/subtask1_baseline.py infer --data-dir data/subtask1
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/subtask1_baseline.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

If `test.csv` is available, also verify the exact `patch_id` set:

```bash
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/example.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

## Claude Handoffs

Use [`claude_handoffs/phase0.md`](claude_handoffs/phase0.md) to split research work while Codex continues implementation. Completed Phase 0 findings are tracked in [`claude_handoffs/findings_phase0.md`](claude_handoffs/findings_phase0.md):

1. Confirm CodaBench submission format.
2. Summarize AgriPotential loader and smoke-test usage.
3. Summarize DACIA5 data structure, labels, and split logic.
4. Recommend fast baseline approaches for both subtasks.
