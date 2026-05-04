# VB Handoffs: Phase 1

## Subtask 2 Baseline Review

Codex produced the first leakage-free DACIA5 tabular baselines on RunPod.

Tracked local summaries:

- `results/subtask2/inspection/subtask2_baseline_summary.json`
- `results/subtask2/inspection/subtask2_feature_summary.json`
- `results/subtask2/inspection/subtask2_label_inspection.json`

Current metrics:

- Problem 1, HistGradientBoosting, 2023 holdout: `Q=0.6655`, `OA=0.7442`, `AA=0.5867`.
- Problem 2, ExtraTrees, 2024 holdout: `Q=0.8102`, `OA=0.8308`, `AA=0.7896`.

Notes:

- APIA crop code is used only to derive labels.
- APIA code and patch index are excluded from model features.
- Subtask 2 final packaging is still pending Claude/VB confirmation.

## Subtask 1 Data Decision

Small CSV files are already downloaded on RunPod:

```bash
/workspace/ai4agri/data/subtask1/agripotential
```

This includes `train.csv`, `val.csv`, `test.csv`, and `metadata.csv`.

Full raster download is still pending because it is large. When ready, run on RunPod:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/download_subtask1_agripotential.py --out-dir data/subtask1/agripotential --labels --images
```

After it finishes, tell Codex to run:

```bash
python scripts/inspect_subtask1.py \
  --data-dir data/subtask1/agripotential \
  --splits train val test \
  --limit 1 \
  --read-pixels \
  --read-labels
```
