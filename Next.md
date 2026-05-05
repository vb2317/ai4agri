# Next

Last updated: 2026-05-05

## Current Floor

Subtask 1 is still the active priority because CodaBench gives immediate leaderboard feedback.

Submitted scores:

- Constant class baseline: `39.52`
- Sampled-pixel baseline: `39.74`
- Overnight uniform raw-temporal HGB: `40.16`
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

Safest next experiment: postprocess the existing ResNet/FPN checkpoint, validate, audit, then decide whether it deserves a submission.

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

## Pooling And Hidden-Window Notes

Current model downsampling behavior:

- `unet`: explicit `2x2` max pooling three times, so hidden resolution goes `128 -> 64 -> 32 -> 16`.
- `resnet_fpn`: ImageNet-style ResNet stem, with `7x7 stride-2` conv followed by ResNet's `3x3 stride-2` max pool, then more downsampling in later ResNet stages. This is more aggressive early downsampling than the U-Net.
- `tiny_vit`: no max pool; patch embedding is an `8x8` stride-8 convolution.
- `sam_decoder`: no max pool; patch embedding is a `4x4` stride-4 convolution.

Heuristic from train+val label clusters:

- Median connected cluster area is about `736` pixels, roughly `27x27`.
- 75th percentile is about `2746` pixels, roughly `52x52`.
- 90th percentile is about `7906` pixels, roughly `89x89`.
- Class-level 90th percentile equivalent square sizes are approximately class 0 `116x116`, class 1 `77x77`, class 2 `67x67`, class 3 `68x68`, class 4 `78x78`.

Proposed ResNet variant:

- Add `resnet_fpn_dense`.
- Change first conv from `7x7 stride=2` to `3x3 stride=1`.
- Remove/disable the early ResNet max pool.
- Keep the FPN lateral decoder.
- Optionally add dilation in later stages if memory permits.

Purpose: preserve small and medium field boundaries longer in the hidden layers. This is different from changing the CSV/input patch window, which remains `128x128`.

## Active Bigger Model Run

Started on L40S at `2026-05-05T17:35:00Z`:

- Run id: `l40s_sam_decoder_summary_pm1_full_b16_e24_s64`
- Remote Python PID at launch: `9766`.
- Model: `sam_decoder`, a promptless SAM-style ViT encoder with a custom dense decoder that accepts the existing Sentinel summary tensor channels.
- Loss: `pm1_ce`, which spreads target probability mass over labels within +/-1 so the objective matches the leaderboard tolerance where, for example, `0` predicted as `1` still counts.
- Config: summary temporal features, full `train.csv` and `val.csv`, batch size `16`, max `24` epochs, patience `5`, `--base-channels 64`, seed `64`, median smoothing `3`.
- GPU check after launch: about `8GB` allocated on the L40S; `396` train batches per epoch.

Monitor:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'tail -n 80 results/subtask1/vision_runs/l40s_sam_decoder_summary_pm1_full_b16_e24_s64/nohup.log'
```

## Overnight Plan

Started a remote overnight queue at `2026-05-05T18:29:25Z` (`2026-05-05 23:59 IST`). It waits for the active SAM-style run to finish, then keeps the L40S busy with sequential experiments.

Queue log:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'tail -n 120 results/subtask1/vision_runs/overnight_queue_20260505.log'
```

Sequence:

1. Finish active `l40s_sam_decoder_summary_pm1_full_b16_e24_s64`.
   - Current best at planning time: Accuracy +/- 1 `0.74070` at epoch `4`; below the `50.63` submitted TinyViT floor, but useful exploration for pm1-aware loss and SAM-style decoder behavior.
2. Run `l40s_resnet_fpn_dense_summary_soft_full_b8_e24_s70`.
   - Purpose: test the hidden-window hypothesis by using a dense ResNet/FPN stem: `3x3 stride=1`, no early maxpool, FPN decoder preserved.
   - This is the highest-priority overnight candidate because the submitted TinyViT still has weak class 4 recall and dense ResNet may preserve field boundaries better.
3. If time remains, run `l40s_tiny_vit_seasonal_soft_full_b8_e20_s65`.
   - Purpose: full-data seasonal TinyViT to test temporal-view diversity beyond the small 1536-patch seasonal probe.

VB morning checklist for `2026-05-06 08:00 IST`:

1. Check GPU/process status:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'nvidia-smi && ps -eo pid,etime,stat,cmd | grep run_subtask1_vision | grep -v grep || true'
```

2. Check queue and latest metrics:

```bash
scripts/runpod_exec.sh --env-file .env.l40s.claude \
  'tail -n 160 results/subtask1/vision_runs/overnight_queue_20260505.log; for r in l40s_sam_decoder_summary_pm1_full_b16_e24_s64 l40s_resnet_fpn_dense_summary_soft_full_b8_e24_s70 l40s_tiny_vit_seasonal_soft_full_b8_e20_s65; do echo --- $r; cat results/subtask1/vision_runs/$r/metrics.json 2>/dev/null || true; done'
```

3. Pull only completed candidate artifacts:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude pull \
  /workspace/ai4agri/results/subtask1/vision_runs/<run_id>/ \
  ./results/subtask1/vision_runs/<run_id>/
scripts/runpod_sync.sh --env-file .env.l40s.claude pull \
  /workspace/ai4agri/results/subtask1/visuals/<run_id>/ \
  ./results/subtask1/visuals/<run_id>/
scripts/runpod_sync.sh --env-file .env.l40s.claude pull \
  /workspace/ai4agri/results/subtask1/val_preds/<run_id>_val_probs.npz \
  ./results/subtask1/val_preds/
```

4. Candidate decision rule:

- Do not submit anything below the `50.63` floor unless it is part of an ensemble/postprocess plan.
- Consider ZIP generation and audit only if full-val Accuracy +/- 1 is at least near TinyViT (`>= 0.76`) or the class recalls show clear complementary value, especially class 4.
- If all queued jobs are done and no candidate is compelling, stop the L40S pod to avoid spend.

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
