# Remote Provider

Last updated: 2026-05-04

## Current RunPod

```text
Provider: RunPod
Pod ID: vit08hc86csllk
Cloud: Secure cloud
Template: runpod-torch-v240
GPU: 1x RTX PRO 4500
VRAM: 32,623 MiB observed
vCPU: 28
RAM: 62 GB listed; 251 Gi observed in container
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

Pending:

- Confirm whether RunPod global networking is enabled.
- Install remaining Python dependencies after `requirements.txt` sync.
- Start data acquisition/inspection after Claude returns loader/data-format details.

## Verified

- SSH to RunPod works.
- JupyterLab URL is available.
- GitHub SSH auth from the Pod works for `vb2317`.
- Repo files are present at `/workspace/ai4agri`.
- PyTorch works with CUDA:

```text
torch==2.4.1+cu124
torch.cuda.is_available() == True
```

- Submission validator works:

```bash
python3 scripts/validate_submission_zip.py --help
```

## Next Commands

From local Mac, push current repo scripts/docs to the Pod:

```bash
scripts/runpod_sync.sh push
```

Then bootstrap from local over SSH:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_bootstrap.sh'
```

Or run directly on the Pod:

```bash
cd /workspace/ai4agri
bash scripts/runpod_bootstrap.sh
```

Check Pod/data status any time:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

## Sync From Mac

Use this when local docs/scripts change:

```bash
scripts/runpod_sync.sh push
```

Pull remote results back:

```bash
scripts/runpod_sync.sh pull-results
```

Pull only inspection outputs:

```bash
scripts/runpod_sync.sh pull-inspection
```

If the Pod lacks `rsync`:

```bash
apt-get update
apt-get install -y rsync
```

The sync helper excludes `.git`, `.env`, `.venv`, `.DS_Store`, `data`, and submission ZIP directories by default.

## Data Management

Download Subtask 2 on the Pod:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
```

Inspect metadata/layout:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/inspect_subtask1.py --splits train val test
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
```

Watch disk and GPU state:

```bash
bash scripts/runpod_status.sh
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

- Keep all project/data/results under `/workspace/ai4agri`.
- Do not use the 20 GB container disk for data.
- Avoid duplicate Subtask 1 raw-data copies; 450 GB is usable but tight.
- Stop the Pod when not actively working.
- Sync results back before deleting the Pod or volume.
