# AI4Agri 2026 — Plan To Win

Last updated: 2026-05-05 (T-2 to Subtask 1 deadline May 7; T-23 to Subtask 2 deadline May 28).

This document is the synthesis between the aspirational strategy in `notebooks/00_strategy.ipynb`
and the operational reality recorded in `CHATGPT_PLAN.md`, `Next.md`, and the leaderboard so far.
It is opinionated about where to spend the remaining time and submission budget.

## 1. Reading the existing material

### 1.1 What `notebooks/00_strategy.ipynb` commits to

NB00 is the master strategy doc. It targets **val Acc±1 ≥ 0.92** via eight stacked techniques:

| # | Technique | Notebook | Claimed gain |
|---|---|---|---|
| 1 | Vegetation indices (NDVI/NDRE/GCVI/EVI/SAVI/MSAVI/NDWI/PRI/RE-NDVI) | NB6 | +5–8% |
| 2 | Phenology + Fourier features (peak DOY, integrated NDVI, growing season, harmonics) | NB6 | +2–4% |
| 3 | CORN ordinal head on a U-Net (loss matches Acc±1) | NB7 | +2–3% |
| 4 | Pseudo-labelling on the 800 unlabeled test patches (2 rounds) | NB9 | +1–3% |
| 5 | 5-model ensemble (LightGBM + 2× U-Net variants + CORN U-Net + pseudo model) | NB10 | +2–3% |
| 6 | Expected-value decoding instead of argmax | NB10 | +1–3% |
| 7 | D4 TTA on U-Net models | NB10 | +1–2% |
| 8 | 5×5 median filter on predicted masks | NB4/NB10 | +1–2% |

NB1–NB10 form a working pipeline (`01 → 06 → 02 → 05` for the floor; then `03,07 → 09 → 10`).
The notebooks are present and structurally complete. They are not yet wired to scripts and
have not been executed end-to-end.

### 1.2 What has actually been submitted to CodaBench

| Submission | Type | Acc±1 (CodaBench) |
|---|---|---|
| Constant class 2 | floor | **39.52** |
| Sampled-pixel HGB (default) | model | 39.74 |
| Overnight HGB, uniform sampling, raw-temporal features, 200k px, seed 43 | model | **40.16** |
| Existing U-Net CE summary rand e10 (`existing_unet_ce_summary_rand_e10_p1024_v256_m5.zip`) | model | 45.96 |
| L40S ResNet/FPN summary e30 | model | 47.6 |
| L40S TinyViT summary soft full e30 seed 52 | model | **50.63** ← current floor |

Unsubmitted validation candidates under review:

| Candidate | Val Acc±1 | Notes |
|---|---:|---|
| `existing_unet_pm1bce_nsum_summary_rand_e10_p1024_v256_m5` | 0.792395 | PM1 multi-hot BCE + sigmoid neighbor-sum; predicts only classes 1..3 by decoder behavior |
| `existing_unet_pm1bce_softnsum_summary_rand_e10_p1024_v256_m5` | 0.786270 | PM1 multi-hot BCE + softmax neighbor-sum |
| `existing_unet_pm1bce_nsum_summary_full_e30_m5` | running | Full-data version of the stronger PM1 setup |

Best **val** Acc±1 for that overnight run was 0.72604 — the test scores are ~32 points below
val. That gap is the single most important fact for planning.

### 1.3 Subtask 2 state

Tabular leakage-free baselines exist on RunPod:

- Problem 1 (7-class temporal generalisation): HGB, 2023 holdout, **Q=0.6655** (OA 0.7442, AA 0.5867).
- Problem 2 (early winter wheat vs alfalfa): ExtraTrees, 2024 holdout, **Q=0.8102** (OA 0.8308, AA 0.7896).

Sentinel-2 12-band order is **not yet confirmed** — vegetation indices are blocked until it is.
Final deliverable is a Colab notebook (or zipped source + README) **plus a 3-page report**, by
email by May 28.

