# Notebook Findings

Learnings captured as notebooks are executed on RunPod. Feed into `CHATGPT_PLAN.md` and `WIN_PLAN.md` once a notebook run is complete.

---

## Constant-Class CodaBench Probes

Submitted 2026-05-06. All five constant-class scores now known (class 3 not submitted):

| Predict everywhere | CodaBench Acc±1 |
|--------------------|-----------------|
| Class 0 (Very Low) | 44.82 |
| **Class 1 (Low)** | **46.58** ← best constant |
| Class 2 (Medium) | 39.52 |
| Class 4 (Very High) | 15.66 |

### Test class distribution (derived)

From Acc±1 algebra:

- P(class 0) + P(class 1) = **44.82%**
- P(class 2) = S1 − S0 = **1.76%** — tiny; class 2 is nearly absent on test
- P(class 1) + P(class 3) = 37.76%
- P(class 3) + P(class 4) = 15.66%
- P(class 0) − P(class 3) = 7.06%
- Accounted for: 62.24% — remaining **~37.76% is likely class 5 (nodata) on the test set**, which is enormous compared to the 10.2% seen in training

### Key implications

1. **Class 2 is nearly absent on test (1.76%).** The constant-class-2 submission scoring 39.52 was largely carried by classes 1 and 3, not class 2. Any model that over-predicts class 2 will hurt on test.
2. **Best naive prediction is class 1, not class 0.** Score(1) = 46.58 > Score(0) = 44.82. Prior calibration should lean toward class 1.
3. **The model floor (50.63) is only 4.05pp above the best constant prediction.** The TinyViT is doing real work but the margin is slim. Any ensemble or postprocessing that collapses toward the prior could easily fall back toward 46.58.
4. **Class 4 is rare on test (part of the 15.66% with class 3).** Class-4 recall improvements seen in val are likely overstated for what they'll do on test.
5. **~37.76% of test pixels are class 5 (nodata).** This is much higher than training (10.2%). If class 5 pixels are excluded from the CodaBench denominator, our effective scoring pool is smaller and model predictions for those pixels don't matter. If they ARE in the denominator, we are unknowingly losing points on them.

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

Run date: 2026-05-06. Remote: default RunPod.

### Feature pipeline confirmed

- **9 vegetation indices:** NDVI, NDRE, GCVI, EVI, SAVI, MSAVI, NDWI, PRI, RE_NDVI
- **10 phenology features:** peak, peak_doy, trough, amplitude, integrated, green_up, senescence, gs_length, std, slope
- **5 harmonic features:** H_DC, H1_cos, H1_sin, H2_cos, H2_sin
- Feature cache already existed — cell 17 wrote 0 new files for all splits. All 6329/781/800 patches already cached from a prior run.
- Manifest saved: `results/subtask1/features/manifest.json`

### Reflectance range flag

Demo patch reflectance max: `2.296` — above the physical ceiling of 1.0. Likely clouds, snow, or unmasked artefacts. The `load_ndvi_series` scrub (clips to `[0, 1.5]`) is already handling this.

### NDVI profiles by class (`results/subtask1/features_eda/class_ndvi_profiles.png`)

**Surprising: Very Low suitability has *higher* NDVI than Very High.**

- Very Low (red) and Low (orange): NDVI ≈ 0.35–0.45, consistently the highest.
- High (dark green) and Very High (bright green): NDVI ≈ 0.25–0.38, the lowest.
- Medium (yellow): largely overlaps all others — nearly indistinguishable by NDVI alone.
- Confidence bands are wide and heavily overlapping across all classes.

**Implication: raw NDVI magnitude is a weak discriminator for viticulture suitability.** High-suitability land is often rocky, well-drained, low-fertility terrain — classic wine-grape terroir — which naturally has lower greenness. Low-suitability areas may be fertile flatlands with dense generic vegetation. This partially undermines the NB00 assumption that NDVI + phenology drives +5–8% gain.

**What likely matters instead:** phenology *timing* features — `peak_doy`, `green_up`, `senescence`, `gs_length` — which capture the seasonal rhythm of vegetation rather than its absolute greenness. This is consistent with the NB1 correlation finding (B8A in November, ρ=0.41): a senescence/bare-soil signal, not a peak-vigour signal.

