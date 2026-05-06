# Next

Last updated: 2026-05-06

## Current Floor

Subtask 1 is still the active priority because CodaBench gives immediate leaderboard feedback.

Critical correction found on `2026-05-06`: raw AgriPotential labels are `1..5`, and raw `0` means unlabelled/nodata. Training code now remaps raw `1..5` to model classes `0..4` and ignores raw `0` as `255`. Any run created before this correction has trained on the wrong label convention and should be treated as deprecated evidence only.

Submitted scores:

- Constant class baseline: `39.52`
- Sampled-pixel baseline: `39.74`
- Overnight uniform raw-temporal HGB: `40.16`
- Existing U-Net CE summary rand e10: `45.96`
- L40S ResNet/FPN vision model: `47.6`
- Full-data TinyViT summary-soft model: `50.63`
- Existing U-Net PM1 BCE neighbor-sum full-data model: `41.83`

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
6. Do not submit PM1 neighbor-sum U-Net as a standalone model again. Its full-val Accuracy +/- 1 was high, but its CodaBench score was only `41.83`, showing a severe validation/leaderboard mismatch.
7. Restart Subtask 1 model exploration from corrected labels before spending more submissions. New inference defaults to writing raw `1..5` PNG values via `--submission-label-offset 1`.

## Label And Band Corrections

Raw label convention:

- Raw `0`: unlabelled/nodata; ignore for training and validation.
- Raw `1..5`: valid ordinal classes.
- Model convention: raw labels are shifted to `0..4` internally.
- Submission convention: corrected inference writes model prediction `+1`, producing raw values `1..5` by default.

Patched files:

- `src/ai4agri/subtask1/data.py`: U-Net/ResNet/TinyViT loader now ignores raw `0` and shifts raw `1..5` to model `0..4`.
- `scripts/subtask1_baseline.py`: sampled-pixel baseline now uses the same raw-label shift.
- `scripts/run_subtask1_vision.py`: inference now supports `--submission-label-offset`, default `1`.
- `scripts/validate_submission_zip.py` and `scripts/review_subtask1_candidate.py`: validation/audit defaults now allow raw submission classes `1..5`.

Band interpretation:

- Sentinel-2 raster band index `0` is `B2`, not `B1`.
- RGB visualization should use indices `2,1,0` for `B4,B3,B2`.
- Likely 10-band order: `B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12`.
- This does not invalidate model inputs, but previous feature/band labels referring to `B1` were wrong.

Deprecated runs:

- All submitted and trained models before this fix, including TinyViT `50.63`, ResNet/FPN `47.6`, U-Net CE `45.96`, and PM1 `41.83`, were trained/evaluated with the wrong raw label convention.
- Keep `50.63` as the leaderboard floor, but do not use old validation metrics to choose architecture without rerunning under corrected labels.

## Corrected-Label GPU-Max Runs

Started on existing RTX PRO 4500 RunPod at `2026-05-06T04:36:19Z` after killing stale and duplicate runs.

Operational changes:

- Added local feature caching via `--cache-dir`; summary tensors are cached under `/tmp/ai4agri_subtask1_summary_cache`.
- Cache size after warmup: about `8.9G` for full train+val summary tensors.
- Added persistent DataLoader workers and higher prefetching.
- U-Net summary training now runs from cache in seconds per epoch instead of repeatedly reading 185G of network-hosted rasters.

Completed corrected PM1 run:

```text
corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache
```

Best visible validation:

- Accuracy +/- 1: `0.8302` at epoch `7`.
- Later best saved metrics should be confirmed from `metrics.json` before submission.
- This run writes corrected raw-label submissions (`1..5`) because inference defaults to `--submission-label-offset 1`.

Active runs:

- `corrected_unet_pm1bce_softnsum_summary_full_e30_m5_s74_b64_cache_parallel`
  - PM1 BCE, softmax neighbor-sum decode, median `5`, batch size `64`.
- `corrected_unet_pm1bce_nsum_summary_full_e30_m3_s75_b32_cache`
  - PM1 BCE, sigmoid neighbor-sum decode, median `3`, batch size `32`.

Killed/cancelled:

- `corrected_resnet_fpn_summary_full_e30_s73`: cancelled when PM1 strategy was restored.
- `corrected_unet_pm1bce_softnsum_summary_full_e30_m5_s74_b32_cache`: duplicate of the batch-64 soft-neighbor run; killed to avoid wasting GPU.

