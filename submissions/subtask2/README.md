# AI4Agri Subtask 2 Submission Notes

This folder describes the intended DACIA5 source/report submission package. The official deliverable is a Google Colab notebook or zipped source folder with clear execution instructions, plus a technical report or extended abstract of at most 3 pages.

## Included Approach

- Task: ImageCLEF 2026 AI4Agri Subtask 2, DACIA5 crop identification.
- Data: Zenodo DACIA5 archive, extracted under `data/subtask2`.
- Model family: leakage-free tabular baselines over 32x32 multispectral Sentinel-2 patch TIFFs.
- Labels: derived from the APIA crop-code token in filenames using `vb_handoffs/Legend_crops.pdf`; the patch-index token is not used as a label.
- Features: per-band mean, standard deviation, min, max, and selected percentiles.
- Exclusions: APIA code, parcel id, and patch index are excluded from model features.
- Blocked feature family: NDVI, NDWI, red-edge, and SWIR indices wait for confirmed Sentinel-2 12-band order.

## Reproduce From A Fresh RunPod Checkout

```bash
cd /workspace/ai4agri
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

python scripts/download_subtask2_zenodo.py
bash scripts/extract_subtask2_zip.sh

python scripts/inspect_subtask2.py --data-dir data/subtask2 --read-arrays
python scripts/inspect_subtask2_labels.py --data-dir data/subtask2
python scripts/subtask2_baseline.py manifest --data-dir data/subtask2 --label-mode apia-code
python scripts/subtask2_baseline.py features
python scripts/subtask2_baseline.py label-features
python scripts/summarize_subtask2_features.py
python scripts/subtask2_baseline.py train --problem problem1
python scripts/subtask2_baseline.py train --problem problem2
```

## Current Tracked Evidence

- `results/subtask2/inspection/subtask2_inspection.json`
- `results/subtask2/inspection/subtask2_label_inspection.json`
- `results/subtask2/inspection/subtask2_feature_summary.json`
- `results/subtask2/inspection/subtask2_baseline_summary.json`
- `notebooks/subtask2_testbed.ipynb`
- `reports/subtask2_technical_report.md`

## Package The Source Bundle

From the repository root:

```bash
python scripts/package_subtask2_submission.py
```

Default output:

```text
results/subtask2/submissions/subtask2_source_bundle.zip
```

Review the ZIP contents before email submission. Do not include raw `data/`, feature caches, model binaries, or generated submission ZIPs unless the organizers explicitly request them.
