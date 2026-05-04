# AI4Agri - ImageCLEF 2026

Competition entry for [ImageCLEF 2026 AI4Agri](https://www.imageclef.org/2026/ai4agri).

## Tasks

### Subtask 1: AgriPotential

Predict grapevine cultivation suitability from multi-temporal Sentinel-2 imagery.

- Input: 34 Sentinel-2 timeframes from 2017-2019, 10 bands, 5 m resolution
- Output: 5-class ordinal mask per test patch
- Metric: Accuracy +/- 1
- Data: Hugging Face `m-sakka/agripotential`
- Submission: CodaBench ZIP with root-level PNG masks named by `test.csv` `patch_id`

### Subtask 2: DACIA5

Classify crop types from Sentinel-2 optical and Sentinel-1 SAR time series near Brasov, Romania.

- Challenge 1: train on 2020-2023, evaluate 7 crop types for 2024
- Challenge 2: classify winter wheat vs alfalfa using March imagery only
- Metric: `Q = 0.5 * OA + 0.5 * AA`
- Data: Zenodo `14283243`
- Submission material: final notebook/source plus technical report, exact artifact format still pending confirmation

## Current Status

- Branch: `main`
- Subtask 1 constant baseline was submitted to CodaBench and scored `39.52`.
- Subtask 1 full data is on RunPod under `/workspace/ai4agri/data/subtask1` and uses about `185G`.
- Subtask 1 sampled-pixel baseline ZIP was submitted to CodaBench and scored `39.74`.
- Subtask 1 next step is a quick improvement decision: rerun with the optimized baseline settings or move attention to Subtask 2 packaging/report work.
- Subtask 2 data is downloaded and inspected; leakage-free tabular baselines are complete and ready for packaging-format confirmation.

## Operating Docs

- [`CHATGPT_PLAN.md`](CHATGPT_PLAN.md): active task tracker, phase plan, and decision log.
- [`ARCHITECTURE.md`](ARCHITECTURE.md): repository, pipeline, local/remote, and artifact architecture.
- [`REMOTE_PROVIDER.md`](REMOTE_PROVIDER.md): current RunPod details and minimal operating commands.
- [`HANDOFF_STRATEGY.md`](HANDOFF_STRATEGY.md): ownership rules for VB, Codex, and Claude.
- [`Next.md`](Next.md): lightweight working checklist and VB-facing notes.

## Repository Map

```text
data/              # Raw competition data; gitignored
notebooks/         # Exploratory test beds; not workflow runners
results/           # Inspections tracked; bulky model/features/submissions ignored
scripts/           # Operational download, inspect, train, infer, validate, and sync scripts
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
scripts/runpod_sync.sh push
```

Run a remote status check:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Pull remote results:

```bash
scripts/runpod_sync.sh pull-results
```

Inspect Subtask 1 metadata or raster windows:

```bash
python scripts/inspect_subtask1.py --data-dir data/subtask1 --splits train val test
python scripts/inspect_subtask1.py --data-dir data/subtask1 --splits train val test --limit 1 --read-pixels --read-labels
```

Train and infer the Subtask 1 sampled-pixel baseline on RunPod:

```bash
python scripts/subtask1_baseline.py train --data-dir data/subtask1
python scripts/subtask1_baseline.py infer --data-dir data/subtask1
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/subtask1_baseline.zip \
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