Monitor:

```bash
scripts/runpod_exec.sh 'ps -eo pid,etime,stat,cmd | grep run_subtask1_vision | grep -v grep; nvidia-smi'
```

Run logs:

```bash
scripts/runpod_exec.sh 'tail -n 80 results/subtask1/vision_runs/corrected_pm1_queue_gpu_max_20260506.log'
scripts/runpod_exec.sh 'tail -n 80 results/subtask1/vision_runs/corrected_unet_pm1bce_softnsum_summary_full_e30_m5_s74_b64_cache_parallel.nohup'
```

Submission gate for these corrected PM1 runs:

- Pull results locally.
- Check `metrics.json`, `metrics_history.json`, visuals, class coverage, and ZIP validation.
- Do not submit unless corrected-label validation and visual review plausibly beat the `50.63` floor.

## Overnight Run Plan

Armed on the existing RTX PRO 4500 RunPod at `2026-05-05T18:20:36Z`.

Queue PID:

```text
17121
```

Queue script:

```text
results/subtask1/vision_runs/overnight_existing_gpu_20260505.sh
```

Queue log:

```text
results/subtask1/vision_runs/overnight_existing_gpu_20260505.log
```

The queue waits for the active full-data PM1 U-Net run to finish before starting additional training. Do not start another foreground training process on the existing pod unless this queue has been stopped or has finished.

Completed lead run:

```text
existing_unet_pm1bce_nsum_summary_full_e30_m5
```

Visible full-val metrics so far:

- Epoch 1: Accuracy +/- 1 `0.76439`, exact `0.20574`, MAE `1.12860`.
- Epoch 2: Accuracy +/- 1 `0.78693`, exact `0.21172`, MAE `1.07214`.
- Epoch 3: Accuracy +/- 1 `0.73572`, exact `0.15946`, MAE `1.20105`.
- Epoch 4: Accuracy +/- 1 `0.73960`, exact `0.16077`, MAE `1.18835`.
- Best saved metrics: Accuracy +/- 1 `0.80566`, exact `0.19225`, MAE `1.08075`, best epoch `10`.
- CodaBench score: `41.83`.
- Interpretation: PM1 neighbor-sum overfit the local validation objective and produced only classes `1..3`; keep artifacts only for analysis or ensemble diversity, not standalone submission.

Queued experiments, in order:

1. `existing_unet_softce_expected_summary_full_e18_m3_s61`
   - U-Net, summary features, `soft_ce`, expected-value decode, median `3`.
   - Purpose: non-PM1 ordinal baseline with smoother decoding.
2. `existing_unet_ce_wmild_argmax_summary_full_e18_m5_s62`
   - U-Net, summary features, weighted CE, argmax decode, median `5`.
   - Purpose: class-recall diversity and a conventional segmentation baseline.
3. `existing_resnet_fpn_softce_expected_summary_full_e18_m3_s63`
   - ResNet/FPN, summary features, `soft_ce`, expected-value decode, median `3`, batch size `4`.
   - Purpose: different encoder/decoder family on the existing pod.
4. `existing_tiny_vit_softce_expected_summary_full_e12_m3_s64`
   - TinyViT, summary features, `soft_ce`, expected-value decode, median `3`, batch size `4`.
   - Purpose: transformer sanity/diversity run if the pod remains available overnight.

## Concat Temporal Queue

Armed on the existing RTX PRO 4500 RunPod at `2026-05-06T00:50Z`.

Queue PID:

```text
21546
```

Queue script:

```text
results/subtask1/vision_runs/concat_queue_20260506.sh
```

Queue log:

```text
results/subtask1/vision_runs/concat_queue_20260506.log
```

Purpose: test `--temporal-mode concat`, which uses every Sentinel-2 scene and every band directly instead of temporal summaries. With the current data this is expected to produce roughly `34 scenes * 10 bands = 340` input channels, compared with `40` channels for `summary` mode.

Queued experiments:

1. `existing_unet_concat_softce_smoke_p512_v128_e4_m3_s71`
   - U-Net, concat temporal mode, `soft_ce`, expected-value decode, median `3`.
   - Patch-limited smoke: `512` train patches, `128` val patches, batch size `4`.
   - Purpose: confirm memory, speed, and visual sanity before committing a full run.
