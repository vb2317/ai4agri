# Architecture

Last updated: 2026-05-05

## Purpose

This repo is built around fast, reproducible competition execution. Local work should produce reviewed scripts, docs, and packaging checks. RunPod should handle full datasets, feature extraction, model training, and inference. VB handles external systems and final submissions. Claude answers bounded research questions that can unblock implementation.

## Execution Topology

| Layer | Runs Where | Owns |
|---|---|---|
| Local Mac | `/Users/vb/dev/projects/ai4agri` | Code edits, docs, commits, result review, ZIP validation after pull |
| RunPod | `/workspace/ai4agri` | Large data, raster reads, feature caches, training, inference |
| CodaBench | Web UI | Subtask 1 uploads and leaderboard feedback |
| ImageCLEF/DACIA5 materials | Web/PDF/notebook materials | Subtask 2 deliverable rules, report expectations, band-order confirmation |

## Repository Layout

```text
scripts/           Operational commands and reproducible workflows
notebooks/         Exploration/test beds paired with percent-format Python files
data/              Raw datasets; ignored by git
results/           Inspections tracked; bulky generated artifacts ignored by git
claude_handoffs/   Research prompts and Claude findings
vb_handoffs/       Logged-in account/provider/submission notes from VB
```

The active task tracker is `CHATGPT_PLAN.md`. `Next.md` is a short working checklist. `REMOTE_PROVIDER.md` contains only current RunPod state and pending remote actions.

## Data And Artifact Policy

- Raw data stays in `data/` and is not committed.
- Full Subtask 1 rasters stay on RunPod unless a small sample is explicitly needed locally.
- Generated model files, feature caches, and submission ZIPs stay under `results/` but are ignored where they are large or disposable.
- Small inspection summaries and planning docs are tracked so agents can coordinate without re-reading full datasets.
- Submission ZIPs must always be validated before VB uploads them.

## Subtask 1 Pipeline

1. Download data on RunPod with `scripts/download_subtask1_hf.py`.
2. Inspect split metadata and raster windows with `scripts/inspect_subtask1.py`.
3. Maintain a packaging floor with `scripts/create_subtask1_constant_zip.py`.
4. Train the sampled-pixel baseline with `scripts/subtask1_baseline.py train`.
5. Infer test masks with `scripts/subtask1_baseline.py infer`.
6. Validate the CodaBench ZIP with `scripts/validate_submission_zip.py --subtask1-codabench`.
7. Pull metrics and ZIP locally, then VB submits to CodaBench.

Current model baseline: histogram gradient boosting over sampled pixels. The current implementation keeps rasters open across patches, shuffles split rows, defaults to class-balanced pixel sampling, and can use raw temporal-stack features plus simple temporal summaries.

## Subtask 2 Pipeline

1. Download and extract the Zenodo archive on RunPod.
2. Inspect layout with `scripts/inspect_subtask2.py`.
3. Confirm label semantics with `scripts/inspect_subtask2_labels.py`.
4. Build a patch manifest with `scripts/subtask2_baseline.py manifest`.
5. Cache tabular features with `scripts/subtask2_baseline.py features`.
6. Join labels with `scripts/subtask2_baseline.py label-features`.
7. Train leakage-free baselines with `scripts/subtask2_baseline.py train`.
8. Package the notebook/source README and report draft with `scripts/package_subtask2_submission.py`.

Current label interpretation: the DACIA5 patch filename middle token is the APIA crop code; the final token is the patch index. Final deliverable format is confirmed as notebook or zipped source folder with README, plus a max 3-page report. Vegetation-index features are blocked until Sentinel-2 band order is confirmed.

## Notebook Policy

Notebooks are not workflow runners. They showcase major steps from the code: data layout, inspection JSONs, sample imagery, feature distributions, metrics, confusion matrices, and candidate outputs.

Use the notebook aliases:

```bash
nbpair notebooks/subtask1_testbed.ipynb notebooks/subtask2_testbed.ipynb
nbsync notebooks/subtask1_testbed.ipynb notebooks/subtask2_testbed.ipynb
nbopen notebooks/subtask1_testbed.ipynb
nbrun notebooks/subtask1_testbed.ipynb
```

When a script changes the shape of a tracked artifact, update the corresponding notebook review cell in the same commit.

## Agent Ownership

VB owns accounts, billing, remote lifetime, final upload decisions, and leaderboard feedback.

Codex owns repository implementation, validators, scripts, notebooks, reproducible commands, and documentation alignment.

Claude owns bounded research: official format checks, band order, final Subtask 2 artifact expectations, report prose, and model recommendations that Codex can implement quickly.

## Current Decision Points

- Subtask 1 sampled-pixel baseline scored `39.74`, only slightly above the constant baseline score `39.52`.
- Decide whether to spend one quick RunPod pass on the optimized baseline settings or shift to Subtask 2 packaging/report work.
- Subtask 2 needs confirmed Sentinel-2 band order before vegetation-index features.
- Subtask 2 has a source/report package scaffold; VB/Codex should review it before May 28 submission.
