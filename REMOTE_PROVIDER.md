# Remote Provider Plan

Last updated: 2026-05-04

## Recommendation

Use **Lambda Cloud On-Demand, 1x NVIDIA A10** as the default remote machine.

Target instance:

- Provider: Lambda Cloud
- Product: On-Demand Cloud instance
- GPU: 1x NVIDIA A10, 24GB VRAM
- RAM: 226 GiB
- vCPU: 30
- Included SSD: 1.3 TiB
- Listed price: $0.75/GPU/hour, plus applicable tax
- Expected 72-hour cost: about $54 plus tax if left running continuously

Why this choice:

- Subtask 1 data is about 200GB, so the 1.3 TiB included SSD gives enough room for raw data, extracted features, checkpoints, and submissions.
- Fixed on-demand pricing is simpler than a marketplace when deadline risk matters.
- Default Lambda images are ML-oriented and include JupyterLab access.
- SSH access is straightforward after adding a public key.
- A10 is enough for baselines, feature extraction, and lightweight CNN/temporal experiments.

Main risk:

- New Lambda accounts can hit quota/capacity limits. If A10 is unavailable, use the fallback section below.

Sources:

- Lambda pricing: https://lambda.ai/service/gpu-cloud/pricing
- Lambda launch flow: https://docs.lambda.ai/public-cloud/console/
- Lambda SSH/Jupyter access: https://docs.lambda.ai/public-cloud/on-demand/connecting-instance/
- Lambda billing: https://docs.lambda.ai/public-cloud/billing/
- Lambda instance creation notes: https://docs.lambda.ai/public-cloud/on-demand/creating-managing-instances/

## VB Subscription Instructions

### 1. Create Or Confirm Lambda Account

- Go to https://cloud.lambda.ai/
- Create or sign into the Lambda Cloud account.
- Open account settings and add billing/payment information.
- Check that On-Demand Cloud instances are enabled.

### 2. Add SSH Key

If you already have a local SSH key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the full output.

In Lambda Cloud:

- Open **SSH keys**.
- Click **Add SSH key**.
- Paste the public key.
- Name it something like `vb-macbook-ai4agri`.
- Save it.

If no SSH key exists locally:

```bash
ssh-keygen -t ed25519 -C "vb-ai4agri"
cat ~/.ssh/id_ed25519.pub
```

Then add the public key in Lambda Cloud.

### 3. Launch The Instance

In Lambda Cloud:

- Open **Instances**.
- Click **Launch instance**.
- Choose **1x NVIDIA A10**.
- Pick the closest available region with A10 capacity.
- Choose the default Lambda Stack / PyTorch-style image if offered.
- Do not attach a persistent filesystem for the first run unless Lambda requires it.
- Select the SSH key added above.
- Accept terms and launch.

Record these values after launch:

```text
Provider: Lambda Cloud
Instance type: 1x NVIDIA A10
Region:
Instance IP:
SSH key path:
Remote project dir: /home/ubuntu/ai4agri
Remote data dir: /home/ubuntu/ai4agri/data
Remote results dir: /home/ubuntu/ai4agri/results
Budget ceiling:
```

### 4. Connect From Local Machine

Lambda instances use the `ubuntu` user:

```bash
ssh -i ~/.ssh/id_ed25519 ubuntu@<INSTANCE_IP>
```

If using a different key path, replace `~/.ssh/id_ed25519`.

### 5. First Remote Setup Commands

Run these on the Lambda instance:

```bash
git --version
python3 --version
nvidia-smi
df -h
free -h
```

Then clone the repo or copy it from local. If the repo is on GitHub:

```bash
git clone <REPO_URL> ~/ai4agri
cd ~/ai4agri
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If `agripotential` is not installable from `requirements.txt`, run:

```bash
pip install git+https://github.com/MohammadElSakka/agripotential
```

### 6. Fill Local `.env`

On the local repo, update `.env` with the launched instance details:

```text
AI4AGRI_REMOTE_HOST=<INSTANCE_IP>
AI4AGRI_REMOTE_USER=ubuntu
AI4AGRI_REMOTE_PROJECT_DIR=/home/ubuntu/ai4agri
AI4AGRI_DATA_DIR=/home/ubuntu/ai4agri/data
AI4AGRI_RESULTS_DIR=/home/ubuntu/ai4agri/results
```

Do not commit `.env`.

### 7. Cost Guardrails

- Use a budget ceiling of **$75** for the initial deadline push unless VB chooses otherwise.
- At $0.75/hr, $75 covers about 100 instance-hours before tax.
- Do not terminate the instance until useful artifacts are synced off it.
- Do not leave the instance running unattended after experiments complete.
- Lambda billing for On-Demand instances runs while instances are running.
- If using a Lambda filesystem, remember filesystem billing continues while the filesystem exists.

## Fallback Provider

Use **RunPod Pods** if Lambda cannot launch an A10 quickly.

Fallback target:

- RunPod Secure Cloud or high-reliability Community Cloud
- 1x L4, A5000, RTX 3090/4090, A6000, or A40
- At least 500GB persistent volume, preferably 750GB
- PyTorch template with SSH/Jupyter enabled
- Initial credits: $50-$75

Why fallback:

- RunPod has broad GPU availability and per-second billing.
- Pods support SSH, Jupyter, and persistent `/workspace` storage.
- Network volumes can persist independently if we need to move between Pods.

RunPod caveats:

- GPU prices vary by availability and market.
- Storage continues billing while stopped.
- Spot instances can be interrupted; avoid spot for first valid submission unless cost becomes the priority.

Sources:

- RunPod pricing: https://docs.runpod.io/pods/pricing
- RunPod billing: https://docs.runpod.io/accounts-billing/billing
- RunPod SSH: https://docs.runpod.io/pods/configuration/use-ssh
- RunPod storage: https://docs.runpod.io/pods/storage/sync-volumes

## Decision Record

Current decision:

- Default remote provider: Lambda Cloud
- Default instance: 1x NVIDIA A10
- Fallback provider: RunPod
- Codex is blocked on writing provider-specific run commands until VB launches the instance or provides the instance details.