### 1.4 Diagnosis: why are NB00 and the leaderboard so far apart?

Plausible causes for the val 0.72 vs test 0.40 gap, ranked by how much they would change strategy:

1. **Geographic / domain shift between the train+val region and the test region.** 6329 train
   patches cover the same raster, but `test.csv` may pull from a very different location or
   acquisition window. NB1's "spatial distribution by majority class" plot is the place to
   verify this; nobody has run it end-to-end.
2. **Class prior shift.** The constant-class-2 baseline scores 39.52, so class 2 alone covers
   ~40% of test pixels with ±1 tolerance. If train is heavier on classes 1/2/3 and test is
   heavier on extremes, a model tuned to val will under-predict the tails on test.
3. **No-data / cloud handling.** Sentinel-2 rasters often have nodata sentinel values; if those
   leak into the temporal mean/std features, train and test get systematically different
   feature scales.
4. **Different patch_size or window alignment between train and test.** Less likely (the loader
   is shared) but worth a 1-line check before believing any val number.

The implication is that the NB00 plan as written is risky: it targets val Acc±1 and most of
its gains can evaporate on test if the train/test shift is not addressed. **Any
val-only improvement under +5pp should be treated as noise relative to the ~30pp val→test
gap.** We need either a leaderboard probe per change or an out-of-fold / spatial CV setup
that mirrors the test shift.

## 2. The strategy I commit to

### 2.1 Win condition

- **Subtask 1:** Final test Acc±1 strictly above 50.63 by EOD May 6 (UTC), with at least one
  fallback submission already on the leaderboard.
- **Subtask 2:** A clean Colab notebook + 3-page report with current tabular baselines as the
  floor (Q=0.66 / Q=0.81), and at least one improved Problem-1 model (target Q ≥ 0.72).

### 2.2 Priorities

Subtask 1 first because it has live leaderboard feedback and the deadline is in 2 days.
Subtask 2 work resumes after the Subtask 1 May 7 freeze.

### 2.3 Subtask 1 — three execution layers, run in parallel

The plan is **NOT** "blindly execute NB00 top-to-bottom". Given the val→test gap, we treat
each layer as an independent leaderboard probe. Each layer ships its own ZIP that we are
willing to submit. We always keep the previous-best as the floor.

**Layer A — Distribution-shift fixes on the existing HGB winner (Day 1 morning, ≤2 hr).**
Lowest risk, fastest to ship. Expected: +0.3 to +1.0 Acc±1 on test.

- A1. Add **class-prior calibration**: re-weight the HGB output probabilities to match the
  empirical test class distribution. Since labels are hidden, use the constant-class-2 score
  (39.52) plus per-class neighbour PNG submissions we already have to back out an approximate
  test prior; otherwise default to the train prior on the validation patches that match
  `test.csv` `row,col` quadrants.
- A2. Switch to **expected-value decoding**: from HGB `predict_proba`, output
  `round(sum(k * p[k]))` instead of `argmax`. This is the single line in NB00 §2.2 and is the
  Acc±1-optimal decoder under symmetric uncertainty. Implement in `scripts/subtask1_baseline.py
  infer` behind a `--decode {argmax,expected}` flag.
- A3. **5×5 median filter** on the predicted masks before PNG write. One scipy call inside
  the inference loop.
- A4. **NoData scrub.** During feature build, set Sentinel-2 reflectance below 0 or above
  10000 to NaN, then `nan_to_num` after temporal aggregation. Prevents single bad timeframes
  from polluting the temporal-mean/std features.

These are independent and additive. Submit at most one A-layer ZIP first; if it improves on
40.16, roll the others in and submit a second.

**Layer B — Domain-aware features and ordinal model (Day 1 afternoon → Day 2 morning, ~6 hr).**
Medium risk; this is the part of NB00 that targets actual signal, not just decoding.

