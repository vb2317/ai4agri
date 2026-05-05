# Scripts

Operational scripts for local and remote AI4Agri runs.

Conventions:

- Every script should accept explicit paths such as `--data-dir`, `--out-dir`, or `--zip-path`.
- Long-running remote commands should write artifacts under `results/`.
- Important experiments should be logged in `results/runs.csv`.
- Smoke-test options should use `--limit` where applicable.
- Notebooks under `notebooks/` should review and visualize script-produced artifacts; do not move operational script commands into notebooks.
- `runpod_sync.sh push` sends code/docs only; generated Subtask 1 model artifacts are pulled back with `pull-results`.

Current scripts:

- `runpod_sync.sh`: local Mac helper for pushing repo changes to RunPod and pulling results or inspection outputs back.
- `runpod_exec.sh`: local Mac helper for running one command on the current RunPod over SSH.
- `configure_runpod_env.sh`: update local `.env` when a new RunPod host, port, pod id, or Jupyter URL is assigned.
- `runpod_install_rsync.sh`: install `rsync` on a fresh RunPod before first sync/pull.
- `runpod_bootstrap.sh`: run on RunPod to install `rsync`, create `.venv`, install dependencies, install `agripotential`, and verify CUDA.
- `runpod_status.sh`: run on RunPod to print host, GPU, disk, project size, key paths, and Python/CUDA status.
- `download_subtask1_agripotential.py`: download AgriPotential CSVs, including `test.csv`; optional label and image GeoTIFF downloads.
- `create_subtask1_constant_zip.py`: create a valid AgriPotential CodaBench ZIP with constant grayscale PNG masks for packaging smoke tests and first baseline submission.
- `download_subtask1_hf.py`: download AgriPotential CSVs, label rasters, and optional Sentinel-2 image rasters from Hugging Face.
- `download_subtask2_zenodo.py`: download the Subtask 2 Zenodo ZIP with checksum verification using only the Python standard library.
- `extract_subtask2_zip.sh`: extract the downloaded Subtask 2 ZIP under `data/subtask2`, installing `unzip` on apt-based images if needed.
- `inspect_subtask1.py`: inspect AgriPotential CSV metadata and optionally smoke-read Sentinel-2/label windows with `--limit`, `--read-pixels`, and `--read-labels`.
- `inspect_subtask2.py`: inspect extracted DACIA5 file layout, labels, years, and optional TIFF array shapes.
- `inspect_subtask2_labels.py`: inspect DACIA5 full-year label masks, per-patch RGB masks, and patch-to-mask matching.
- `run_subtask1_experiments.py`: run smoke, quick, overnight, or targeted Subtask 1 experiment suites; rank metrics; optionally infer and validate the best ZIP.
- `review_subtask1_candidate.py`: audit a Subtask 1 vision run before submission; checks required run artifacts, visuals, ZIP validation, and non-collapsed class presence.
- `subtask2_baseline.py`: build a DACIA5 patch TIFF manifest, cache tabular per-band features, and train ExtraTrees/HistGradientBoosting baselines once labels are confirmed.
- `summarize_subtask2_features.py`: summarize the generated Subtask 2 manifest/features into a small tracked inspection JSON.
- `package_subtask2_submission.py`: create a reviewable DACIA5 source/report ZIP without raw data, model binaries, or feature caches.
- `subtask1_baseline.py`: train/infer the sampled-pixel AgriPotential baseline. It keeps rasters open across patches, shuffles split rows, defaults to class-balanced pixel sampling, and uses raw plus temporal-summary pixel features.
- `train_subtask2_baseline.py`: direct experimental DACIA5 trainer that assumes the last filename token is the crop label; use only after label semantics are confirmed.
- `validate_submission_zip.py`: configurable ZIP sanity checker for candidate submissions. Use `--subtask1-codabench` for confirmed AgriPotential rules: root-level `<patch_id>.png` masks, optional `report.pdf`, and class ids `0..4`.

Common local commands:

```bash
scripts/configure_runpod_env.sh --host NEW_HOST --port NEW_PORT --pod-id NEW_POD_ID
scripts/runpod_install_rsync.sh
scripts/runpod_sync.sh push
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
scripts/runpod_sync.sh pull-results
```

Multiple RunPods:

Use `.env` for the active VB/Codex pod and a separate ignored env file for Claude's L40S lane.

```bash
scripts/configure_runpod_env.sh \
  --env-file .env.l40s.claude \
  --host L40S_HOST \
  --port L40S_PORT \
  --pod-id L40S_POD_ID \
  --pod-name claude-l40s \
  --test
scripts/runpod_sync.sh --env-file .env.l40s.claude push
scripts/runpod_exec.sh --env-file .env.l40s.claude 'bash scripts/runpod_status.sh'
scripts/runpod_sync.sh --env-file .env.l40s.claude pull-results
```

Common RunPod commands:

```bash
cd /workspace/ai4agri
bash scripts/runpod_bootstrap.sh
source .venv/bin/activate
python scripts/download_subtask1_hf.py --skip-images
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
python scripts/download_subtask1_hf.py --out-dir data/subtask1
python scripts/inspect_subtask1.py --splits train val test
python scripts/create_subtask1_constant_zip.py
python scripts/run_subtask1_experiments.py --data-dir data/subtask1 --suite overnight --infer-best --validate-best
python scripts/run_subtask1_experiments.py --data-dir data/subtask1 --suite targeted --infer-best --validate-best
python scripts/review_subtask1_candidate.py --run-id l40s_resnet_fpn_summary_e30
python scripts/subtask1_baseline.py train --data-dir data/subtask1
python scripts/subtask1_baseline.py infer --data-dir data/subtask1
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/inspect_subtask2_labels.py --data-dir data/subtask2
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2 --label-mode apia-code
python scripts/subtask2_baseline.py features
python scripts/subtask2_baseline.py label-features
python scripts/summarize_subtask2_features.py
python scripts/subtask2_baseline.py train --problem problem1
python scripts/package_subtask2_submission.py
# Experimental direct trainer after filename labels are confirmed; do not use for primary metrics:
python scripts/train_subtask2_baseline.py --data-dir data/subtask2 --problem 1
python scripts/train_subtask2_baseline.py --data-dir data/subtask2 --problem 2
```
