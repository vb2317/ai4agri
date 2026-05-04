# Next

## Now (before May 7)

- [ ] VB: confirm Subtask 1 CodaBench submission limits and evaluation timing.
- [X] VB: launch RunPod On-Demand GPU Pod.
- [X] VB: confirm remote budget ceiling.
- [ ] VB: confirm RunPod global networking status.
- [ ] Download Subtask 1 data via Hugging Face (`m-sakka/agripotential`) on remote.
- [X] Download Subtask 2 data from Zenodo on remote.
- [X] Run `scripts/inspect_subtask1.py` and `scripts/inspect_subtask2.py` on actual data.
- [ ] Confirm DACIA5 patch label source before training Subtask 2 baseline.
- [ ] Baseline: Subtask 2 — tabular patch features + ExtraTrees/HistGradientBoosting.
- [ ] Baseline: Subtask 1 — sampled-pixel ordinal model.
- [ ] Submit baseline predictions to CodaBench (Subtask 1)

## Before May 28 (Notebook submission)

- [ ] Subtask 1: improve model — U-Net or ViT on multi-temporal stack
- [ ] Subtask 2 Challenge 1: temporal model (LSTM / Transformer) on patch sequences
- [ ] Subtask 2 Challenge 2: early detection with March-only features
- [ ] Write 3-page technical report for Subtask 2
- [ ] Clean notebook for Subtask 2 Colab submission

## Later

- [ ] Ablation: which Sentinel-2 bands matter most for each task
- [ ] Ensemble strategies across temporal frames

## Completed

- [X] Confirm ImageCLEF/CLEF registration status.
- [X] Confirm CodaBench access for Subtask 1.
- [X] Confirm Subtask 1 CodaBench ZIP structure and file naming rules.
- [X] Add Subtask 1 CodaBench validator mode.
- [X] Research AgriPotential loader and DACIA5 data format.
- [X] Add data inspection scripts for both subtasks.
- [X] Add Subtask 2 manifest, feature extraction, and tabular baseline script.
- [X] Sync repo files to RunPod at `/workspace/ai4agri`.
- [X] Verify RunPod Python/PyTorch/CUDA environment.