- B1. Run NB6 on RunPod to cache **vegetation indices and phenology features** for all 7,910
  patches. The cache estimate in NB6 §7 says ~12 GB if we keep summary statistics. 9 indices
  × `{mean, std, p10, p50, p90}` = 45 features per band-equivalent, plus 8 phenology +
  5 harmonic features ≈ 58 per pixel. Wire this into `scripts/subtask1_baseline.py` as a
  `--features {raw_temporal, indices_phenology}` mode.
- B2. **Ordinal regressor head**: replace HGB classifier with HGB regressor on the integer
  label and round to nearest integer. This trains on the actual ordinal target and works for
  free with sklearn. Compare to the existing classifier on val *and* on a leaderboard probe.
- B3. **Bigger pixel budget + multi-seed bag.** Current best is 200k pixels, single seed.
  Bag 5 seeds × 400k pixels each, average soft predictions. This is the cheapest ensemble
  available and the suite scaffolding (`scripts/run_subtask1_experiments.py`) already
  supports seed sweeps.

Submit one B ZIP only after Layer A has at least confirmed an improvement; otherwise the
B improvements may be hidden by the same shift problem.

**Layer C — Spatial model + ensemble (Day 2, ~12 hr GPU).**
Higher risk for the deadline, higher ceiling. Only run if Layer A + B together give us a
reproducible test gain.

- C1. **U-Net `summary` variant** from NB3 with **soft ordinal labels** (eps=0.1). Train 30
  epochs on the indices+phenology cache, batch 8, AdamW 1e-3 cosine. Save val
  probabilities as `.npz` for stacking.
- C2. **CORN ordinal U-Net** from NB7. Same training budget, different head; this is the
  diversity component.
- C3. **Stacked ensemble** in NB10: weighted soft-prob average of {best HGB regressor,
  U-Net summary, CORN U-Net}, weights tuned on val. Apply expected-value decoding + median
  filter + (U-Nets only) D4 TTA at inference.
- C4. **Pseudo-labelling** (NB9) is **deferred** unless C1/C2 already beat 40.16 on test. With
  a 30pp val→test gap, pseudo-labels generated from val-overfit predictions will amplify
  that bias rather than correct it.

### 2.4 Submission gating (preserve the leaderboard floor)

- Floor: `results/subtask1/submissions/l40s_tiny_vit_summary_soft_full_e30_s52.zip`
  (50.63). We never submit a ZIP that fails `validate_submission_zip.py --subtask1-codabench
  --check-class-values --expected-ids-file data/subtask1/test.csv`.
- PM1-loss candidates must pass `notebooks/12_accuracy_pm1_review.ipynb` visual review:
  red pixels in the Accuracy +/- 1 map should be localized, and edge classes 0/4 should
  mostly map to adjacent classes 1/3 rather than crossing by more than one class.
- Submission budget: today (May 5) and tomorrow (May 6) we have 20 daily submissions plus
  whatever remains of the 100 total. Spend 1 submission on Layer A, 1 on Layer B, up to 2 on
  Layer C variants. Keep ≥ 4 in reserve for final-day rebuilds.
- Every submission writes a row to `results/runs.csv` with the validated ZIP path, val
  metrics, and CodaBench score.

### 2.5 Subtask 2 — between May 8 and May 28

After Subtask 1 freezes, the plan is:

- **Confirm Sentinel-2 12-band order** for DACIA5 patches. This unblocks NDVI/NDRE/etc. and
  is currently the single biggest gap. Inspect `Legend_crops.pdf` and one full GeoTIFF
  header (`gdalinfo`) to confirm whether bands are stored in the standard `m-sakka` order
  or the Sentinel-2 L2A native order.
- **Problem 1 (7-class temporal generalisation):** keep the leakage-free split (train years,
  hold out 2024) and add (a) vegetation indices over all available dates, (b) per-month
  aggregations, (c) a 1D-CNN or LightGBM-on-temporal-stats model. Target Q ≥ 0.72.
