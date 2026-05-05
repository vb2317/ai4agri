# Next

## Today: 2026-05-05 Winning Move

Subtask 1 is the priority because it has immediate leaderboard feedback. Current submitted scores:

- Constant class baseline: `39.52`
- First sampled-pixel baseline: `39.74`
- Overnight uniform raw-temporal HGB: `40.16`

Goal today: split ownership cleanly. Claude owns the new L40S 48 GB RunPod vision run end to end; Codex focuses on improving the existing RunPod setup and preserving common analysis artifacts for VB review.

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
- [X] Pivot Subtask 1 to a vision-model campaign; keep HGB only as fallback/ensemble floor.
- [X] Assign the L40S 48 GB pod entirely to Claude; see `claude_handoffs/phase1.md`.
- [ ] Codex: improve existing RunPod helpers, common notebooks, validators, and result sync.
- [ ] VB: review Claude-produced visual artifacts before any submission.

## RunPod Assignment

- Existing pod / `.env`: VB + Codex, for setup hardening, shared scripts, validators, and common analysis.
- L40S pod / `.env.l40s.claude`: Claude, for the complete ResNet/FPN and TinyViT vision run.
- Shared analysis remains in this repo:
  - `notebooks/subtask1_testbed.ipynb`
  - `notebooks/10_final_stack.ipynb`
  - `results/subtask1/vision_runs/`
  - `results/subtask1/val_preds/`
  - `results/subtask1/visuals/`
  - `results/subtask1/submissions/`

Configure Claude's L40S pod:

```bash
scripts/configure_runpod_env.sh \
  --env-file .env.l40s.claude \
  --host L40S_PUBLIC_SSH_HOST_OR_IP \
  --port L40S_PUBLIC_SSH_PORT \
  --pod-id L40S_POD_ID \
  --pod-name claude-l40s \
  --jupyter-url L40S_JUPYTER_URL \
  --test
```

Push shared code to Claude's pod:

```bash
scripts/runpod_install_rsync.sh --env-file .env.l40s.claude
scripts/runpod_sync.sh --env-file .env.l40s.claude push
scripts/runpod_exec.sh --env-file .env.l40s.claude 'bash scripts/runpod_status.sh'
```

Pull Claude's completed run artifacts:

```bash
scripts/runpod_sync.sh --env-file .env.l40s.claude pull-results
```

Existing pod smoke/status:

```bash
scripts/runpod_sync.sh push
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
```

Artifacts to review in `notebooks/subtask1_testbed.ipynb`:

- `results/subtask1/vision_runs/<run_id>/config.json`, `metrics.json`, `train.log`
- `results/subtask1/val_preds/<run_id>_val_probs.npz`
- `results/subtask1/visuals/<run_id>/`
- `results/subtask1/submissions/<run_id>.zip`

## Latest Existing-Pod Vision Candidate

- Run ID: `existing_unet_ce_summary_rand_e10_p1024_v256_m5`
- Model: U-Net, `summary` temporal mode, CE loss, randomized limited rows, median `5`
- Train/val subset: 1024 train patches, 256 validation patches
- Best epoch: `2`
- Validation Accuracy +/- 1: `0.7278788585595585`
- Exact accuracy: `0.43254234800646274`
- MAE: `1.1169152227438965`
- Remote ZIP validation: passed against `data/subtask1/test.csv`
- ZIP: `results/subtask1/submissions/existing_unet_ce_summary_rand_e10_p1024_v256_m5.zip`
- Visuals: `results/subtask1/visuals/existing_unet_ce_summary_rand_e10_p1024_v256_m5/`
- Test class distribution: class 0 `40.36%`, class 1 `26.24%`, class 2 `1.54%`, class 3 `0.18%`, class 4 `31.67%`
- Gate: not constant and beats HGB validation floor on randomized subset, but class 2/3 recall is weak; VB visual review required before any CodaBench submission.

## Latest Weighted Vision Smoke

- Run ID: `existing_unet_wce_summary_rand_e6_p512_v128_m5`
- Model: U-Net, `summary` temporal mode, weighted CE, randomized limited rows, median `5`
- Train/val subset: 512 train patches, 128 validation patches
- Best epoch: `1`
- Validation Accuracy +/- 1: `0.7425670355301913`
- Exact accuracy: `0.4574410747449113`
- MAE: `0.9890531818457138`
- Per-class recall: class 0 `0.7968`, class 1 `0.0000`, class 2 `0.0118`, class 3 `0.6654`, class 4 `0.0000`
- Visuals: `results/subtask1/visuals/existing_unet_wce_summary_rand_e6_p512_v128_m5/`
- Gate: useful for VB side-by-side review because it recovers class 3 and improves +/-1 on a smaller randomized slice, but it collapses classes 1 and 4 and should not be submitted as-is.

### VB

- [ ] Keep existing RunPod configured in `.env`.
- [ ] Configure Claude L40S pod in `.env.l40s.claude`:
  ```bash
  scripts/configure_runpod_env.sh \
    --env-file .env.l40s.claude \
    --host L40S_PUBLIC_SSH_HOST_OR_IP \
    --port L40S_PUBLIC_SSH_PORT \
    --pod-id L40S_POD_ID \
    --pod-name claude-l40s \
    --jupyter-url L40S_JUPYTER_URL \
    --test
  ```
- [ ] Hand Claude `claude_handoffs/phase1.md`.
- [ ] Review Claude's visual artifacts in `notebooks/subtask1_testbed.ipynb`.
- [ ] Submit only the best validated candidate ZIP, and record CodaBench score immediately.

### Codex

- [X] Add multi-env RunPod helper support for `.env` plus `.env.l40s.claude`.
- [X] Keep Claude L40S execution handoff current.
- [ ] Improve existing RunPod setup and shared artifact review workflow.
- [ ] Preserve the submission gate: visual review, validate ZIP, expected ids, and class values before upload.

### Claude

- [ ] Own the L40S 48 GB RunPod lane end to end.
- [ ] Run `claude_handoffs/phase1.md`.
- [ ] Return metrics, logs, visual artifact paths, ZIP validation status, and submit/reject recommendation.

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
- [ ] Run the overnight Subtask 1 suite:
  ```bash
  python scripts/run_subtask1_experiments.py \
    --data-dir data/subtask1 \
    --suite overnight \
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
