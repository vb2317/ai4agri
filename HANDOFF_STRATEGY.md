# AI4Agri Handoff Strategy

Last updated: 2026-05-05

## Purpose

Coordinate VB, Codex, and Claude so work moves in parallel without duplicating effort or creating conflicting artifacts.

Current operational state is tracked in `CHATGPT_PLAN.md`. Repository and pipeline architecture is tracked in `ARCHITECTURE.md`. Phase-specific prompts and findings live under `claude_handoffs/` and `vb_handoffs/`.

The core pattern:

1. VB decides and operates external systems.
2. Claude owns the dedicated L40S 48 GB RunPod execution lane for Subtask 1 vision experiments.
3. Codex turns confirmed findings into repo code, scripts, validators, notebooks, and reproducible commands, and keeps the existing pod setup healthy.

## Default Ownership

### VB

Owns:

- Account access: ImageCLEF, CodaBench, Hugging Face, Zenodo, cloud provider.
- Credentials and tokens.
- Remote budget and provider choice.
- Final submission uploads.
- Strategic tradeoffs when time, budget, or leaderboard feedback conflict.

Does not need to own:

- Script implementation.
- Local validation tooling.
- Experiment bookkeeping format.
- Drafting reproducible commands once provider/path choices are known.

### Codex

Owns:

- Repository structure and implementation.
- Local and remote runnable scripts.
- Submission validators and packaging.
- Metrics implementations.
- Updating `README.md`, `CHATGPT_PLAN.md`, and handoff docs.
- Converting Claude findings into executable code.
- Keeping generated artifacts reproducible.

Codex should avoid:

- Guessing logged-in CodaBench rules.
- Hardcoding remote paths before VB chooses them.
- Starting large downloads without VB confirming provider, budget, and path.

### Claude

Owns:

- Bounded research questions.
- The L40S Subtask 1 vision run when explicitly assigned in `claude_handoffs/phase1.md`.
- Logged-in page summarization if VB gives Claude access or screenshots.
- Literature/package/tutorial review.
- Draft model ideas that Codex can implement.
- Report prose and ablation narrative after metrics exist.

Claude should avoid:

- Making final submission decisions.
- Changing shared repo structure during the L40S run; use existing scripts and return artifacts/metrics.
- Running HGB-only experiments on the L40S lane unless needed for a final ensemble comparison.

## Handoff States

Use these states in notes, issues, or chat:

- `Blocked`: needs external access, data, or a VB decision.
- `Ready for Claude`: research question is bounded and can run in parallel.
- `Ready for Codex`: input is confirmed enough to implement.
- `Ready for VB`: artifact or decision needs human action.
- `Done`: outcome is recorded in the repo or submission system.

## Decision Rules

### When VB Should Decide

Ask VB when:

- Money is involved.
- Credentials are involved.
- The task requires logged-in submission/account action.
- Two viable paths have different deadline risk.
- We need to freeze a submission candidate.

### When Claude Should Get A Handoff

Use Claude when:

- The answer is research-heavy and can be summarized.
- The task can run while Codex is implementing something else.
- The output should be recommendations, not repo changes.
- Login-only pages or docs need human-mediated review.

Good Claude tasks:

- Exact CodaBench format.
- AgriPotential loader usage.
- DACIA5 file layout and labels.
- Fast baseline ideas from official tutorials or papers.
- Report draft from final metrics.

### When Codex Should Proceed Directly

Codex should proceed when:

- The task is local repo work.
- A reasonable default is low-risk.
- The artifact improves reproducibility.
- The next step does not require external credentials or large remote spend.

Good Codex tasks:

- Validators.
- Loaders.
- Metrics.
- Smoke tests.
- Training/inference scripts.
- Packaging scripts.
- Documentation updates.

## Critical Path

The original route to useful results was:

1. VB confirms exact CodaBench submission format.
2. VB chooses remote provider and budget.
3. Claude confirms AgriPotential and DACIA5 data access details.
4. Codex writes data inspection scripts.
5. VB starts downloads or remote environment.
6. Codex runs smoke tests and builds baselines.
7. VB submits first valid CodaBench ZIP.
8. Claude helps interpret score/error feedback.
9. Codex improves and repackages.

Current critical path for 2026-05-05:

