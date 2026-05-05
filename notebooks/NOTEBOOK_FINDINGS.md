# Notebook Findings

Learnings captured as notebooks are executed on RunPod. Feed into `CHATGPT_PLAN.md` and `WIN_PLAN.md` once a notebook run is complete.

---

## 00_strategy.ipynb

Run date: 2026-05-05. Remote: default RunPod.

### Data confirmed

- Train / Val / Test patches: `6329 / 781 / 800`
- Timeframes: `34` — columns: `filename`, `day`, `month`, `year`
- Patch columns: `patch_id`, `row`, `col`, `patch_size`, `n_annotated`

### Temporal distribution (timeframes per month)

| Month | Count |
|-------|-------|
| Jan | 3 |
| Feb | 1 |
| Mar | 2 |
| Apr | 2 |
| May | 1 |
| Jun | 3 |
| Jul | 5 |
| Aug | 4 |
| Sep | 3 |
| Oct | 5 |
| Nov | 2 |
| Dec | 3 |

**Peak months: July (5) and October (5). Sparse: February (1) and May (1).**

### Implications

- No single season dominates, so raw band averages miss the summer vigour vs winter bare-soil contrast.
- Phenology features (peak DOY, integrated NDVI, growing season length, Fourier harmonics) carry real signal — this validates running NB6 for Layer B.
- Sparse months (Feb, May) are under-represented; features from those months may be rarer but more discriminative.

### Pending

- Cell 10 (Acc±1 floor from class fractions) requires NB1 `eda_summary.json`. Re-run after NB1 completes.

---

## 01_eda_subtask1.ipynb

Run date: 2026-05-05. Remote: default RunPod.

### Temporal coverage

- Date range: **2017-01-03 → 2019-12-29** (3 years)
- Tile ID: `T31TEJ` (Sentinel-2 MGRS tile — southwestern France / Bordeaux region)
- All 34 filenames follow `T31TEJ_YYYY_MM_DD.tif`

### Class distribution (6329 training patches)

| Class | Label | Pixel count | Fraction |
|-------|-------|-------------|----------|
| 0 | Very Low | 38,507,107 | **37.1%** |
| 1 | Low | 15,416,308 | 14.9% |
| 2 | Medium | 12,788,160 | 12.3% |
| 3 | High | 15,201,738 | 14.7% |
| 4 | Very High | 11,234,481 | 10.8% |
| 5 | Unknown (nodata) | 10,546,542 | 10.2% |

Saved to: `results/subtask1/inspection/class_distribution.png`

### Temporal profiles (cell 9)

Only 5 patches sampled for class 0 — the `TEMPORAL_SAMPLE_LIMIT` loop exited early. Other classes may have had insufficient samples. Profiles saved to `results/subtask1/inspection/temporal_profiles.png` but interpret with caution given the low sample count.

### Spatial distribution (cell 11)

Plot saved to `results/subtask1/inspection/spatial_distribution.png`. Visual review needed to assess whether classes cluster geographically (key for diagnosing val→test shift).

### Band × timeframe correlation with label (cell 13)

Top 10 features by |Spearman ρ|:

| Rank | Timeframe | Date | Band | ρ |
|------|-----------|------|------|---|
| 1 | 11 | 2017-11-19 | B8A | 0.409 |
| 2 | 10 | 2017-11-14 | B8A | 0.403 |
| 3 | 11 | 2017-11-19 | B9 | 0.380 |
| 4 | 10 | 2017-11-14 | B9 | 0.373 |
| 5 | 16 | 2018-07-07 | B8 | 0.366 |
| 6 | 11 | 2017-11-19 | B4 | 0.365 |
| 7 | 12 | 2017-12-24 | B8A | 0.364 |
| 8 | 10 | 2017-11-14 | B4 | 0.360 |
| 9 | 12 | 2017-12-24 | B9 | 0.358 |
| 10 | 13 | 2018-01-28 | B8A | 0.348 |

Saved to: `results/subtask1/inspection/band_time_correlation.png`

### EDA summary JSON

Saved to `results/subtask1/inspection/eda_summary.json`. Class pixel fractions recorded (class 5 excluded):
`{0: 0.3714, 1: 0.1487, 2: 0.1233, 3: 0.1466, 4: 0.1083}`

### Key implications

**Class distribution:**
- Class 0 dominates at 37.1%. The constant-class-2 baseline (39.52) is suboptimal — predicting class 0 everywhere would hit classes 0+1 = ~52% Acc±1 on train distribution. Worth a 1-submission probe.
- Class 5 (Unknown, 10.2%) is nodata/boundary — already correctly excluded from training in `subtask1_baseline.py` via `valid_label_mask` (labels <= 4).
- Prior calibration should target class 0, not class 2. WIN_PLAN Layer A1 assumption needs updating.

**Band correlations:**
- Strongest signal is in **November–December (B8A, B9, B4)** — late-autumn/early-winter dates. This is when vineyard vegetation is senescing and bare soil becomes visible, creating the clearest suitability contrast.
- **B8A (red-edge)** is the single most correlated band — important for vegetation health discrimination.
- **July B8 (NIR)** is the only summer date in the top 10 — peak vigour signal is present but weaker than the autumn signal.
- Implication: **phenology features anchored around November–December will likely outperform raw band averages.** NB6 vegetation indices and phenology features are high priority.

**Temporal profiles:**
- Only 5 class-0 patches sampled — the early-exit condition fired because class 0 patches are abundant and the limit was hit immediately while other classes were undersampled. The temporal profiles plot may not be representative. Consider increasing `TEMPORAL_SAMPLE_LIMIT` or sampling more evenly per class.

---

## 06_advanced_features.ipynb

Section 6 profile sampling was bounded after a RunPod notebook run stalled at `164/6329` patches after roughly 3 minutes.

Change captured in the notebook:

- `PROFILE_SCAN_LIMIT = 700`
- `PROFILE_PATCHES_PER_CLASS = 8`
- label `5` is treated as nodata/boundary and ignored for majority-class profiling
- NDVI profile loading reads only red/NIR bands instead of the full 10-band stack
- cached output: `results/subtask1/features_eda/class_ndvi_profiles_sample.npz`

Interpretation: this section is now a quick visual intuition aid, not a full statistical profile. Increase the limits only when using local data or when a full slow profile is explicitly needed.

---

## 11_subtask1_visual_review.ipynb

Created to review script-produced Subtask 1 vision artifacts without rerunning training.

Key behavior:

- Loads a `RUN_ID` from `results/subtask1`.
- Shows class legend with nodata/boundary as a separate gray display class.
- Computes metrics from `val_probs.npz` while ignoring invalid/nodata pixels.
- Adds Accuracy +/- 1 maps:
  - green: exact
  - yellow: within one ordinal class
  - red: miss by more than one
  - gray: ignored

---

## 12_accuracy_pm1_review.ipynb

Created as a focused notebook for the competition metric.

Default run:

- `existing_unet_pm1bce_nsum_summary_rand_e10_p1024_v256_m5`

Validated local execution through the good-example and edge-example sections.

What it surfaces:

- Global exact, Accuracy +/- 1, miss `>1`, and MAE.
- Good examples with high Accuracy +/- 1.
- Good examples where exact accuracy is low but most errors are off by one.
- Edge-class examples where true class `0` maps to `1`, and true class `4` maps to `3`.
- Worst patches by Accuracy +/- 1.
- Local comparison table across all available `val_probs` artifacts.
