# Remote Provider

Last updated: 2026-05-04

## Current State

```text
Provider: RunPod
Pod ID: vit08hc86csllk
Cloud: Secure cloud
Location: EU-RO-1
Global networking: off
Template: runpod-torch-v240
GPU: 1x RTX PRO 4500
vCPU: 28
RAM: 62 GB listed
Container disk: 20 GB
Volume: 450 GB mounted at /workspace
Price: $0.71/hr total
Budget ceiling: $75
JupyterLab: https://vit08hc86csllk-8888.proxy.runpod.net/lab
Direct SSH: ssh root@213.173.107.6 -p 34365 -i ~/.ssh/id_ed25519
Project: /workspace/ai4agri
Data: /workspace/ai4agri/data
Results: /workspace/ai4agri/results
```

## Verified

- SSH from local Mac to RunPod works.
- JupyterLab URL is available.
- GitHub SSH auth from the Pod works for `vb2317`.
- Repo files are present at `/workspace/ai4agri`.
- PyTorch CUDA works: `torch==2.4.1+cu124`, `torch.cuda.is_available() == True`.
- Public internet downloads worked even with global networking off.
- Subtask 1 full data is present at `/workspace/ai4agri/data/subtask1`; reported size is `185G`.
- Subtask 2 data is downloaded, extracted, inspected, and feature/baseline artifacts exist under `/workspace/ai4agri/results/subtask2`.

## Pending

- Keep the Pod running only while Subtask 1 training/inference is active.
- When full Subtask 1 training finishes, run inference, validate the ZIP, and pull results locally.
- Stop the Pod when idle after metrics and submission candidates have been synced back.

## Local Commands

Push current scripts/docs to RunPod:

```bash
scripts/runpod_sync.sh push
```

Run a command on RunPod:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Pull all remote results:

```bash
scripts/runpod_sync.sh pull-results
```

Pull only inspection outputs:

```bash
scripts/runpod_sync.sh pull-inspection
```

If local macOS lacks `rsync`:

```bash
brew install rsync
```

If the Pod lacks `rsync`:

```bash
apt-get update
apt-get install -y rsync
```

## RunPod Commands

```bash
cd /workspace/ai4agri
source .venv/bin/activate
bash scripts/runpod_status.sh
```

Subtask 1 model ZIP path after inference:

```bash
python scripts/subtask1_baseline.py infer --data-dir data/subtask1
python scripts/validate_submission_zip.py \
  --zip-path results/subtask1/submissions/subtask1_baseline.zip \
  --subtask1-codabench \
  --expected-ids-file data/subtask1/test.csv \
  --check-class-values
```

Overnight Subtask 1 experiment suite:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
mkdir -p results/subtask1/experiments
nohup python scripts/run_subtask1_experiments.py \
  --data-dir data/subtask1 \
  --suite overnight \
  --infer-best \
  --validate-best \
  > results/subtask1/experiments/overnight.log 2>&1 &
```

## Local `.env`

Do not commit `.env`.

```text
AI4AGRI_REMOTE_HOST=213.173.107.6
AI4AGRI_REMOTE_USER=root
AI4AGRI_REMOTE_PROJECT_DIR=/workspace/ai4agri
AI4AGRI_DATA_DIR=/workspace/ai4agri/data
AI4AGRI_RESULTS_DIR=/workspace/ai4agri/results
RUNPOD_SSH_PORT=34365
```

## Rules

- Keep all project files, data, and results under `/workspace/ai4agri`.
- Do not use the 20 GB container disk for raw data or generated features.
- Avoid duplicate Subtask 1 raw-data copies; the 450 GB volume is usable but tight.
- Sync results back before deleting the Pod or volume.
