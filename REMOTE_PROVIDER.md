# Remote Provider

Last updated: 2026-05-05

## RunPod Config Template

When a new pod is created, update local `.env` first. Do not hardcode pod host/port in scripts.

```bash
scripts/configure_runpod_env.sh \
  --host NEW_PUBLIC_SSH_HOST_OR_IP \
  --port NEW_PUBLIC_SSH_PORT \
  --pod-id NEW_POD_ID \
  --jupyter-url NEW_JUPYTER_LAB_URL
```

Then test connectivity:

```bash
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Install `rsync` on a fresh pod before using sync/pull helpers:

```bash
scripts/runpod_install_rsync.sh
```

Push current code/docs to the new pod:

```bash
scripts/runpod_sync.sh push
```

## Migration Plan

### Mode A: Restart With Existing Volume

Use this when the new pod attaches the previous 450 GB volume at `/workspace`.

Local Mac:

```bash
scripts/configure_runpod_env.sh \
  --host NEW_PUBLIC_SSH_HOST_OR_IP \
  --port NEW_PUBLIC_SSH_PORT \
  --pod-id NEW_POD_ID \
  --jupyter-url NEW_JUPYTER_LAB_URL \
  --test
scripts/runpod_sync.sh push
scripts/runpod_exec.sh 'bash scripts/runpod_bootstrap.sh'
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

RunPod data check:

```bash
cd /workspace/ai4agri
du -sh data/subtask1
test -f data/subtask1/test.csv
test -f data/subtask1/viticulture.tif
find data/subtask1 -maxdepth 1 -name "*.tif" | wc -l
```

Expected signal: `data/subtask1` is about `185G`, `test.csv` and `viticulture.tif` exist, and the TIFF count is large enough to include the 34 Sentinel-2 rasters plus labels. If this passes, start the overnight suite directly.

### Mode B: Restart Without Existing Data

Use this when `/workspace/ai4agri/data/subtask1` is missing, tiny, or does not contain the expected CSVs/rasters.

Local Mac:

```bash
scripts/configure_runpod_env.sh \
  --host NEW_PUBLIC_SSH_HOST_OR_IP \
  --port NEW_PUBLIC_SSH_PORT \
  --pod-id NEW_POD_ID \
  --jupyter-url NEW_JUPYTER_LAB_URL \
  --test
scripts/runpod_sync.sh push
scripts/runpod_exec.sh 'bash scripts/runpod_bootstrap.sh'
```

RunPod redownload:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/download_subtask1_hf.py --out-dir data/subtask1
python scripts/inspect_subtask1.py \
  --data-dir data/subtask1 \
  --splits train val test \
  --limit 1 \
  --read-pixels \
  --read-labels
du -sh data/subtask1
```

Expected signal: the download completes, image/label smoke-read succeeds, and `data/subtask1` is about `185G`. Start the overnight suite only after this check passes.

### Start Overnight Suite

Run this in either mode after data checks pass:

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

## Last Known Pod

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

- Start a replacement pod and choose Mode A if the old volume is available; otherwise use Mode B and redownload Subtask 1.
- Today priority: Subtask 1 leaderboard loop. Do not spend time on Subtask 2 until the next candidate has been trained, validated, and either submitted or rejected.
- Keep the Pod running only while Subtask 1 training/inference is active.
- When overnight experiments finish, inspect `summary.csv`, validate the best ZIP, and pull results locally.
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
scripts/runpod_install_rsync.sh
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
AI4AGRI_REMOTE_HOST=<new pod ssh host>
AI4AGRI_REMOTE_USER=root
AI4AGRI_REMOTE_PROJECT_DIR=/workspace/ai4agri
AI4AGRI_REMOTE_DATA_DIR=/workspace/ai4agri/data
AI4AGRI_REMOTE_RESULTS_DIR=/workspace/ai4agri/results
RUNPOD_SSH_PORT=<new pod ssh port>
RUNPOD_SSH_KEY=~/.ssh/id_ed25519
RUNPOD_JUPYTER_URL=<optional>
RUNPOD_POD_ID=<optional>
RUNPOD_POD_NAME=<optional>
```

## Rules

- Keep all project files, data, and results under `/workspace/ai4agri`.
- Do not use the 20 GB container disk for raw data or generated features.
- Avoid duplicate Subtask 1 raw-data copies; the 450 GB volume is usable but tight.
- Sync results back before deleting the Pod or volume.