1. VB keeps the existing RunPod connection in `.env` and configures the L40S pod in `.env.l40s.claude`.
2. Claude runs the entire L40S Subtask 1 vision lane from `claude_handoffs/phase1.md`.
3. Codex improves the existing RunPod setup, common scripts, validators, notebooks, and artifact review flow.
4. VB reviews visual artifacts in `notebooks/subtask1_testbed.ipynb`.
5. VB submits one validated, plausibly improved ZIP and records leaderboard score.

## Parallel Work Plan

### Track A: Existing Pod And Submission

Owner: VB with Codex support.

- VB: keep RunPod funded only for active work.
- VB: keep `.env` pointed at the existing pod.
- VB: submit only validated ZIPs and record scores.
- Codex: keep remote scripts pod-agnostic and validation strict.

### Track B: L40S Vision Experiments

Owner: Claude.

- Claude: use `.env.l40s.claude` and run `claude_handoffs/phase1.md` end to end.
- Claude: return metrics, visual artifact paths, logs, validation status, and recommendation.
- VB: submit the selected candidate only after validation.

### Track C: Common Analysis And Review

Owner: Codex.

- Codex: maintain `scripts/run_subtask1_vision.py`, validators, and notebook review cells.
- Codex: keep artifact paths stable for VB review.
- Codex: integrate Claude-returned results into docs and final stack review.

### Track D: Parked Reporting

Owner: Codex structures, Claude drafts, VB approves.

- Subtask 2 reporting remains parked until the next Subtask 1 leaderboard pass is complete.

## Historical Phase 0 Handoffs

These entries are retained as historical context. Use `CHATGPT_PLAN.md` for current assignments.

### Handoff 1: VB To Claude

Status: Done.

Use `claude_handoffs/phase0.md`, prompt 1.

Expected output:

- Exact CodaBench ZIP structure: root-level files only.
- Required filenames: one PNG per `test.csv` `patch_id`, named `<patch_id>.png`; optional `report.pdf`.
- Prediction shape: each PNG is a pixel-level segmentation mask for the corresponding test patch.
- Class ids: integer values `0` to `4`.
- Submission limits/evaluation timing: still not captured in `vb_handoffs/phase0.md`.

Codex follow-up:

- Update `scripts/validate_submission_zip.py` usage examples. Done.
- Add packaging script if the format is stable.

### Handoff 2: VB To Claude

Status: Done.

Use `claude_handoffs/phase0.md`, prompt 2.

Expected output:

- AgriPotential install command.
- Minimal loader snippet.
- Shape and split details.
- Whether streaming avoids full 200GB download.

Codex follow-up:

- Implement `scripts/inspect_subtask1.py`.

### Handoff 3: VB To Claude

Status: Done.

Use `claude_handoffs/phase0.md`, prompt 3.

Expected output:

- DACIA5 file list and label mapping.
- Split rules for both challenges.
- Patch layout.
- Any official notebook/report expectations.

Codex follow-up:

- Implement `scripts/inspect_subtask2.py`.
- Start Subtask 2 baseline pipeline.

### Handoff 5: VB To Claude

Status: Done.

Use `claude_handoffs/phase0.md`, prompt 4.

Expected output:

- Low-risk baseline recommendation memo for both subtasks.
- Ranked feature/model list.
- Class imbalance handling notes.
- Explicit assumptions and failure modes.

Codex follow-up:

- Convert recommendations into first baseline scripts after data inspection confirms shapes.

### Handoff 4: VB To Codex

Status: Done. RunPod Pod launched, connection details recorded, global networking status recorded as off, and public downloads succeeded.

Needed from VB:

- Keep the Pod running only during active training/inference, then stop it when idle.

Codex follow-up:

- Maintain RunPod commands and sync helpers in `REMOTE_PROVIDER.md` and `scripts/`.
- Add provider-specific notes to `README.md`.
- Prepare first remote smoke-test command.

## Handoff Template

```text
Owner:
Task:
Context:
Inputs:
Expected output:
Deadline:
Blocked by:
After completion:
```

## Completion Criteria

A handoff is complete only when:

- The result is written into a repo file, or
- The decision is recorded in `CHATGPT_PLAN.md`, or
- The submission/upload action is recorded with timestamp and outcome.

Do not rely on chat history alone for decisions that affect reproducibility.
