# Subtask 1 Leaderboard Memo: 2026-05-05

## Current Signal

- Current submitted floor: `40.16` from `hgb_uniform_temporal_200k_s43`.
- The strongest local validation signal is HGB with uniform pixel sampling and raw-temporal features.
- Class-balanced sampling underperformed uniform sampling in the overnight suite, so do not spend the next submission on another class-balanced variant unless later summaries contradict this.

## Recommended Next Move

Run the targeted suite added in `scripts/run_subtask1_experiments.py`:

```bash
python scripts/run_subtask1_experiments.py \
  --data-dir data/subtask1 \
  --suite targeted \
  --infer-best \
  --validate-best
```

This keeps the model family fixed and only varies pixel budget and seed:

- `hgb_uniform_temporal_300k_s48`
- `hgb_uniform_temporal_400k_s49`
- `hgb_uniform_temporal_500k_s50`
- `hgb_uniform_temporal_600k_s51`

Submit only if the generated ZIP validates and the validation metrics are plausibly different/better than the `40.16` run.

## Low-Risk Moves

1. Increase uniform sampled pixels before switching model family.
   - This directly tests whether `200k` pixels was under-sampling the training raster.
   - It is less risky than adding a neural pipeline because the existing inference/validation path is already proven.

2. Try multiple seeds around the same configuration.
   - Uniform sampling depends on sampled pixel distribution.
   - A small seed sweep can improve stability without changing the artifact format.

3. Keep raw-temporal features for HGB.
   - In the overnight suite, raw-temporal beat raw for comparable HGB variants.
   - This matches the dataset design: multi-temporal Sentinel-2 frames are core signal, not just independent bands.

## Defer For Now

- Spatial smoothing: defensible for suitability maps, but current validation is sampled-pixel based and does not measure spatial postprocessing. Add it only after pulling full validation masks or after a targeted run stalls.
- Ordinal calibration/rounding: useful if a regressor or probability model is added. Current classifier outputs hard classes, so calibration needs probability diagnostics before it is worth a submission.
- ExtraTrees: overnight ExtraTrees did not beat HGB. Keep it as a fallback if targeted HGB saturates.
- U-Net/ViT: higher implementation and runtime risk. Do not start before the targeted HGB sweep either improves the score or clearly stalls.

## Official Example Notes

Sources checked:

- Official package repository: https://github.com/MohammadElSakka/agripotential
- Dataset card: https://huggingface.co/datasets/m-sakka/agripotential
- AgriPotential paper excerpt found via ResearchGate: `AgriPotential: A Novel Multi-Spectral and Multi-Temporal Remote Sensing Dataset for Agricultural Potentials`

Findings:

- The official repository points users to a tutorial and CodaBench competition link but does not expose a special normalization or nodata rule in its README.
- The Hugging Face dataset exposes `metadata.csv`, `train.csv`, `val.csv`, and `test.csv` split rows with `patch_id`, `row`, `col`, `patch_size`, and `n_annotated`.
- The paper describes the ten Sentinel-2 bands used by AgriPotential as `B2`, `B3`, `B4`, `B5`, `B6`, `B7`, `B8`, `B8A`, `B11`, and `B12`.
- No checked official source indicates that our current direct raster-window approach is missing a mandatory preprocessing step. The next code risk is sampling/modeling, not file-format handling.
