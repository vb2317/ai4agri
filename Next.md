# Next

## Now (Subtask 1 First)

- [X] VB: submit the validated constant baseline ZIP to Subtask 1 CodaBench.
  - File: `results/subtask1/submissions/constant_class_2.zip`
  - Expected CodaBench target: AgriPotential / Subtask 1.
  - Do not rename files inside the ZIP.
  - After upload, record submission status, validation errors if any, score if available, and evaluation timing in this file.
 
  > validated the submission, it received a accuracy score of 39.52

- [X] VB: confirm Subtask 1 CodaBench submission limits and evaluation timing.
  - Record daily/total submission cap 
   > daily limit is 10, total allowed is 100
  - Record whether scoring is immediate, queued, or delayed.
   > Immediate scoring
  - Record whether failed submissions count against the limit.
   > Irrelevant, ignore this

- [X] VB: confirm RunPod global networking status before downloading AgriPotential rasters.
   > Pod is located in EU-RO-1, global network is off
  - In RunPod Pod details/connectivity, confirm whether public internet egress is enabled.
  - If disabled, enable it or report the exact limitation.

  > Public internet downloads succeeded with global networking off, so no further action is needed now.

- [X] VB or RunPod operator: sync latest branch to RunPod at `/workspace/ai4agri`.
  - Branch: `main`
  - Run `git pull` or use the repo sync helper from a machine with RunPod SSH access.
- [X] VB or RunPod operator: download Subtask 1 CSVs and viticulture label raster first.
  - Run on RunPod:
    ```bash
    cd /workspace/ai4agri
    source .venv/bin/activate
    python scripts/download_subtask1_hf.py --out-dir data/subtask1 --skip-images
    ```
  - Confirm files exist: `metadata.csv`, `train.csv`, `val.csv`, `test.csv`, `viticulture.tif`.
- [X] VB or RunPod operator: smoke-read one Subtask 1 patch with labels.
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
- [X] VB or RunPod operator: download Sentinel-2 image rasters only if disk/time budget is acceptable.
  - Full image download is large.
  - Run on RunPod only:
    ```bash
    cd /workspace/ai4agri
    source .venv/bin/activate
    python scripts/download_subtask1_hf.py --out-dir data/subtask1
    ```
  - Record final disk usage with `du -sh data/subtask1`.
  > root@6528cb1710c5:/workspace/ai4agri# du -sh data/subtask1
185G	data/subtask1
- [X] VB or RunPod operator: finish the sampled-pixel Subtask 1 baseline after image rasters are present.
  - Start with a smoke run:
    ```bash
    python scripts/subtask1_baseline.py train \
      --data-dir data/subtask1 \
      --patch-limit 20 \
      --val-patch-limit 5 \
      --pixels-per-patch 256 \
      --max-train-pixels 5000
    ```
  - Smoke run completed and produced exact accuracy `0.5648`, Accuracy +/- 1 `0.9136`, MAE `0.5768`; this was a pipeline check, not a representative score.
  - Full run has already been triggered on RunPod. On completion, run inference and validation:
    ```bash
    python scripts/subtask1_baseline.py infer --data-dir data/subtask1
    python scripts/validate_submission_zip.py \
      --zip-path results/subtask1/submissions/subtask1_baseline.zip \
      --subtask1-codabench \
      --expected-ids-file data/subtask1/test.csv \
      --check-class-values
    ```
  - Record `metrics.json` exact accuracy, Accuracy +/- 1, MAE, and validation confusion matrix.
- [X] VB: submit `results/subtask1/submissions/subtask1_baseline.zip` only after validation passes, then record CodaBench score/errors.
  > Score is 39.74

## Now (Subtask 1 Leaderboard Loop)

- [ ] Confirm whether the submitted `39.74` ZIP came from the older script version or the optimized version.
- [ ] Sync/pull latest code on RunPod and confirm it has commit `5bb8c08` or newer.
- [ ] Run the overnight Subtask 1 suite:
  ```bash
  python scripts/run_subtask1_experiments.py \
    --data-dir data/subtask1 \
    --suite overnight \
    --infer-best \
    --validate-best
  ```
- [ ] Review `results/subtask1/experiments/<timestamp>/overnight/summary.csv`.
- [ ] If validation metrics are plausible, pull and submit the best validated candidate ZIP.
- [ ] Record every CodaBench score and avoid spending submissions on unvalidated ZIPs.

## Before May 28 (Notebook submission)

- [X] Confirm DACIA5 patch label source before training Subtask 2 baseline.
- [X] Baseline: Subtask 2 — run tabular script on RunPod after label source is confirmed.
- [ ] Subtask 1: improve leaderboard score with optimized tabular/pixel baselines first.
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
