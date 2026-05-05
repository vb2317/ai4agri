# Next

Last updated: 2026-05-05

## Current Floor

Subtask 1 is still the active priority because CodaBench gives immediate leaderboard feedback.

Submitted scores:

- Constant class baseline: `39.52`
- Sampled-pixel baseline: `39.74`
- Overnight uniform raw-temporal HGB: `40.16`
- Existing U-Net CE summary rand e10: `45.96`
- L40S ResNet/FPN vision model: `47.6`
- Full-data TinyViT summary-soft model: `50.63`

Current floor: `50.63` from:

```text
results/subtask1/submissions/l40s_tiny_vit_summary_soft_full_e30_s52.zip
```

Validation for that run:

- Run ID: `l40s_tiny_vit_summary_soft_full_e30_s52`
- Best epoch: `6`
- Validation Accuracy +/- 1: `0.76609`
- Exact accuracy: `0.46752`
- MAE: `0.93469`
- CodaBench score: `50.63`

## VB Instructions

1. Keep `50.63` as the floor. Do not submit anything unless the expected improvement is credible.
2. Check CodaBench submission limits before spending more attempts.
3. If the L40S or existing RunPod pod is idle, stop it to avoid unnecessary cost.
4. If trying one more Subtask 1 candidate, prefer inference-only postprocessing from the existing ResNet/FPN checkpoint before retraining.
5. After every CodaBench upload, immediately record the score in this file and in `CHATGPT_PLAN.md`.

## Best Next Candidate

Two lanes are active:

1. L40S lane: postprocess the existing ResNet/FPN checkpoint, validate, audit, then decide whether it deserves a submission.
2. Existing RunPod lane: full-data U-Net with PM1 multi-hot BCE and neighbor-sum sigmoid decoding.

Current active full-data run on the existing RunPod:

```text
existing_unet_pm1bce_nsum_summary_full_e30_m5
```

Monitor:

```bash
scripts/runpod_exec.sh 'tail -n 80 results/subtask1/vision_runs/existing_unet_pm1bce_nsum_summary_full_e30_m5/nohup.log'
```

PM1 smoke/subset results on the existing RunPod:

- `existing_unet_pm1bce_nsum_summary_rand_e10_p1024_v256_m5`
  - Loss: `pm1_bce`
  - Decode: `neighbor_sum_sigmoid`
  - Best validation Accuracy +/- 1: `0.792395`
  - Best epoch: `9`
  - Note: predicts only classes `1..3`, which is expected under neighbor-sum edge behavior and may still be favorable for the Accuracy +/- 1 metric.
- `existing_unet_pm1bce_softnsum_summary_rand_e10_p1024_v256_m5`
  - Loss: `pm1_bce`
  - Decode: `neighbor_sum`
  - Best validation Accuracy +/- 1: `0.786270`
  - Best epoch: `4`

New visual review notebooks:

- `notebooks/11_subtask1_visual_review.ipynb`: general GT/prediction/error/Accuracy +/- 1 visual review.
- `notebooks/12_accuracy_pm1_review.ipynb`: focused Accuracy +/- 1 review with curated good examples, edge-class behavior, and failure sets.

Safest L40S experiment: postprocess the existing ResNet/FPN checkpoint, validate, audit, then decide whether it deserves a submission.

Run on the L40S pod:

```bash
cd /workspace/ai4agri
source .venv/bin/activate

python scripts/run_subtask1_vision.py infer \
  --data-dir data/subtask1 \
  --run-id l40s_resnet_fpn_summary_e30_expected_m3 \
  --model resnet_fpn \
  --temporal-mode summary \
  --checkpoint results/subtask1/vision_runs/l40s_resnet_fpn_summary_e30/best.pt \
  --decode expected \
  --median-size 3 \
  --visual-limit 20

python scripts/review_subtask1_candidate.py \
  --run-id l40s_resnet_fpn_summary_e30_expected_m3 \
  --data-dir data/subtask1 \
  --report-json results/subtask1/vision_runs/l40s_resnet_fpn_summary_e30_expected_m3/candidate_review.json
```