- **Problem 2 (winter wheat vs alfalfa, March only):** ExtraTrees already at Q=0.81. Add
  March-window VIs and re-run; target Q ≥ 0.84. Keep the model very simple — the report
  needs to be defensible in 3 pages.
- **Notebook:** strip `notebooks/subtask2_submission.ipynb` to a single Colab-runnable
  pipeline that re-creates manifest → features → train → predict for both problems.
- **Report:** 3 pages — problem statement, leakage controls, feature design, results table
  with confusion matrices, error analysis, and reproduction commands. Already scaffolded at
  `reports/subtask2_technical_report.md`; flesh out after the new model lands.

## 3. Notebook assessment — what to keep, fix, or skip

| Notebook | Use it? | Action |
|---|---|---|
| `00_strategy.ipynb` | Yes, as the strategy reference | Keep; this WIN_PLAN.md restates which parts to actually run. |
| `01_eda_subtask1.ipynb` | Run once on RunPod | Critical: the spatial scatter + temporal profiles tell us whether a train→test shift exists. Run **first**. |
| `02_pixel_baseline_subtask1.ipynb` | Skip running directly | Codex equivalent already exists in `scripts/subtask1_baseline.py`. Use the script; keep notebook for figures. |
| `03_unet_subtask1.ipynb` | Use only for Layer C | Needs to be wired to feature cache from NB6. |
| `04_ensemble_postprocess_subtask1.ipynb` | Use for Layer C | Useful α grid + median-filter logic — port the median filter into `scripts/subtask1_baseline.py infer` for Layer A. |
| `05_inference_submit_subtask1.ipynb` | Mirror logic into the script | The script-based inference path is what VB submits; notebook is a presentation copy only. |
| `06_advanced_features.ipynb` | **Run this on RunPod** | Highest-leverage notebook still un-run. Cache features for Layer B/C. |
| `07_corn_ordinal_unet.ipynb` | Layer C only | Risk: extra training time. Diversity-only justification. |
| `09_pseudo_labeling.ipynb` | **Defer** | Only valuable if val→test shift is closed. Otherwise it amplifies bias. |
| `10_final_stack.ipynb` | Layer C only | Use for the final ensemble submission. |
| `subtask1_testbed.ipynb` / `.py` | Keep | Already does what it should; presentation/inspection. |
| `subtask2_testbed.ipynb` / `.py` | Keep | Same. |
| `subtask2_submission.ipynb` / `.py` | Yes — extend | This is the actual deliverable for Subtask 2. Convert to Colab-runnable end-to-end. |

The pipeline notebooks (NB1–NB10) were authored as an experimental track but the actual
shipped pipeline lives in `scripts/`. The right move is to keep the notebooks as
presentation/figures, port the few high-leverage cells (median filter, expected-value
decoder, indices+phenology) into the script pipeline, and only fall back to running a
notebook end-to-end for the U-Net training (NB3/NB7) since there is no script equivalent.

## 4. Concrete next 48 hours — hour-by-hour

### Day 1, May 5 (today)

| Block | Owner | Action | Artifact |
|---|---|---|---|
| 0–1 hr | Codex | Add `--decode expected` and `--median-filter 5` flags to `scripts/subtask1_baseline.py infer` | code change, smoke run |
| 0–1 hr | Codex (parallel) | Add NoData scrub (`<0` and `>10000` → NaN) to feature builder | code change |
| 1–2 hr | VB on RunPod | Re-infer the existing 200k-seed-43 model with `--decode expected --median-filter 5`, validate ZIP | ZIP A1 |
| 2–3 hr | VB | Submit A1 ZIP to CodaBench, record score in `Next.md` and `results/runs.csv` | leaderboard score |
| 1–4 hr | Codex (parallel) | Run NB6 on RunPod to cache `indices_phenology` features for train/val/test | feature cache |
| 4–6 hr | Codex | Wire `--features indices_phenology` and HGB regressor option into `scripts/run_subtask1_experiments.py`; launch a small grid (2 seeds × {classifier, regressor} × {raw_temporal, indices_phenology}) | summary.csv |
| 6–8 hr | VB | If grid produces a candidate with val Acc±1 > 0.726 + median-filter test gain, submit Layer B ZIP | leaderboard score |
| 8–10 hr | Codex | Start NB3 U-Net `summary` training on cached indices_phenology features, batch 8, 30 epochs, save val probs | unet_best.pt + val_probs.npz |

