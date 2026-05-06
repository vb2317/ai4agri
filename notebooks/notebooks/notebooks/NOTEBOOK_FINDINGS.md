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

### Class distribution (6329 training patches)

| Class | Label | Pixel count | Fraction |
|-------|-------|-------------|----------|
| 0 | Very Low | 38,507,107 | **37.1%** |
| 1 | Low | 15,416,308 | 14.9% |
| 2 | Medium | 12,788,160 | 12.3% |
| 3 | High | 15,201,738 | 14.7% |
| 4 | Very High | 11,234,481 | 10.8% |
| 5 | Unknown (nodata) | 10,546,542 | 10.2% |

### Implications

- **Class 0 dominates at 37.1%, not class 2.** The constant-class-2 baseline (39.52) is suboptimal. Predicting class 0 everywhere hits classes 0+1 = ~52% Acc±1 on the train distribution — a potential free +12pp over the submitted constant baseline if test has a similar prior. Worth a 1-submission probe.
- **Class 5 is nodata/boundary (10.2%).** Must be excluded from training targets and not counted in scoring. The `KeyError: 5` crash in the temporal profiles cell was this class leaking through — fixed by adding `if majority_cls not in class_profiles: continue`.
- **Classes 1–4 are roughly balanced (10–15%).** No severe tail problem on the real ordinal classes. Class imbalance is entirely class 0 vs the rest.
- **Prior calibration direction:** Any class-prior recalibration step should weight toward class 0, not class 2. The WIN_PLAN Layer A1 assumption (calibrate toward class 2) needs revisiting.

### Pending

- Temporal profiles plot (`temporal_profiles.png`) — tells us which bands/months separate classes.
- Spatial scatter plot — tells us whether train and test patches are in the same region (val→test shift diagnosis).

---

## 06_advanced_features.ipynb

Not yet run.
