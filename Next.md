# Next

## Now (Subtask 1 First)

- [ ] VB: submit the validated constant baseline ZIP to Subtask 1 CodaBench.
  - File: `results/subtask1/submissions/constant_class_2.zip`
  - Expected CodaBench target: AgriPotential / Subtask 1.
  - Do not rename files inside the ZIP.
  - After upload, record submission status, validation errors if any, score if available, and evaluation timing in this file.
- [ ] VB: confirm Subtask 1 CodaBench submission limits and evaluation timing.
  - Record daily/total submission cap.
  - Record whether scoring is immediate, queued, or delayed.
  - Record whether failed submissions count against the limit.
- [ ] VB: confirm RunPod global networking status before downloading AgriPotential rasters.
  - In RunPod Pod details/connectivity, confirm whether public internet egress is enabled.
  - If disabled, enable it or report the exact limitation.
- [ ] VB or RunPod operator: sync latest branch to RunPod at `/workspace/ai4agri`.
  - Branch: `codex/phase1-inspection-scripts`
  - Run `git pull` or use the repo sync helper from a machine with RunPod SSH access.
- [ ] VB or RunPod operator: download Subtask 1 CSVs and viticulture label raster first.
  - Run on RunPod:
    ```bash
    cd /workspace/ai4agri
    source .venv/bin/activate
    python scripts/download_subtask1_hf.py --out-dir data/subtask1 --skip-images
    ```
  - Confirm files exist: `metadata.csv`, `train.csv`, `val.csv`, `test.csv`, `viticulture.tif`.
- [ ] VB or RunPod operator: smoke-read one Subtask 1 patch with labels.
  - Run on RunPod:
    ```bash
    cd /workspace/ai4agri
    source .venv/bin/activate
    python scripts/inspect_subtask1.py \
      --data-dir data/subtask1 \
      --splits train val test \
      --limit 1 \
      --read-labels
    ```
  - Pull or paste the resulting label shape/counts and any error.
- [ ] VB or RunPod operator: download Sentinel-2 image rasters only if disk/time budget is acceptable.
  - Full image download is large.
  - Run on RunPod only:
    ```bash
    cd /workspace/ai4agri
    source .venv/bin/activate
    python scripts/download_subtask1_hf.py --out-dir data/subtask1
    ```
  - Record final disk usage with `du -sh data/subtask1`.
- [ ] VB or RunPod operator: train the sampled-pixel Subtask 1 baseline after image rasters are present.
  - Start with a smoke run:
    ```bash
    python scripts/subtask1_baseline.py train \
      --data-dir data/subtask1 \
      --patch-limit 20 \
      --val-patch-limit 5 \
      --pixels-per-patch 256 \
      --max-train-pixels 5000
    ```
  - If smoke run works, run the larger baseline:
    ```bash
    python scripts/subtask1_baseline.py train --data-dir data/subtask1
    python scripts/subtask1_baseline.py infer --data-dir data/subtask1
    python scripts/validate_submission_zip.py \
      --zip-path results/subtask1/submissions/subtask1_baseline.zip \
      --subtask1-codabench \
      --expected-ids-file data/subtask1/test.csv \
      --check-class-values
    ```
  - Record `metrics.json` exact accuracy, Accuracy +/- 1, MAE, and validation confusion matrix.
- [ ] VB: submit `results/subtask1/submissions/subtask1_baseline.zip` only after validation passes, then record CodaBench score/errors.

## Parked Until Subtask 1 Is Submitted

## Before May 28 (Notebook submission)

- [ ] Confirm DACIA5 patch label source before training Subtask 2 baseline.
- [ ] Baseline: Subtask 2 — run tabular script on RunPod after label source is confirmed.
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
- [X] Add Subtask 1 constant-mask CodaBench ZIP writer.
- [X] Add Subtask 1 Hugging Face downloader.
- [X] Add Subtask 1 sampled-pixel train/inference baseline script.
- [X] Add Subtask 2 manifest, feature extraction, and tabular baseline script.
- [X] Generate and locally validate Subtask 1 constant-mask ZIP with `800` PNG masks.
- [X] Sync repo files to RunPod at `/workspace/ai4agri`.
- [X] Verify RunPod Python/PyTorch/CUDA environment.
