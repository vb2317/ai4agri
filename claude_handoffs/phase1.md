# Claude Handoff: L40S Subtask 1 Vision Run

Status: Ready for Claude
Date: 2026-05-05

## Ownership

Claude owns the full L40S 48 GB RunPod lane end to end:

- Verify pod environment and data.
- Bootstrap dependencies if needed.
- Run Subtask 1 vision smoke experiments.
- Promote one stable ResNet/FPN or TinyViT run to a full run.
- Pull or report metrics, logs, visual artifacts, and candidate ZIP path.
- Do not submit to CodaBench. VB owns final upload.

Codex owns the common repo code, validators, notebooks, and existing non-L40S RunPod setup.

## Current Floor

The current validated CodaBench floor is `40.16`.

Existing floor ZIP:

```text
results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip
```

Do not spend L40S time on HGB-only experiments unless needed for an ensemble comparison. The L40S lane is for vision models.

## Local Env File

VB should configure the L40S pod locally without overwriting the existing pod:

```bash
scripts/configure_runpod_env.sh \
  --env-file .env.l40s.claude \
  --host L40S_PUBLIC_SSH_HOST_OR_IP \
  --port L40S_PUBLIC_SSH_PORT \
  --pod-id L40S_POD_ID \
  --pod-name claude-l40s \
  --jupyter-url L40S_JUPYTER_URL \
  --test
```

Claude should use `--env-file .env.l40s.claude` on every local helper command.

## Setup Commands

Push common code to the L40S pod:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude push
```

Install remote prerequisites and inspect the pod:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude 'bash scripts/runpod_bootstrap.sh'
scripts/runpod_exec.sh --env-file .env.l40s.claude 'bash scripts/runpod_status.sh'
```

Data check:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude '
  source .venv/bin/activate
  du -sh data/subtask1 || true
  test -f data/subtask1/test.csv
  test -f data/subtask1/viticulture.tif
  find data/subtask1 -maxdepth 1 -name "*.tif" | wc -l
  python scripts/inspect_subtask1.py \
    --data-dir data/subtask1 \
    --splits train val test \
    --limit 1 \
    --read-pixels \
    --read-labels
'
```

If `data/subtask1` is missing or incomplete, run:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude '
  source .venv/bin/activate
  python scripts/download_subtask1_hf.py --out-dir data/subtask1
'
```

## Smoke Runs

Run ResNet/FPN smoke first:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude '
  source .venv/bin/activate
  mkdir -p results/subtask1/vision_runs/l40s_smoke_resnet_fpn_summary
  nohup python scripts/run_subtask1_vision.py train \
    --data-dir data/subtask1 \
    --run-id l40s_smoke_resnet_fpn_summary \
    --model resnet_fpn \
    --temporal-mode summary \
    --epochs 2 \
    --patch-limit 32 \
    --val-patch-limit 8 \
    --batch-size 8 \
    --visual-limit 8 \
    --write-test-visuals \
    > results/subtask1/vision_runs/l40s_smoke_resnet_fpn_summary/nohup.log 2>&1 &
'
```

Run TinyViT smoke only after ResNet/FPN is stable:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude '
  source .venv/bin/activate
  mkdir -p results/subtask1/vision_runs/l40s_smoke_tiny_vit_summary
  nohup python scripts/run_subtask1_vision.py train \
    --data-dir data/subtask1 \
    --run-id l40s_smoke_tiny_vit_summary \
    --model tiny_vit \
    --temporal-mode summary \
    --epochs 2 \
    --patch-limit 32 \
    --val-patch-limit 8 \
    --batch-size 8 \
    --visual-limit 8 \
    --write-test-visuals \
    > results/subtask1/vision_runs/l40s_smoke_tiny_vit_summary/nohup.log 2>&1 &
'
```

Check progress:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude 'tail -n 80 results/subtask1/vision_runs/l40s_smoke_resnet_fpn_summary/nohup.log'
```

## Full Run

Promote the best smoke family only if masks are non-collapsed and metrics/visuals are sane.

Recommended first full L40S run:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude '
  source .venv/bin/activate
  mkdir -p results/subtask1/vision_runs/l40s_resnet_fpn_summary_e30
  nohup python scripts/run_subtask1_vision.py train \
    --data-dir data/subtask1 \
    --run-id l40s_resnet_fpn_summary_e30 \
    --model resnet_fpn \
    --temporal-mode summary \
    --epochs 30 \
    --batch-size 8 \
    --patience 8 \
    --visual-limit 20 \
    --write-test-visuals \
    > results/subtask1/vision_runs/l40s_resnet_fpn_summary_e30/nohup.log 2>&1 &
'
```

If memory allows and ResNet/FPN is sane, run TinyViT full:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude '
  source .venv/bin/activate
  mkdir -p results/subtask1/vision_runs/l40s_tiny_vit_summary_e30
  nohup python scripts/run_subtask1_vision.py train \
    --data-dir data/subtask1 \
    --run-id l40s_tiny_vit_summary_e30 \
    --model tiny_vit \
    --temporal-mode summary \
    --epochs 30 \
    --batch-size 8 \
    --patience 8 \
    --visual-limit 20 \
    --write-test-visuals \
    > results/subtask1/vision_runs/l40s_tiny_vit_summary_e30/nohup.log 2>&1 &
'
```

## Inference And Validation

For the selected full run:

```bash
RUN_ID=l40s_resnet_fpn_summary_e30
MODEL=resnet_fpn

scripts/runpod_exec.sh --env-file .env.l40s.claude "
  source .venv/bin/activate
  python scripts/run_subtask1_vision.py infer \
    --data-dir data/subtask1 \
    --run-id ${RUN_ID} \
    --model ${MODEL} \
    --temporal-mode summary \
    --checkpoint results/subtask1/vision_runs/${RUN_ID}/best.pt
  python scripts/validate_submission_zip.py \
    --zip-path results/subtask1/submissions/${RUN_ID}.zip \
    --subtask1-codabench \
    --expected-ids-file data/subtask1/test.csv \
    --check-class-values
"
```

Pull the L40S results:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude pull-results
```

## Required Output Back To VB/Codex

Return only implementation-relevant run status:

- Pod GPU and CUDA check result.
- Whether data was already present or redownloaded.
- Smoke run metrics paths and any errors/OOM.
- Full run `run_id`.
- `metrics.json` summary: Accuracy +/- 1, exact accuracy, MAE, per-class recall.
- Visual artifact directory.
- Validation return code for the ZIP.
- Candidate ZIP path.
- Recommendation: submit, reject, or hold for ensemble review.

## Human Review Gate

VB reviews `notebooks/subtask1_testbed.ipynb` with `RUN_ID` set to the selected L40S run.

Reject the run before submission if:

- predictions collapse to one class;
- classes `0` and `4` never appear;
- edges are spatially incoherent;
- ZIP validation fails;
- validation metrics are clearly below the `40.16` floor without a qualitative reason to try it.
