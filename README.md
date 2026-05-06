# AI4Agri - ImageCLEF 2026

Competition entry for [ImageCLEF 2026 AI4Agri](https://www.imageclef.org/2026/ai4agri).

## Tasks

### Subtask 1: AgriPotential

Predict grapevine cultivation suitability from multi-temporal Sentinel-2 imagery.

- Input: 34 Sentinel-2 timeframes from 2017-2019, 10 bands, 5 m resolution
- Output: 5-class ordinal mask per test patch (classes 0–4 in model space, submitted as raw labels 1–5)
- Metric: Accuracy +/- 1
- Data: Hugging Face `m-sakka/agripotential`
- Submission: CodaBench ZIP with root-level PNG masks named by `test.csv` `patch_id`

**Label convention**: raw `viticulture.tif` values are 0=nodata, 1–5=Very Low to Very High. The pipeline
maps raw 1–5 → model classes 0–4 at load time and writes raw 1–5 back into submission PNGs via
`--submission-label-offset 1`. Nodata (raw 0) is excluded from training and scored as ignore index 255.

### Subtask 2: DACIA5

Classify crop types from Sentinel-2 optical and Sentinel-1 SAR time series near Brasov, Romania.

- Challenge 1: train on 2020-2023, evaluate 7 crop types for 2024
- Challenge 2: classify winter wheat vs alfalfa using March imagery only
- Metric: `Q = 0.5 * OA + 0.5 * AA`
- Data: Zenodo `14283243`
- Submission material: Colab notebook or zipped source folder with README, plus max 3-page technical report

## Current Status

- Branch: `main`
- Subtask 1 constant baseline submitted to CodaBench: `39.52`
- Subtask 1 sampled-pixel baseline submitted: `39.74`
- Subtask 1 overnight uniform raw-temporal HGB submitted: `40.16`
- Subtask 1 L40S ResNet/FPN submitted: `47.6`
- Subtask 1 TinyViT full-data (pre-fix) submitted: `50.63` — current CodaBench floor
- Corrected-label U-Net runs in progress on RunPod (seasonal and concat temporal modes); label bug confirmed fixed in `src/ai4agri/subtask1/data.py`
- Subtask 2 data is downloaded and inspected; leakage-free tabular baselines are complete but parked while Subtask 1 leaderboard work is active

**Critical label fix (2026-05-06)**: the old pipeline included raw label 0 (nodata) as training class 0
and excluded raw label 5 (Very High) entirely. `data.py:remap_raw_labels()` has always been correct;
the bug was in older notebooks and `subtask1_baseline.py`. All active vision runs use the fixed mapping
via `AgriPotentialVisionDataset`. Training now covers 7.45M labeled pixels (vs ~3.8M before the fix).

## Operating Docs

- [`CHATGPT_PLAN.md`](CHATGPT_PLAN.md): active task tracker, phase plan, and decision log
- [`ARCHITECTURE.md`](ARCHITECTURE.md): repository, pipeline, local/remote, and artifact architecture
- [`REMOTE_PROVIDER.md`](REMOTE_PROVIDER.md): RunPod migration plan, current pod template, and operating commands
- [`HANDOFF_STRATEGY.md`](HANDOFF_STRATEGY.md): ownership rules for VB, Codex, and Claude
- [`Next.md`](Next.md): lightweight working checklist and VB-facing notes
- [`notebooks/NOTEBOOK_FINDINGS.md`](notebooks/NOTEBOOK_FINDINGS.md): per-notebook discoveries, including label offset bug documentation

## VB Operator Notes

Use [`Next.md`](Next.md) as the current operating sheet. The active CodaBench floor is `50.63` from TinyViT full-data.

Before spending a CodaBench submission:

- Confirm the remaining daily/total submission budget.
- Run `scripts/review_subtask1_candidate.py --run-id <run_id> --data-dir data/subtask1`.
- Visually review `results/subtask1/visuals/<run_id>/` or open `notebooks/11_subtask1_visual_review.ipynb`.
- Use `notebooks/13_run_analysis.ipynb` to compare epoch curves and per-class recall across runs.
- Submit only if the candidate is plausibly better than `50.63`.
- Record the CodaBench score immediately in `Next.md` and `CHATGPT_PLAN.md`.

Verify submission PNGs contain raw labels 1–5 (not model-space 0–4) before uploading:

```bash
python scripts/review_subtask1_candidate.py --run-id <run_id> --data-dir data/subtask1
```

If no training or inference is active, stop idle RunPod pods.

## Repository Map

```text
data/              # Raw competition data; gitignored
notebooks/         # Exploratory test beds; not workflow runners
results/           # Inspections tracked; bulky model/features/submissions ignored
scripts/           # Operational download, inspect, train, infer, validate, and sync scripts
src/               # ai4agri Python package: data loading, models, metrics, visualize
claude_handoffs/   # Claude research prompts and findings
vb_handoffs/       # VB external-system notes and handoffs
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

For the optional AgriPotential package:

```bash
python -m pip install git+https://github.com/MohammadElSakka/agripotential
```

Copy the local environment template when remote helpers are needed:

```bash
cp .env.example .env
```

Do not commit `.env`.

## Notebook Policy

Notebooks are test beds for showing data shape, inspection artifacts, visualizations, and model outputs. Scripts own the workflow steps: download, inspect, feature extraction, training, inference, validation, and packaging.

Key notebooks:

| Notebook | Purpose |
|---|---|
| `01_eda_subtask1.ipynb` | Raw label distribution, band profiles, NDVI |
| `02_pixel_baseline_subtask1.ipynb` | Sampled-pixel HGB baseline |
| `03_unet_subtask1.ipynb` | Minimal U-Net training loop |
| `06_advanced_features.ipynb` | Per-patch NDVI profile cache and clustering |
| `11_subtask1_visual_review.ipynb` | Load saved vision run artifacts; gate submission decisions |
| `13_run_analysis.ipynb` | Training curves, per-class recall, all-runs comparison table |

Use the configured aliases to keep notebooks paired and synced:

```bash
nbpair notebooks/subtask1_testbed.ipynb notebooks/subtask2_testbed.ipynb
nbsync notebooks/subtask1_testbed.ipynb notebooks/subtask2_testbed.ipynb
nbopen notebooks/subtask1_testbed.ipynb
nbrun notebooks/subtask1_testbed.ipynb
```

## Common Commands

Push local scripts/docs to RunPod:

```bash
scripts/configure_runpod_env.sh --host NEW_HOST --port NEW_PORT --pod-id NEW_POD_ID
scripts/runpod_install_rsync.sh
scripts/runpod_sync.sh push
```

Run a remote status check:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Pull remote results (excludes checkpoints and notebook checkpoints):

```bash
scripts/runpod_sync.sh pull-results
```

Inspect Subtask 1 metadata or raster windows:

```bash
python scripts/inspect_subtask1.py --data-dir data/subtask1 --splits train val test
python scripts/inspect_subtask1.py --data-dir data/subtask1 --splits train val test --limit 1 --read-pixels --read-labels
```

Train and infer the Subtask 1 vision pipeline on RunPod:

```bash
# Train a U-Net with seasonal temporal aggregation
python scripts/run_subtask1_vision.py train \
  --data-dir data/subtask1 \
  --run-id my_run \
  --model unet \
  --temporal-mode seasonal \
  --epochs 30 \
  --loss pm1_bce \
  --decode neighbor_sum_sigmoid \
  --median-size 5

# Infer and package a submission ZIP (writes raw labels 1–5)
python scripts/run_subtask1_vision.py infer \
  --data-dir data/subtask1 \
  --run-id my_run \
  --checkpoint results/subtask1/vision_runs/my_run/best.pt

# Review before submission
python scripts/review_subtask1_candidate.py \
  --run-id my_run \
  --data-dir data/subtask1

# Validate the ZIP independently
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/my_run.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

Run the Subtask 2 tabular baseline workflow:

```bash
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/inspect_subtask2_labels.py --data-dir data/subtask2
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2 --label-mode apia-code
python scripts/subtask2_baseline.py features
python scripts/subtask2_baseline.py label-features
python scripts/subtask2_baseline.py train --problem problem1
python scripts/subtask2_baseline.py train --problem problem2
```

## Claude Handoffs

Use [`claude_handoffs/phase0.md`](claude_handoffs/phase0.md) and [`claude_handoffs/phase1.md`](claude_handoffs/phase1.md) to split research work while Codex continues implementation. Completed findings are tracked in [`claude_handoffs/findings_phase0.md`](claude_handoffs/findings_phase0.md) and [`claude_handoffs/findings_phase1.md`](claude_handoffs/findings_phase1.md):

1. Confirm CodaBench submission format.
2. Summarize AgriPotential loader and smoke-test usage.
3. Summarize DACIA5 data structure, labels, and split logic.
4. Recommend fast baseline approaches for both subtasks.
5. Confirm Subtask 2 deliverable format and review the leakage-free tabular baseline.
