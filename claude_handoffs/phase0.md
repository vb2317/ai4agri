# Claude Handoffs: Phase 0

Use these prompts to split parallel research from Codex implementation.

## 1. CodaBench Submission Format

Status: Done from `vb_handoffs/phase0.md`.

Findings:
- Required submission is one ZIP archive for the test subset described by `test.csv`.
- All files must be directly at the root of the ZIP; no subfolders.
- Include segmented images as PNG files.
- Each PNG must be named exactly after its corresponding `patch_id`, e.g. `<patch_id>.png`.
- Goal is all 800 test images; fewer are permissible but reduce score.
- Extraneous files beyond expected PNGs are ignored by the scorer.
- Predicted output values must be integers from `0` very low to `4` very high.
- Optional method PDF may be included only as `report.pdf`; any other PDF name is ignored.
- Test labels are hidden and retained by organizers.
- Evaluation metric is Accuracy +/- 1.

Still unknown:
- Submission limits and evaluation timing were not present in the handoff text.

```text
Project: AI4Agri 2026, Subtask 1 AgriPotential.

Task:
Inspect the official CodaBench competition instructions for competition 12055 after login if needed.

Needed output:
- Exact required ZIP structure.
- Required file names.
- Prediction array/file shape.
- Allowed class ids.
- Submission limits and evaluation timing.
- Link or screenshot reference if available.

Constraints:
- Return concise findings.
- Do not guess if the page does not show details.
```

## 2. AgriPotential Loader

Status: Done. Findings recorded in `claude_handoffs/findings_phase0.md`.

```text
Project: AI4Agri 2026, Subtask 1 AgriPotential.

Task:
Review the official AgriPotential package/tutorial and summarize the fastest way for Codex to implement local/remote inspection scripts.

Needed output:
- Install command.
- Minimal smoke-test Python snippet for `subset="train"`, `subset="val"` or equivalent validation split, and `subset="test"`.
- Exact import names/functions, especially whether `get_input_loader(subset="test")` is real API or pseudocode.
- How `patch_id` is yielded for test samples.
- Tensor shape, dtype, band/time ordering, and label shape if documented.
- Data path configuration and whether streaming/partial download avoids the full ~200GB upfront.
- Any documented train/validation/test file names such as `test.csv`.
- Gotchas for memory, disk, PNG mask writing, or class ids.

Format:
- Keep answer concise.
- Include source links or file names.
- End with a `Codex implementation notes` section listing what `scripts/inspect_subtask1.py` should do.
```

## 3. DACIA5 Data Format

Status: Done. Findings recorded in `claude_handoffs/findings_phase0.md`.

```text
Project: AI4Agri 2026, Subtask 2 DACIA5.

Task:
Review the Zenodo dataset documentation and any included metadata docs so Codex can implement a loader and a fast tabular baseline.

Needed output:
- Download command or file list.
- Label mapping.
- Year/month split logic for both challenges.
- Patch file layout and shapes for Sentinel-2 optical and Sentinel-1 SAR.
- File formats and how labels/metadata connect to patch arrays.
- Which fields identify year, date/month, crop class, parcel/patch id, and challenge.
- Recommended prediction/report submission format.
- Any official baseline or notebook if present.

Format:
- Keep answer concise.
- Include source links or file names.
- End with a `Codex implementation notes` section listing what `scripts/inspect_subtask2.py` and the first baseline should do.
```

## 4. Fast Baseline Recommendations

Status: Done. Findings recorded in `claude_handoffs/findings_phase0.md`.

```text
Project: AI4Agri 2026, both subtasks.

Task:
Produce a low-risk baseline recommendation memo that Codex can implement immediately once data inspection works.

Needed output:
- Subtask 1: lowest-risk ordinal baseline for Accuracy +/- 1 using sampled pixels or patch summaries.
- Subtask 1: feature list from Sentinel-2 time series that can be extracted quickly.
- Subtask 1: how to write PNG masks robustly from model outputs.
- Subtask 2 Challenge 1: feature list and model choice for crop identification, optimized for Q = 0.5*AA + 0.5*OA.
- Subtask 2 Challenge 2: March-only feature list and binary model choice.
- Class imbalance handling for both subtasks.
- Ranked list: implement first, implement second, skip unless time remains.

Constraints:
- Favor methods implementable in under one day.
- Prefer scikit-learn / PyTorch basics already in `requirements.txt`.
- Avoid speculative deep architectures unless the data format is confirmed.
- Include failure modes or assumptions.
```
