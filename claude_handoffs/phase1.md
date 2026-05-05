# Claude Handoffs: 2026-05-05

## Priority

Focus on Subtask 1 AgriPotential today. It has immediate leaderboard feedback.

Current submitted scores:

- Constant class baseline: `39.52`
- First sampled-pixel baseline: `39.74`

Codex has an experiment runner that will compare:

- HistGradientBoosting vs ExtraTrees
- uniform vs class-balanced sampling
- raw vs raw-temporal features
- larger pixel budgets

## Needed From Claude

```text
Project: AI4Agri 2026 Subtask 1 AgriPotential.

Task:
Return a concise leaderboard-improvement memo for the current sampled-pixel baseline.

Current baseline:
- Input: 34 Sentinel-2 timeframes x 10 bands.
- Output: 5-class ordinal suitability mask.
- Metric: Accuracy +/- 1.
- Current CodaBench score: 39.74.
- Current code samples labeled pixels, trains scikit-learn HGB or ExtraTrees, and writes PNG masks.
- Current optimized code can use class-balanced sampling and raw_temporal features.

Needed output:
- Top 3 low-risk improvements Codex can implement in under 2 hours.
- Whether ordinal calibration, class-prior correction, or spatial smoothing is likely to help Accuracy +/- 1.
- Any official AgriPotential preprocessing details we might be missing:
  nodata handling, band order, temporal order, normalization/scaling, label semantics, or patch geometry.
- Any warning signs that validation Accuracy +/- 1 may not correlate with CodaBench leaderboard.

Constraints:
- Do not propose U-Net/ViT as the immediate next step unless the tabular/pixel path is exhausted.
- Keep the answer implementation-oriented and cite exact source/file names if used.
```

## Parked Claude Items

These remain useful but are lower priority today:

- DACIA5 Sentinel-2 12-band order.
- Subtask 2 report prose.
- Subtask 2 neural baseline recommendations.
