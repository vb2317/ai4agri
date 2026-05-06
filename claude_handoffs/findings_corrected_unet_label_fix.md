# Corrected-Label U-Net Findings

Status: Done.

Reference note:

- `results/subtask1/inspection/corrected_unet_label_assessment.md`

Summary:

- The strongest corrected-label U-Net run is `corrected_unet_pm1bce_nsum_summary_full_e30_m5_s73_b32_cache`.
- Its authoritative run-level metrics are `accuracy_pm1=0.8551415353`, `exact_accuracy=0.2689802622`, `mean_absolute_error=0.8999029187`, with best epoch `6`.
- The nearest alternatives are:
  - `corrected_unet_pm1bce_softnsum_summary_full_e30_m5_s74_b64_cache_parallel` at `accuracy_pm1=0.8411502577`
  - `corrected_unet_pm1bce_nsum_summary_full_e30_m3_s75_b32_cache` at `accuracy_pm1=0.8271882239`
- All corrected-label U-Net runs still have zero recall for classes `0` and `4`, so the label fix is necessary but not sufficient.
- The repo summary file still shows `0.8302152249` for the best run, so there is a metrics mismatch to reconcile before any downstream report cites a single source of truth.

Recommended handling:

- Use the assessment note as the canonical reference for future Subtask 1 discussions.
- Prefer `metrics.json` from the run directory over the stale `results/runs.csv` value when comparing corrected-label U-Net runs.
