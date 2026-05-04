# AI4Agri — ImageCLEF 2026

Competition entry for [ImageCLEF 2026 AI4Agri](https://www.imageclef.org/2026/ai4agri).

## Tasks

### Subtask 1: AgriPotential (Viticulture)
Predict land suitability for grapevine cultivation from multi-temporal Sentinel-2 imagery.

- **Input:** 34 Sentinel-2 timeframes (2017–2019), 10 bands, 5m resolution
- **Output:** 5-class ordinal label per pixel (very low → very high suitability)
- **Metric:** Accuracy±1 (predictions within one class count as correct)
- **Data:** HuggingFace [`m-sakka/agripotential`](https://huggingface.co/datasets/m-sakka/agripotential) (~200GB)
- **Platform:** [CodaBench](https://www.codabench.org/competitions/12055/)

### Subtask 2: DACIA5 (Crop Identification)
Identify crop types from Sentinel-2 optical + Sentinel-1 SAR time series near Brașov, Romania.

**Challenge 1 — Past vs Present:** Train on 2020–2023, predict 7 crop types in 2024.
**Challenge 2 — Early Detection:** Classify winter wheat vs alfalfa using March imagery only.

- **Metric:** Q = 0.5×AA + 0.5×OA
- **Data:** [Zenodo 14283243](https://zenodo.org/records/14283243) (3.4GB)
- **Submit:** Colab notebook or zipped source + 3-page technical report

## Key Dates

| Milestone | Date |
|---|---|
| Submission deadline | May 7, 2026 |
| Notebook submission | May 28, 2026 |
| Conference | Sep 21–24, 2026 (Jena, Germany) |

## Structure

```
data/
  subtask1/       # AgriPotential patches (HuggingFace)
  subtask2/       # DACIA5 patches (Zenodo)
notebooks/
  subtask1/       # Exploration and experiments
  subtask2/
src/
  subtask1/       # Training and inference scripts
  subtask2/
results/
  subtask1/       # Submission ZIPs
  subtask2/       # Predictions + report
```

## Setup

```bash
pip install -r requirements.txt
```

For Subtask 1 data:
```bash
pip install git+https://github.com/MohammadElSakka/agripotential
```
