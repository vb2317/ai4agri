# Scripts

Operational scripts for local and remote AI4Agri runs.

Conventions:

- Every script should accept explicit paths such as `--data-dir`, `--out-dir`, or `--zip-path`.
- Long-running remote commands should write artifacts under `results/`.
- Important experiments should be logged in `results/runs.csv`.
- Smoke-test options should use `--limit` where applicable.

Current scripts:

- `runpod_sync.sh`: local Mac helper for pushing repo changes to RunPod and pulling results or inspection outputs back.
- `runpod_exec.sh`: local Mac helper for running one command on the current RunPod over SSH.
- `runpod_bootstrap.sh`: run on RunPod to install `rsync`, create `.venv`, install dependencies, install `agripotential`, and verify CUDA.
- `runpod_status.sh`: run on RunPod to print host, GPU, disk, project size, key paths, and Python/CUDA status.
- `create_subtask1_constant_zip.py`: create a valid AgriPotential CodaBench ZIP with constant grayscale PNG masks for packaging smoke tests and first baseline submission.
- `download_subtask1_hf.py`: download AgriPotential CSVs, label rasters, and optional Sentinel-2 image rasters from Hugging Face.
- `download_subtask2_zenodo.py`: download the Subtask 2 Zenodo ZIP with checksum verification using only the Python standard library.
- `extract_subtask2_zip.sh`: extract the downloaded Subtask 2 ZIP under `data/subtask2`, installing `unzip` on apt-based images if needed.
- `inspect_subtask1.py`: inspect AgriPotential CSV metadata and optionally smoke-read Sentinel-2/label windows with `--limit`, `--read-pixels`, and `--read-labels`.
- `inspect_subtask2.py`: inspect extracted DACIA5 file layout, labels, years, and optional TIFF array shapes.
- `subtask1_baseline.py`: train a sampled-pixel AgriPotential baseline from local rasters and write test PNG masks in a CodaBench ZIP.
- `subtask2_baseline.py`: build a DACIA5 patch TIFF manifest, cache tabular per-band features, and train ExtraTrees/HistGradientBoosting baselines once labels are confirmed.
- `validate_submission_zip.py`: configurable ZIP sanity checker for candidate submissions. Use `--subtask1-codabench` for confirmed AgriPotential rules: root-level `<patch_id>.png` masks, optional `report.pdf`, and class ids `0..4`.

Common local commands:

```bash
scripts/runpod_sync.sh push
scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
scripts/runpod_sync.sh pull-results
```

Common RunPod commands:

```bash
cd /workspace/ai4agri
bash scripts/runpod_bootstrap.sh
source .venv/bin/activate
python scripts/download_subtask1_hf.py --skip-images
python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh
python scripts/inspect_subtask1.py --splits train val test
python scripts/create_subtask1_constant_zip.py
python scripts/subtask1_baseline.py train --data-dir data/subtask1
python scripts/subtask1_baseline.py infer --data-dir data/subtask1
python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2
python scripts/subtask2_baseline.py features
# After the DACIA5 crop-label source is confirmed and labels are present:
python scripts/subtask2_baseline.py train --problem problem1
```