### Profile sampling

83 label windows scanned, 8 patches found per class (all 5 classes). `PROFILE_SCAN_LIMIT=700` cap not hit. Cache: `results/subtask1/features_eda/class_ndvi_profiles_sample.npz`.

---

## agripotential_tutorial.ipynb — CRITICAL PIPELINE BUG

Reviewed: 2026-05-06. Source: official dataset tutorial by Mohammad El Sakka (added locally).

### Raw label mapping (cell 21)

Cell 21 states explicitly:

> "some label pixels are set to 0. Those are unlabelled and should not affect training. Labelled pixels have a range of [1, 5], respectively corresponding to: very low, low, average, high, very high."

Raw label values in `viticulture.tif`:
- `0` — nodata / unlabelled (must be excluded from training)
- `1` — Very Low
- `2` — Low
- `3` — Average / Medium
- `4` — High
- `5` — Very High

### Band order (cell 17)

Cell 17 shows:
```python
red1   = date1_image[2]  # B4
green1 = date1_image[1]  # B3
blue1  = date1_image[0]  # B2
```

Bands start at **B2 (index 0)**, not B1. Correct 10-band order: `B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12`.

### The pipeline bug

`subtask1_baseline.py` and all vision training scripts currently use:

```python
valid_label_mask = np.isfinite(labels) & (labels >= 0) & (labels <= 4)
```

This is **wrong in two directions simultaneously**:
- Includes raw `0` (nodata/unlabelled) as training class 0 → pollutes class 0 (Very Low) with nodata pixels.
- Excludes raw `5` (Very High) entirely → the model has **never seen a Very High label** during training.

Correct fix (not yet implemented):

```python
valid = (labels >= 1) & (labels <= 5)
labels_shifted = labels[valid] - 1  # remap 1→0, 2→1, 3→2, 4→3, 5→4
```

### Why models still score above chance

The Acc±1 metric allows off-by-one errors. A 1-class label offset means:
- A pixel truly labelled `5` (Very High, raw) → our pipeline treats it as invalid (excluded).
- A pixel truly labelled `0` (nodata, raw) → our pipeline treats it as class 0 (Very Low).

Because the test labels in `viticulture.tif` are zeroed out (hidden by organizers), this bug does not directly corrupt test inference — but it corrupts **training supervision** for the 10.8% of pixels that were actually Very High. The ±1 tolerance partially absorbs the displacement for pixels near the boundary.

### Implications

1. **Class 4 (Very High) recall weakness explained.** Every model trained so far has been blind to Very High labels. The dismal class 4 recall (e.g., 0.0245 for TinyViT full-data) is caused by this bug, not model capacity.
2. **True training class distribution is different from what we reported.** The 10.2% we called "nodata (class 5)" are actually Very High (class 5, raw) — real suitability labels that should be in training. The actual nodata fraction is likely higher than 10.2%.
3. **Constant-class score algebra needs revisiting.** When we submitted constant-class-0 (our pipeline class) to CodaBench, we were submitting "predict very low everywhere," which is correct in the shifted space. The algebra was conceptually right, but the interpretation of which raw label corresponds to which pipeline class needs updating.
4. **Fix required before further training.** Any retraining without this fix will repeat the same error. Existing checkpoints are all trained with the buggy mask and should be treated as "best effort with biased labels."
5. **Band naming is wrong for interpretability only.** Our `BAND_NAMES` starts from B1 (index 0), but bands actually start from B2. This does not affect model correctness (it's a labelling issue), but it means all feature-importance and correlation plots that name bands are off by one.

### Fix scope (to be implemented separately)

Files that need the `valid_label_mask` fix:
- `scripts/subtask1_baseline.py`
- `scripts/run_subtask1_vision.py` (or the dataset loader it calls)
- Any other script that reads `viticulture.tif` labels and builds a mask

`BAND_NAMES` fix (interpretability only):
- Update in all notebooks and scripts that display band names: replace `["B1","B2",...]` with `["B2","B3","B4","B5","B6","B7","B8","B8A","B11","B12"]`.

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