Pull results locally:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude pull-results
```

Submit only if:

- ZIP validation passes.
- Candidate audit passes.
- Visuals are not obviously worse than `l40s_resnet_fpn_summary_e30`.
- Class distribution is plausible and not collapsed.

## Transformer Information Runs

Started on L40S at `2026-05-05T12:07:21Z`; finished at `2026-05-05T12:32:32Z`.

Purpose: collect TinyViT validation probabilities and visual panels for eventual ensemble decisions, not immediate CodaBench upload.

Completed runs:

- `l40s_tiny_vit_summary_soft_p1536_v256_s52`: Accuracy +/- 1 `0.75066`, exact `0.51240`, MAE `0.93316`.
  - Per-class recall: class 0 `0.8823`, class 1 `0.0602`, class 2 `0.0000`, class 3 `0.3919`, class 4 `0.3107`.
  - Useful because it is the strongest TinyViT by +/-1, but class 2 is absent.
- `l40s_tiny_vit_seasonal_soft_p1536_v256_s53`: Accuracy +/- 1 `0.74500`, exact `0.48601`, MAE `0.96214`.
  - Per-class recall: class 0 `0.8117`, class 1 `0.0048`, class 2 `0.0000`, class 3 `0.6251`, class 4 `0.0418`.
  - Useful because seasonal features give a different class 3-heavy error profile.
- `l40s_tiny_vit_summary_wce_p1536_v256_s54`: Accuracy +/- 1 `0.72038`, exact `0.46342`, MAE `1.04371`.
  - Per-class recall: class 0 `0.7074`, class 1 `0.1833`, class 2 `0.0782`, class 3 `0.2374`, class 4 `0.5405`.
  - Useful because weighted CE recovers class 4 and some class 2, making it the best diversity candidate for an ensemble.

Monitor:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'tail -n 80 results/subtask1/vision_runs/transformer_info_20260505.log'
```

Pulled local artifacts:

- Validation probabilities: `results/subtask1/val_preds/l40s_tiny_vit_*_val_probs.npz`
- Metrics/checkpoints/logs: `results/subtask1/vision_runs/l40s_tiny_vit_*/`
- Visual panels: `results/subtask1/visuals/l40s_tiny_vit_*/`

Do not submit these directly. Use them to test ensemble weights against `l40s_resnet_fpn_summary_e30_val_probs.npz`.

## Full TinyViT Run

Started on L40S at `2026-05-05T15:41:00Z`; finished with early stopping after epoch `12`.

- Run id: `l40s_tiny_vit_summary_soft_full_e30_s52`
- Config: TinyViT, summary temporal features, soft ordinal CE, seed `52`, median smoothing `3`, batch size `8`, max `30` epochs, patience `6`.
- Dataset scope: full `train.csv` and full `val.csv`; no `--patch-limit` or `--val-patch-limit`.
- Best epoch: `6`.
- Full-val Accuracy +/- 1: `0.76609`; exact `0.46752`; MAE `0.93469`.
- CodaBench score: `50.63`, which is the current submitted floor.
- Per-class recall at best epoch: class 0 `0.7391`, class 1 `0.2301`, class 2 `0.0438`, class 3 `0.5843`, class 4 `0.0245`.
- Local artifacts: checkpoint/metrics under `results/subtask1/vision_runs/l40s_tiny_vit_summary_soft_full_e30_s52/`, val probabilities at `results/subtask1/val_preds/l40s_tiny_vit_summary_soft_full_e30_s52_val_probs.npz`, visuals under `results/subtask1/visuals/l40s_tiny_vit_summary_soft_full_e30_s52/`, ZIP at `results/subtask1/submissions/l40s_tiny_vit_summary_soft_full_e30_s52.zip`.
- Use as an ensemble candidate, not an automatic submission: class 3 is strong, but class 4 recall is weak.

Monitor:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'tail -n 80 results/subtask1/vision_runs/l40s_tiny_vit_summary_soft_full_e30_s52/train.log'
```

Check process/GPU:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'nvidia-smi && ps -eo pid,etime,stat,cmd | grep run_subtask1_vision | grep -v grep || true'
```

## Secondary Options

Use these only after the postprocess check:

- Weighted ResNet/FPN or U-Net run if class 4 recall remains the main weakness.
- Ensemble ResNet/FPN with TinyViT or HGB only if the second model is genuinely different and passes audit.
- Subtask 2 notebook/report cleanup after Subtask 1 submissions stop improving.

## RunPod Commands

Status:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude 'bash scripts/runpod_status.sh'
```

Push code/docs:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude push
```

Pull all results:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude pull-results
```

Review a candidate:

```bash
python scripts/review_subtask1_candidate.py \
  --run-id <run_id> \
  --data-dir data/subtask1
```

## Submission Gate

Before any new Subtask 1 upload:

- `scripts/review_subtask1_candidate.py` passes.
- `results/subtask1/visuals/<run_id>/` has been visually reviewed.
- The candidate is not just a duplicate of the submitted `50.63` ZIP.
- VB is ready to record the CodaBench score immediately.

## Parking Lot

- Confirm DACIA5 Sentinel-2 12-band order before adding vegetation indices.
- Prepare Subtask 2 Colab/notebook and 3-page report before the May 28 deadline.
- Keep HGB results as fallback/ensemble evidence, not as the primary improvement path.
