# AI4Agri Handoff Strategy

Last updated: 2026-05-04

## Purpose

Coordinate VB, Codex, and Claude so work moves in parallel without duplicating effort or creating conflicting artifacts.

The core pattern:

1. VB decides and operates external systems.
2. Claude researches bounded questions and returns findings.
3. Codex turns confirmed findings into repo code, scripts, validators, notebooks, and reproducible commands.

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
- Logged-in page summarization if VB gives Claude access or screenshots.
- Literature/package/tutorial review.
- Draft model ideas that Codex can implement.
- Report prose and ablation narrative after metrics exist.

Claude should avoid:

- Making final submission decisions.
- Producing broad brainstorming when a specific answer is needed.
- Changing repo structure unless explicitly assigned.

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

The fastest route to useful results is:

1. VB confirms exact CodaBench submission format.
2. VB chooses remote provider and budget.
3. Claude confirms AgriPotential and DACIA5 data access details.
4. Codex writes data inspection scripts.
5. VB starts downloads or remote environment.
6. Codex runs smoke tests and builds baselines.
7. VB submits first valid CodaBench ZIP.
8. Claude helps interpret score/error feedback.
9. Codex improves and repackages.

## Parallel Work Plan

### Track A: Access And Format

Owner: VB with Claude support.

- VB: log into CodaBench and confirm competition access.
- Claude: summarize exact CodaBench submission rules from page text or screenshots.
- VB: choose remote provider and budget.
- Codex: update validator options and packaging script after rules are known.

### Track B: Data Loading

Owner: Claude researches, Codex implements, VB runs external downloads.

- Claude: summarize AgriPotential loader and DACIA5 file layout.
- Codex: implement inspection scripts with `--limit`.
- VB: provide remote path and start downloads.
- Codex: run smoke tests remotely once data exists.

### Track C: Baselines

Owner: Codex implements, Claude advises.

- Codex: implement Subtask 2 tabular baseline first.
- Codex: implement Subtask 1 sampled ordinal baseline second.
- Claude: propose low-risk feature/model additions while Codex builds the baseline.
- VB: pick submission candidates based on validation and leaderboard feedback.

### Track D: Reporting

Owner: Codex structures, Claude drafts, VB approves.

- Codex: generate metrics tables and reproducibility commands.
- Claude: draft report prose and figure captions.
- VB: review final notebook/report.

## Immediate Handoffs

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

Status: Ready for Claude.

Use `claude_handoffs/phase0.md`, prompt 2.

Expected output:

- AgriPotential install command.
- Minimal loader snippet.
- Shape and split details.
- Whether streaming avoids full 200GB download.

Codex follow-up:

- Implement `scripts/inspect_subtask1.py`.

### Handoff 3: VB To Claude

Status: Ready for Claude.

Use `claude_handoffs/phase0.md`, prompt 3.

Expected output:

- DACIA5 file list and label mapping.
- Split rules for both challenges.
- Patch layout.
- Any official notebook/report expectations.

Codex follow-up:

- Implement `scripts/inspect_subtask2.py`.
- Start Subtask 2 baseline pipeline.

### Handoff 4: VB To Codex

Status: Blocked until VB chooses remote provider.

Needed from VB:

- Provider name.
- Remote OS/image if known.
- Disk size.
- GPU type, if any.
- Project directory path.
- Data directory path.
- Budget ceiling.

Codex follow-up:

- Write remote setup commands.
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
