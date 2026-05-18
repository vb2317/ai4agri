# Share Manifest

## Share In Same Repo

Preferred for the first design pass.

Give the designer:

- repo access;
- this folder: `handoff/designer/`;
- run command: `python3 backend/server.py`;
- URL: `http://localhost:5173`;
- RFP source: `rfp/section12.md`.

This keeps the UI, data, RFP mappings, and implementation together.

## Create A Clean Repo Later

Create a clean repo only if:

- the designer is external and should not see strategy notes or model/backend experiments;
- the UI needs to be handed off as a pure frontend artifact;
- the project needs deployment separate from AI4Agri research assets.

Suggested clean-repo contents:

```text
upahar-demo-handoff/
  README.md
  app/
  backend/
  rfp/
  handoff/designer/
```

Exclude:

```text
backend/models/
backend/tiles/
docs/vb_notes.md
docs/vb_strategy_memo.md
docs/outreach_targets.md
docs/partner_*.md
docs/cost_breakdown.md
../notebooks/
../src/
```

If imagery tiles are needed for visual review, include a small tile subset or screenshots instead of the full tile/model payload.