### Day 2, May 6 (final day)

| Block | Owner | Action | Artifact |
|---|---|---|---|
| 0–4 hr | Codex | Train NB7 CORN U-Net, save val probs | corn_unet_best.pt + corn_val_probs.npz |
| 4–6 hr | Codex | NB10 stacking grid on val: HGB regressor + U-Net summary + CORN U-Net | best_config.json |
| 6–8 hr | Codex | Test inference with the stack, D4 TTA on U-Nets, expected-value decode, 5×5 median filter | ZIP C1 |
| 8–10 hr | VB | Submit ZIP C1, record score | leaderboard score |
| 10–12 hr | All | If C1 beats Layer B, optionally submit a no-TTA variant as a robustness check; otherwise stop | leaderboard score |
| 12+ hr | All | Freeze submission. Pull all artifacts locally, commit, push branch. | clean git state |

### Day 3, May 7

Submission deadline. Only act if VB needs to re-upload a previously validated ZIP. No new
training runs.

## 5. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Layer A produces no leaderboard improvement (val→test shift dominates everything) | Medium | Run NB1 EDA *first*; if test patches are spatially distinct, build a within-train spatial CV that mimics it before training Layer C models. |
| RunPod data missing (Mode B redownload) | Medium | Mode B path is documented in `Next.md`; budget ~6 hr for the 185 GB redownload; cuts Day 1 in half. Have Layer A ready to go from cached features if available. |
| U-Net training does not converge in 30 epochs | Low | NB3 default (`summary` mode, base_ch=32) fits in <8 hr on a single GPU; have NB3 with `concat` mode as fallback if `summary` underfits. |
| CodaBench daily limit hit | Low | We need ≤4 submissions; budget is 10/day. |
| Final ZIP fails validation 30 min before deadline | Low | Pre-validate every ZIP with `validate_submission_zip.py` before submission. Keep the 40.16 ZIP loaded in CodaBench as the floor at all times. |
| Subtask 2 band order remains unconfirmed past May 8 | Medium | Default to `m-sakka/agripotential` order (B1..B9 then B11/B12) and document the assumption in the report; do not block. |

## 6. Decision log entries to add when actions land

Each of these gets one line in `CHATGPT_PLAN.md`'s "Decision Log" once executed:

- A1+A2+A3 ZIP submitted with score X (Layer A).
- Indices+phenology feature cache built; B ZIP submitted with score X.
- U-Net summary trained, val Acc±1 = X.
- CORN U-Net trained, val Acc±1 = X.
- Final stack ZIP submitted with score X.
- Subtask 1 final standing recorded.
- Subtask 2 Sentinel-2 band order confirmed (or assumption documented).
- Subtask 2 Problem 1 / Problem 2 final Q recorded.
- Subtask 2 notebook + report submitted by email on May 28.

## 7. What this plan deliberately does NOT do

- **Does not commit to pseudo-labelling.** The val→test gap makes self-training risky; only
  enable it after the gap closes.
- **Does not chase ViT / temporal transformers.** They are NB8 (Tier C) territory and the
  May 7 deadline does not afford the training time.
- **Does not add Subtask 2 vegetation indices** until the band order is confirmed; the
  existing leakage-free baselines are the report floor.
- **Does not refactor the script/notebook split.** Notebooks remain test beds; scripts
  remain workflow runners; high-leverage cells (median filter, expected-value decode,
  indices+phenology, ordinal regression head) are *ported into the scripts* rather than
  promoted to notebook execution.
