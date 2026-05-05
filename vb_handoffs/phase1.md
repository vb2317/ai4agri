# VB Handoffs: 2026-05-05

## Priority

Subtask 1 leaderboard work is the priority today.

Current submitted scores:

- Constant class baseline: `39.52`
- First sampled-pixel baseline: `39.74`

Goal: start the replacement RunPod, run the Subtask 1 experiment suite, and submit only one validated candidate if it is plausibly better.

## VB Tasks

### 1. Configure The New Pod

Run locally after the pod exposes SSH:

```bash
scripts/configure_runpod_env.sh \
  --host NEW_PUBLIC_SSH_HOST_OR_IP \
  --port NEW_PUBLIC_SSH_PORT \
  --pod-id NEW_POD_ID \
  --jupyter-url NEW_JUPYTER_LAB_URL \
  --test
```

Then push current code:

```bash
scripts/runpod_sync.sh push
```

### 2. Choose Migration Mode

Use `REMOTE_PROVIDER.md`.

Mode A: existing `/workspace` volume is present.

- Verify `data/subtask1` is about `185G`.
- Verify `test.csv` and `viticulture.tif` exist.
- Verify there are enough `.tif` rasters for the 34 Sentinel-2 frames plus labels.

Mode B: data is missing.

- Run `scripts/download_subtask1_hf.py --out-dir data/subtask1`.
- Smoke-read pixels and labels.
- Start experiments only after the smoke-read succeeds.

### 3. Start The Experiment Suite

Run on RunPod:

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

Check progress:

```bash
tail -f results/subtask1/experiments/overnight.log
```

### 4. Submission Gate

Submit only if:

- `best_inference.json` exists.
- The validation return code is `0`.
- The ZIP is not a duplicate of the previous `39.74` baseline.
- Codex has reviewed the summary or the metrics clearly beat the previous candidate.

Record the CodaBench score immediately in `Next.md` or chat.

## Do Not Spend Time On

- Subtask 2 packaging today unless Subtask 1 experiments are running and blocked.
- U-Net/ViT pod upgrade until we have the tabular/pixel experiment signal.
