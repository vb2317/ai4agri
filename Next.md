# Next

## Today: 2026-05-05 Winning Move

Subtask 1 is the priority because it has immediate leaderboard feedback. Current submitted scores:

- Constant class baseline: `39.52`
- First sampled-pixel baseline: `39.74`
- Overnight uniform raw-temporal HGB: `40.16`

Goal today: use the replacement RunPod to produce one stronger, validated Subtask 1 candidate and submit only if it is plausibly different/better.

Latest overnight result:

- Best validation run: `hgb_uniform_temporal_200k_s43`
- Accuracy +/- 1: `0.72604`
- Exact accuracy: `0.5524`
- MAE: `0.97296`
- Validated ZIP: `results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip`
- CodaBench score: `40.16`
- Signal: uniform sampling + raw-temporal features beat class-balanced variants in this suite.

Immediate next local pull command:

```bash
scripts/runpod_sync.sh pull \
  /workspace/ai4agri/results/subtask1/submissions/20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip \
  ./results/subtask1/submissions/
```

Submitted to CodaBench and scored `40.16`.

Next move:

- [X] Treat `40.16` as the new floor.
- [X] Add a targeted follow-up suite near the winning setup: HGB + uniform sampling + raw-temporal features.
- [ ] Run the targeted suite before switching to U-Net/ViT:
  ```bash
  python scripts/run_subtask1_experiments.py \
    --data-dir data/subtask1 \
    --suite targeted \
    --infer-best \
    --validate-best
  ```

### VB

- [ ] Wait for replacement RunPod to become ready.
- [ ] Configure local `.env`:
  ```bash
  scripts/configure_runpod_env.sh \
    --host NEW_PUBLIC_SSH_HOST_OR_IP \
    --port NEW_PUBLIC_SSH_PORT \
    --pod-id NEW_POD_ID \
    --jupyter-url NEW_JUPYTER_LAB_URL \
    --test
  ```
- [ ] Push current repo files:
  ```bash
  scripts/runpod_sync.sh push
  ```
- [ ] Choose migration mode:
  - Mode A: existing volume present, verify `data/subtask1`.
  - Mode B: data missing, redownload Subtask 1 and smoke-read images/labels.
- [ ] Start the targeted Subtask 1 experiment suite after data checks pass.
- [ ] Submit only the best validated candidate ZIP, and record CodaBench score immediately.

### Codex

- [ ] Keep docs/scripts aligned with the replacement pod workflow.
- [ ] After experiments finish, review `summary.csv`, `summary.json`, logs, and `best_inference.json`.
- [ ] If the best candidate is weak, implement one targeted improvement: ExtraTrees tuning, class-prior calibration, or simple spatial smoothing.
- [ ] Preserve the submission gate: validate ZIP, expected ids, and class values before upload.

### Claude

- [X] Focus on Subtask 1 only today.
- [X] Return a compact memo on low-risk AgriPotential improvements implementable in under 2 hours:
  - ordinal calibration/rounding
  - class-prior correction
  - spatial smoothing for suitability masks
  - preprocessing/nodata/band-order issues from official examples
  - Memo: `claude_handoffs/subtask1_leaderboard_memo_20260505.md`.

## RunPod Start Commands

Mode A data check:

```bash
cd /workspace/ai4agri
du -sh data/subtask1
test -f data/subtask1/test.csv
test -f data/subtask1/viticulture.tif
find data/subtask1 -maxdepth 1 -name "*.tif" | wc -l
```

Mode B redownload:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
python scripts/download_subtask1_hf.py --out-dir data/subtask1
python scripts/inspect_subtask1.py \
  --data-dir data/subtask1 \
  --splits train val test \
  --limit 1 \
  --read-pixels \
  --read-labels
du -sh data/subtask1
```

Start experiments:

```bash
cd /workspace/ai4agri
source .venv/bin/activate
mkdir -p results/subtask1/experiments
nohup python scripts/run_subtask1_experiments.py \
  --data-dir data/subtask1 \
  --suite overnight \
  --infer-best \
  --validate-best \
  > results/subtask1/experiments/overnight.log 2>&1 &
```

Check progress:

```bash
tail -f results/subtask1/experiments/overnight.log
```

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
- [ ] Run the targeted Subtask 1 suite:
  ```bash
  python scripts/run_subtask1_experiments.py \
    --data-dir data/subtask1 \
    --suite targeted \
    --infer-best \
    --validate-best
  ```
- [ ] Review `results/subtask1/experiments/<timestamp>/overnight/summary.csv`.
- [X] Inspect `results/subtask1/experiments/20260504T180650Z/overnight/best_inference.json`.
- [ ] Pull and submit `20260504T180650Z_overnight_hgb_uniform_temporal_200k_s43.zip`.
- [ ] Record every CodaBench score and avoid spending submissions on unvalidated ZIPs.

## Before May 28 (Notebook submission)

- [X] Confirm DACIA5 patch label source before training Subtask 2 baseline.
- [X] Baseline: Subtask 2 — run tabular script on RunPod after label source is confirmed.
- [X] Confirm Subtask 2 deliverable format: Colab notebook or zipped source folder with README, plus max 3-page report, submitted by email.
- [ ] Confirm DACIA5 Sentinel-2 12-band order before adding vegetation-index features.
- [ ] Subtask 1: improve model — U-Net or ViT on multi-temporal stack
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
