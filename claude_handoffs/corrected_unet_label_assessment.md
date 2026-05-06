# Corrected-Label U-Net Assessment

Last updated: 2026-05-06

## Scope

This note covers the corrected-label Subtask 1 U-Net runs trained after the raw label fix:

- raw labels `1..5` are remapped to model classes `0..4`
- raw label `0` is ignored as nodata

These runs are the first U-Net results that should be treated as valid under the corrected label convention.

## Ranking By Validation Accuracy +/- 1

| Rank | Run ID | Setup | Best epoch | Acc +/- 1 | Exact | MAE | Notes |
|------|--------|-------|------------|-----------|-------|-----|-------|
| 1 | `corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache` | `pm1_bce`, `neighbor_sum_sigmoid`, median `5`, batch `32`, cached summary tensors | `6` | `0.8551415353` | `0.2689802622` | `0.8999029187` | Best pm1 run; strongest middle-class recall |
| 2 | `corrected_unet_pm1bce_softnsum_summary_full_e30_m5_s74_b64_cache_parallel` | `pm1_bce`, `neighbor_sum`, median `5`, batch `64`, cached summary tensors | `6` | `0.8411502577` | `0.2820150799` | `0.9117596675` | Slightly better exact accuracy, lower pm1 |
| 3 | `corrected_unet_pm1bce_nsum_summary_full_e30_m3_s75_b32_cache` | `pm1_bce`, `neighbor_sum_sigmoid`, median `3`, batch `32`, cached summary tensors | `1` | `0.8271882239` | `0.2580701805` | `0.9415628501` | Lower smoothing underperformed the median-5 run |

## Interpretation

- The best corrected-label U-Net is `corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache`.
- Batch `32` with cached summary tensors was the strongest configuration among the corrected runs.
- `neighbor_sum_sigmoid` with median `5` beat the median `3` variant on both Acc +/- 1 and MAE.
- `neighbor_sum` decode at batch `64` improved exact accuracy slightly, but it lost pm1 versus the best run.
- All three runs still collapsed the edge classes:
  - class `0` recall: `0.0`
  - class `4` recall: `0.0`
  - classes `1..3` carried almost all of the predictive mass

That means the corrected-label fix is real, but the current U-Net recipe still needs boundary-class work before it is a strong final candidate.

## Important Caveat

The current repo summary file `results/runs.csv` records `0.8302152249` for `corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache`, but the run's `metrics.json` on RunPod reports `0.8551415353`.

Treat the run-level `metrics.json` as authoritative until the discrepancy is reconciled.

## Recommended Next Step

- Keep `corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache` as the reference corrected-label U-Net result.
- If spending more GPU time, test class weighting or a decode/postprocess change rather than repeating the same neighbor-sum recipe.
- Pull the visuals for the top two runs before deciding whether the best corrected-label model is submission-worthy.

## Source Paths

- `results/runs.csv`
- Remote run metrics on RunPod:
  - `results/subtask1/vision_runs/corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache/metrics.json`
  - `results/subtask1/vision_runs/corrected_unet_pm1bce_softnsum_summary_full_e30_m5_s74_b64_cache_parallel/metrics.json`
  - `results/subtask1/vision_runs/corrected_unet_pm1bce_nsum_summary_full_e30_m3_s75_b32_cache/metrics.json`
