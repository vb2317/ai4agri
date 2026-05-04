# Claude Findings: Phase 0

Last updated: 2026-05-04

## 2. AgriPotential Loader

Status: Done.

Sources:

- Official package: https://github.com/MohammadElSakka/agripotential
- Dataset files: https://huggingface.co/datasets/m-sakka/agripotential/tree/main
- Competition page: https://www.codabench.org/competitions/12055/

Findings:

- Install with `pip install git+https://github.com/MohammadElSakka/agripotential`.
- Real API is `from agripotential.dataset.potential_dataset import PotentialDataset`.
- Constructor is `PotentialDataset(label_name, mode, data_path=None)`.
- `label_name` is one of `viticulture`, `market`, or `field`; competition target is `viticulture`.
- `mode` is one of `train`, `val`, or `test`.
- If `data_path` is omitted, the package reads from `https://huggingface.co/datasets/m-sakka/agripotential/resolve/main/`.
- The package reads `metadata.csv`, `<mode>.csv`, and `<label_name>.tif`.
- `__getitem__` returns `(data, label, patch_id)`.
- `data` shape is `(34, 10, patch_size, patch_size)` as `float32`.
- `label` shape is `(patch_size, patch_size)` as `uint8`.
- CSV counts confirmed from Hugging Face: `metadata.csv` has 34 image rows, `train.csv` has 6329 patches, `val.csv` has 781 patches, and `test.csv` has 800 patches.
- CSV columns are `patch_id`, `row`, `col`, `patch_size`, and `n_annotated` for splits; `metadata.csv` contains `filename`, `day`, `month`, and `year`.
- The package download helper downloads `train.csv`, `val.csv`, `metadata.csv`, label GeoTIFFs, and optionally all images, but it does not include `test.csv` in its CSV list.
- `get_input_loader(subset="test")` appears to be CodaBench pseudocode, not a package API.

Gotchas:

- The package iterator always attempts to read labels, including in `mode="test"`. Codex inspection/inference code should read `test.csv` and image windows directly rather than assuming test labels exist.
- Full imagery is large; metadata inspection can read only CSVs first.
- Raster reads open each Sentinel-2 GeoTIFF per patch. Feature extraction should batch or cache where possible once baseline code is stable.
- Submission masks must be PNGs named `<patch_id>.png` with integer class ids `0..4`.

Codex implementation notes:

- `scripts/inspect_subtask1.py` should read CSV metadata first and only read imagery when `--read-pixels` is passed.
- It should accept `--data-dir`, `--out-dir`, `--splits`, `--limit`, `--read-pixels`, and `--read-labels`.
- It should write JSON under `results/subtask1/inspection/`.
- For inference, prefer direct rasterio window reads from `metadata.csv` + `test.csv` so labels are not required.

## 3. DACIA5 Data Format

Status: Done.

Sources:

- Zenodo record: https://zenodo.org/records/14283243
- Zenodo API: https://zenodo.org/api/records/14283243
- ImageCLEF task page: https://www.imageclef.org/2026/ai4agri

Findings:

- Download file is `AI4AGRI Sentinel-2 Brasov area 2020-2024 dataset.zip`.
- Size is 1,134,693,201 bytes.
- Checksum is `md5:72a7da84ca5069843c67b5a816be04d7`.
- Direct API content link is available under the Zenodo record file metadata.
- Images are Sentinel-2 MSI GeoTIFFs, 800 x 450 pixels x 12 bands, stored under `Images_Sentinel2_GeoTIFF/Sentinel2_yyyy`.
- Masks and legends are under `Masks_and_legend/Sentinel2_yyyy`, with RGB masks plus label masks in PNG and MAT formats.
- Patch data is under `32x32_patches`.
- Multispectral patches are under `32x32_patches/32x32_multispectral_patches/problem1` and `problem2`.
- Each problem is divided into `training` and `test`.
- Patches are stored in both GeoTIFF and MAT formats under `patches_tiff` and `patches_mat`.
- RGB patches exist separately under `32x32_RGB_patches` for visualization/ground-truth masks.
- Zenodo describes 32 x 32 x 12 Sentinel-2 multispectral patches.

Challenge interpretation:

- Problem 1 / Challenge 1: crop identification with temporal generalization, training with 2020-2023 data and testing with 2024 data.
- Problem 1 labels: Wheat `0`, Corn `1`, Peas `2`, Rapeseed `3`, Potato `4`, Sugarbeet `5`, Alfalfa `6`.
- Problem 2 / Challenge 2: ImageCLEF 2026 asks for March-only early detection of winter wheat vs alfalfa.
- Problem 2 labels: Winter Wheat `0`, Alfalfa `1`.
- The Zenodo text mentions a May 20 split for early identification, but ImageCLEF 2026 supersedes that for the current challenge with March imagery.
- The ImageCLEF page says Subtask 2 submissions are a Google Colab notebook plus a 3-page technical report.

Codex implementation notes:

- `scripts/inspect_subtask2.py` should summarize file counts by problem, split, format, and year.
- It should read a few TIFF shapes when `--read-arrays` is passed.
- The first baseline should use `32x32_multispectral_patches` TIFF or MAT arrays, extracting per-band means/std/min/max/percentiles and vegetation indices.
- If Sentinel-1 SAR is supplied separately in the competition package, add VV/VH features after inspection confirms its layout.

## 4. Fast Baseline Recommendations

Status: Done.

### Implement First

- Subtask 2 tabular baseline.
- Extract per-patch per-band mean, standard deviation, min, max, and percentiles from 32x32x12 Sentinel-2 patches.
- Add NDVI-like and moisture/red-edge features if band order is confirmed from metadata or docs.
- Train `ExtraTreesClassifier` and `HistGradientBoostingClassifier`; use class weights or balanced sampling for class imbalance.
- Validate Problem 1 with a year-aware split, e.g. hold out 2023 locally if 2024 labels are hidden.
- For Problem 2, filter to March winter wheat/alfalfa samples and validate by year.

### Implement Second

- Subtask 1 sampled-pixel ordinal baseline.
- Sample labeled pixels from train/val patches.
- Features: per-band temporal mean/std/min/max, selected month/frame values, NDVI-like temporal summaries, and missing/cloud robustness if masks are present.
- Model: `HistGradientBoostingRegressor` rounded/clipped to `0..4`, plus `ExtraTreesClassifier` as a comparison.
- Metric: exact accuracy, Accuracy +/- 1, and mean absolute class error.
- Inference: predict every pixel in each test patch and write `uint8` PNG masks named `<patch_id>.png`.

### Skip Unless Time Remains

- Deep Subtask 1 U-Net or temporal Transformer.
- Subtask 2 patch CNN/GRU unless tabular baselines plateau and the data loader is already stable.
- CORAL-style ordinal heads unless a PyTorch training loop is already working.

Failure modes:

- Subtask 1 remote raster reads may be I/O-bound; avoid rereading all 34 GeoTIFFs repeatedly during feature experiments.
- Subtask 2 class imbalance can make overall accuracy look acceptable while average accuracy is weak.
- Band order must be verified before committing vegetation-index features to final reports.
