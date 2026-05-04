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

On the Pod:

```bash
cd /workspace/ai4agri
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install git+https://github.com/MohammadElSakka/agripotential
```

Then verify:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
python scripts/validate_submission_zip.py --help
```

## Sync From Mac

Use this when local docs/scripts change:

```bash
rsync -rtv --no-owner --no-group --no-perms \
  --exclude .git \
  --exclude .DS_Store \
  --exclude data \
  --exclude results/subtask1/submissions \
  --exclude results/subtask2/submissions \
  -e "ssh -p 34365 -i ~/.ssh/id_ed25519" \
  ./ root@213.173.107.6:/workspace/ai4agri/
```

If the Pod lacks `rsync`:

```bash
apt-get update
apt-get install -y rsync
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