2. `existing_unet_concat_softce_full_e12_m3_s72`
   - U-Net, concat temporal mode, `soft_ce`, expected-value decode, median `3`.
   - Full train/val splits, max `12` epochs, patience `4`, batch size `4`.
   - Purpose: assess whether full temporal information improves over summary-mode U-Net.

Monitor:

```bash
scripts/runpod_exec.sh 'tail -n 80 results/subtask1/vision_runs/concat_queue_20260506.log'
```

Do not interpret concat as RGB. It is an all-band, all-scene input mode. The tradeoff is richer temporal information versus much heavier I/O and a wider first convolution.

Monitor queue:

```bash
scripts/runpod_exec.sh 'tail -n 80 results/subtask1/vision_runs/overnight_existing_gpu_20260505.log'
```

Monitor active training:

```bash
scripts/runpod_exec.sh 'ps -eo pid,etime,cmd | grep -E "run_subtask1_vision.py train|overnight_existing_gpu" | grep -v grep'
```

Pull results in the morning:

```bash
scripts/runpod_sync.sh pull-results
```

Morning decision gates for VB:

- Keep `50.63` as the submission floor unless a new candidate has a credible reason to beat it.
- First inspect `metrics.json`, `train.log`, and visual panels for the active PM1 full run.
- Use `notebooks/12_accuracy_pm1_review.ipynb` for PM1-specific good/failure examples.
- Use `notebooks/11_subtask1_visual_review.ipynb` for GT/prediction/error/Accuracy +/- 1 panel review.
- Submit only if ZIP validation passes, visuals are coherent, predictions are not collapsed, and the candidate is plausibly stronger than the submitted TinyViT.
- If L40S access is available in the morning, prioritize Claude exporting L40S artifacts and postprocessing/ensembling there; it remains the better pod for TinyViT and ResNet exploration.

## VB Task: SAM vs TinyViT Output Review

Run `notebooks/11_sam_vs_tinyvit_output_analysis.ipynb` before using the SAM decoder in any ensemble.

Purpose:

- Explain why `l40s_sam_decoder_summary_pm1_full_b16_e24_s64` underperformed the full-data TinyViT.
- Measure whether SAM has real complementary correct pixels or only noisy disagreement.
- Test TinyViT/SAM validation probability averaging and expected-value decoding before spending a submission.

Current diagnosis before notebook review:

- TinyViT is the submitted floor at `50.63`, with validation Accuracy +/- 1 `0.76609`.
- SAM decoder validation Accuracy +/- 1 was `0.74070`, with class-2 recall `0.0`.
- The SAM run used a promptless SAM-style encoder trained from scratch, not pretrained RGB SAM.
- The `pm1_ce` loss may have helped tolerance-aware neighboring labels but likely softened exact class separation too much.

VB decision rule:

- Do not submit SAM standalone unless CodaBench proves otherwise.
- Use SAM in an ensemble only if the notebook's validation sweep beats TinyViT alone and the gain is not just a tiny exact-accuracy fluctuation.
- If SAM class 2 remains collapsed in the notebook tables, the next SAM run must change loss/class weighting; do not only train longer.

## Best Next Candidate

Two lanes are active:

1. L40S lane: postprocess the existing ResNet/FPN checkpoint, validate, audit, then decide whether it deserves a submission.
2. Existing RunPod lane: overnight non-PM1 U-Net/ResNet/TinyViT runs. PM1 neighbor-sum is demoted to analysis/ensemble-diversity only.

Completed full-data PM1 run on the existing RunPod:

```text
existing_unet_pm1bce_nsum_summary_full_e30_m5
```

Monitor:

```bash
scripts/runpod_exec.sh 'tail -n 80 results/subtask1/vision_runs/existing_unet_pm1bce_nsum_summary_full_e30_m5/nohup.log'
```

Submission result:

- ZIP: `results/subtask1/submissions/existing_unet_pm1bce_nsum_summary_full_e30_m5.zip`
- Validation Accuracy +/- 1: `0.80566`
- CodaBench score: `41.83`
- Conclusion: do not submit this model family standalone again. The neighbor-sum PM1 objective is locally attractive but leaderboard-poor.

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
