# Designer Handoff: UPAHAR Section 12 Demo

## Recommendation

Use this same repo for the first design pass.

This repo already contains the working UI, backend, tile assets, and RFP source text needed to understand the product. A new clean repo is only worth creating if the designer should not see strategy notes, backend implementation details, or broader AI4Agri work.

For a clean share, send the designer this folder plus access to the repo root. Their main entry points are:

- `app/index.html` - UI shell.
- `app/styles.css` - current visual system.
- `app/app.js` - interactions and rendering.
- `app/data.js` - demo content, parcels, metrics, and RFP mappings.
- `backend/server.py` - local demo server.
- `rfp/section12.md` - source RFP text.
- `handoff/designer/design_brief.md` - product and design brief.
- `handoff/designer/rfp_brief.md` - RFP requirements that matter for the UI.

## Start The Current UI

### Easiest On Mac

Double-click:

```text
Start UPAHAR Demo.command
```

This starts the local demo server and opens the browser automatically. Keep the terminal window open while reviewing the app. Close it or press `Control-C` to stop the server.

If Python 3 is not available, the script opens the static preview automatically.

### Zero-Dependency Static Preview

Double-click:

```text
Open Static Preview.command
```

This opens `app/index.html` directly in the browser. It is enough for visual review of the main UI, RFP badges, parcel panels, and layout. Backend-only SAM/API behavior may be limited.

### Manual Developer Path

From the repo root:

```bash
python3 backend/server.py
```

Then open:

```text
http://localhost:5173
```

The app is intentionally local-first. It reads from the backend when running locally and falls back to static `app/data.js` if opened from disk.

## What The Designer Should Review

1. First viewport: map, selected parcel panel, reviewer flow.
2. Section 12 traceability: badges, source drawer, coverage matrix.
3. Parcel interaction: click parcel, inspect crop/confidence/stress/NDVI/advisory/evidence.
4. SAM boundary workflow: prompt/candidate/QC/publish-to-map story.
5. Mobile/tablet fit: controls, badges, map, drawer, and selected parcel content.

## Design Goal

Make the current artifact feel like a serious government tender-review product demo, not a hackathon dashboard.

The interface should communicate:

- operational confidence;
- auditability and Section 12 traceability;
- parcel-level evidence;
- clear distinction between shown/demo/planned capabilities;
- readiness for field, WebGIS, and DAC users.

## Guardrails

- Do not turn this into a marketing landing page.
- Keep the map and selected parcel workflow as the main product surface.
- Preserve the RFP traceability model: requirement badge -> demo surface -> source drawer.
- Keep mock/demo data visibly honest. Do not imply production Chhattisgarh deployment.
- Prefer quiet, dense, operational UI over decorative storytelling.
