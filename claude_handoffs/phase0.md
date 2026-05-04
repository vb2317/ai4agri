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

```text
Project: AI4Agri 2026, Subtask 1 AgriPotential.

Task:
Review the official AgriPotential package/tutorial and summarize the fastest way to load a small training sample, validation sample, and test sample.

Needed output:
- Install command.
- Minimal smoke-test Python snippet.
- Data path or streaming options.
- Tensor shapes and label shapes if documented.
- Any gotchas for memory or disk.
```

## 3. DACIA5 Data Format

```text
Project: AI4Agri 2026, Subtask 2 DACIA5.

Task:
Review the Zenodo dataset documentation and any included metadata docs.

Needed output:
- Download command or file list.
- Label mapping.
- Year/month split logic for both challenges.
- Patch file layout and shapes.
- Recommended prediction/report submission format.
```
