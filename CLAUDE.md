# CLAUDE.md — AI4Agri

## Competition

ImageCLEF 2026 AI4Agri — two subtasks using satellite imagery for agricultural ML.

- **Subtask 1 (AgriPotential):** Pixel-level ordinal regression (5 classes) on Sentinel-2 time series. Metric: Accuracy±1. Submit ZIP to CodaBench.
- **Subtask 2 (DACIA5):** Crop classification from optical + SAR patches. Two tracks (7-class temporal generalization; 2-class early detection). Submit Colab notebook + 3-page report.

## Data Notes

- Subtask 1 patches: 34 timeframes × 10 bands × pixel grid — treat as (T, C, H, W) tensors
- Subtask 2 patches: 32×32 pixels, optical (12 bands) and SAR (2 bands) separate
- Do not commit raw data — use `data/` dirs which are gitignored

## Current Repo Conventions

- Operational scripts live in `scripts/`.
- Notebooks live in `notebooks/` and are exploratory test beds, not workflow runners.
- Keep notebooks synced with the configured aliases: `nbpair`, `nbsync`, `nbopen`, `nbrun`.
- Submission artifacts go under `results/subtask1/` or `results/subtask2/`.
- Use `results/subtask1/submissions/` for CodaBench ZIPs.
- Do not commit raw data or bulky generated artifacts; follow `.gitignore`.
- Use `CHATGPT_PLAN.md` for active task state and `ARCHITECTURE.md` for pipeline layout.

## Metric Targets

- Subtask 1: Accuracy±1 — ordinal structure matters; off-by-one is fine
- Subtask 2 Ch1: Q1 = 0.5×AA + 0.5×OA — balanced class accuracy matters
- Subtask 2 Ch2: Q2 = 0.5×Acc(winter wheat) + 0.5×Acc(alfalfa)
