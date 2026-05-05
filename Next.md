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

Current floor: `47.6` from:

```text
results/subtask1/submissions/l40s_resnet_fpn_summary_e30.zip
```

Validation for that run:

- Run ID: `l40s_resnet_fpn_summary_e30`
- Best epoch: `10`
- Validation Accuracy +/- 1: `0.78984`
- Exact accuracy: `0.45868`
- MAE: `0.86056`
- Audit: `results/subtask1/vision_runs/l40s_resnet_fpn_summary_e30/local_candidate_review.json`
- Test class pixel fractions: class 0 `0.38625`, class 1 `0.23099`, class 2 `0.11646`, class 3 `0.25395`, class 4 `0.01236`
- Flat PNGs: `28/800`

## VB Instructions

1. Keep `47.6` as the floor. Do not submit anything unless the expected improvement is credible.
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
- The candidate is not just a duplicate of the submitted `47.6` ZIP.
- VB is ready to record the CodaBench score immediately.

## Parking Lot

- Confirm DACIA5 Sentinel-2 12-band order before adding vegetation indices.
- Prepare Subtask 2 Colab/notebook and 3-page report before the May 28 deadline.
- Keep HGB results as fallback/ensemble evidence, not as the primary improvement path.
