# MP Agri Insurance Risk Command

This demo is a Madhya Pradesh agri-insurance risk command dashboard for parcel creation, Sentinel-2 crop intelligence, and LGND.ai human-in-the-loop review.

The current product shape has three tabs:

- `Parcel Creator`: SAM-backed parcel boundary creation and correction.
- `Sentinel-2 Intelligence`: crop type, crop stress, confidence, and vegetation-index outputs from seasonal imagery.
- `LGND Review`: analyst review for similar or changed chips flagged by the ML model.

The goal is not to overbuild a production platform. The immediate goal is to keep a crisp insurer workflow that can absorb real Sentinel-2 tiles, ML outputs, SAM/SamGeo boundaries, and LGND search results while remaining honest about demo data.

## Background Evidence

Section 12 was migrated from the doc2llm knowledge pack into `rfp/`:

- `rfp/section12.md`: human-readable Section 12 text with section IDs and page ranges.
- `rfp/section12_outline.md`: compact outline for review and planning.
- `rfp/section12_sections.json`: machine-readable Section 12 sections for app data, badges, and coverage mapping.

These files remain local background evidence for tender traceability, but they are not the default product navigation.

## Demo App

The working prototype lives under `app/`:

- `app/index.html`: dashboard shell.
- `app/styles.css`: operational dashboard styling.
- `app/data.js`: static demo parcels, metrics, ML/SAM/LGND workflow data, and background evidence mapping.
- `app/app.js`: product tabs, SVG parcel map rendering, epoch control, parcel drilldown, SAM workflow, ML panels, and LGND status flow.

## Run The Server

Run the backend-backed dashboard locally:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar
python3 backend/server.py
```

Then open `http://localhost:5173`.

The backend defaults to port `5173`. To use another port:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar
PORT=5181 python3 backend/server.py
```

Then open `http://localhost:5181`.

The UI reads from the backend first and falls back to `app/data.js` only when opened directly from disk. The backend is Python-first and file-backed so Sentinel-2 tiles, ML outputs, SAM/SamGeo boundaries, and LGND.ai responses can be dropped in before a production database or map server exists.

Useful server checks:

```bash
curl http://localhost:5173/api/health
curl http://localhost:5173/api/demo-data
curl http://localhost:5173/api/imagery/metadata
```

Core local endpoints:

- `GET /api/demo-data`: complete dashboard payload used by the UI.
- `GET /api/imagery/metadata`: AOI, epochs, imagery requirements, and tile template.
- `GET /api/geojson/parcels`: parcel polygons as GeoJSON for ML/SAM updates.
- `GET /api/geojson/ground-truth`: GT points as GeoJSON.
- `GET /api/geojson/procurement-centers`: claim-service / operations hubs as GeoJSON.
- `GET /api/sar/nisar`: NISAR/SAR product notes, access path, and demo positioning.
- `GET /api/tiles/<epoch-id>/<z>/<y>/<x>.png`: local tile first, remote fallback.
- `GET /api/ml/predictions`: per-parcel crop/stress predictions, confidence, uncertainty, index curve, imagery dates, cloud score, model version, and `changeLabel`/`gtNeeded` flags.
- `GET /api/ml/validation`: confusion matrix, per-class recall, overall/balanced accuracy, and the honesty note powering the Sentinel-2 validation card.
- `GET /api/parcels/export`: approved insured-parcel boundaries as GeoJSON for the ML aggregation step.
- `POST /api/sam/auto`: SAM automatic mask generation over the chip viewport — returns every probable field boundary as candidate polygons (the Parcel Creator default when no point/box prompt is placed). Runs on CPU (Apple MPS rejects a float64 op in the generator); the first call loads the model, so it is slower than subsequent calls.
- `POST /api/sam/suggest`: prompted SAM (point/box) for refining a single field boundary.

ML artifacts are read from `backend/data/generated/` (freshly generated, gitignored) with a committed fallback in `backend/seed/`.

## Sentinel-2 + ML Pipeline

Scripts under `backend/scripts/` produce the artifacts the Sentinel-2 tab consumes. They run against the project venv (`../.venv`), which carries `rasterio`, `scikit-learn`, `shapely`, and `requests`.

```bash
# 1. Build the per-parcel temporal artifact (indices + seasonal summaries).
#    Demo mode derives it from the curated parcels; no credentials needed.
../.venv/bin/python backend/scripts/ingest_sentinel2.py --mode demo

# 2. Train the crop classifier + stress heuristic and emit predictions + validation.
../.venv/bin/python backend/scripts/run_ml_predictions.py        # --model extratrees optional

# 3. Export approved parcel boundaries as GeoJSON for the aggregation step.
../.venv/bin/python backend/scripts/export_parcels.py            # --approved <published.json>
```

Real Sentinel-2 ingestion (VB): set `CDSE_USER`/`CDSE_PASS` (Copernicus Data Space login) and run
`ingest_sentinel2.py --mode copernicus --bbox "minLon minLat maxLon maxLat" --windows "start/end,..."`.
Scene search is wired; per-parcel asset clipping + index extraction is the remaining credentialed step.

The shipped artifact is a deliberate demonstrator: weak/curated labels over 8 parcels yield ~38% leave-one-out accuracy, so it is surfaced honestly (validation card + `validationStatus`) rather than overwriting the curated executive demo. Replace with real Sentinel-2 + field labels before any accuracy claim.

The previous static option still works for quick inspection, but it will not enable backend APIs, tile caching, SAM backend inference, or LGND.ai proxy calls:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar/app
python3 -m http.server 5173
```

Then open `http://localhost:5173`.

## LGND.ai Integration

LGND.ai is integrated through a backend proxy. The browser never receives the API key. Do not put the token in `app/`, `data.js`, localStorage, screenshots, or committed files.

For local development, put the token in the ignored `.env` file:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar
printf 'LGND_TOKEN="YOUR_LGND_API_KEY"\n' > .env
python3 backend/server.py
```

You can also start the server with `LGND_TOKEN` exported in the shell:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar
export LGND_TOKEN="YOUR_LGND_API_KEY"
python3 backend/server.py
```

Or with a custom port:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar
export LGND_TOKEN="YOUR_LGND_API_KEY"
PORT=5181 python3 backend/server.py
```

Optional override:

```bash
export LGND_API_BASE="https://embeddings.api.lgnd.ai/v1"
```

Check whether the backend sees the LGND token:

```bash
curl http://localhost:5173/api/lgnd/status
```

The expected `configured` value is `true` when `LGND_TOKEN` is present in the backend process environment.

Local LGND proxy endpoints:

- `GET /api/lgnd/status`
- `GET /api/lgnd/tenants`
- `GET /api/lgnd/collections?tenantId=<tenant-id>`
- `GET /api/lgnd/indexes?tenantId=<tenant-id>&collectionId=<collection-id>`
- `POST /api/lgnd/filter-by-geometry`
- `POST /api/lgnd/search-by-location`
- `POST /api/lgnd/search-changed-chips`

Example flow:

```bash
curl http://localhost:5173/api/lgnd/tenants
```

Use the returned tenant ID to list collections:

```bash
curl "http://localhost:5173/api/lgnd/collections?tenantId=<tenant-id>"
```

Search by location:

```bash
curl -X POST http://localhost:5173/api/lgnd/search-by-location \
  -H "Content-Type: application/json" \
  -d '{
    "tenantId": "<tenant-id>",
    "collectionId": "<collection-id>",
    "latitude": 22.75,
    "longitude": 77.73,
    "start_date": "2025-06-01",
    "end_date": "2025-10-31",
    "top_k": 10
  }'
```

Filter chips by an insured parcel or claim-cluster geometry:

```bash
curl -X POST http://localhost:5173/api/lgnd/filter-by-geometry \
  -H "Content-Type: application/json" \
  -d '{
    "tenantId": "<tenant-id>",
    "collectionId": "<collection-id>",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [77.7200, 22.7501],
        [77.7216, 22.7502],
        [77.7222, 22.7492],
        [77.7200, 22.7501]
      ]]
    },
    "limit": 100
  }'
```

Run changed-chip search for claim triage:

```bash
curl -X POST http://localhost:5173/api/lgnd/search-changed-chips \
  -H "Content-Type: application/json" \
  -d '{
    "tenantId": "<tenant-id>",
    "collectionId": "<collection-id>",
    "positive_texts_past": ["healthy green crop"],
    "positive_texts_current": ["bare soil, dry crop, stressed vegetation"],
    "top_k": 20
  }'
```

Current demo posture:

- LGND calls are live only when `LGND_TOKEN` is set.
- The UI shows LGND credential status in the LGND panel.
- The current app uses LGND for embedding/search/change-discovery workflow integration, not as a replacement for Sentinel-2 ingestion or parcel-level ML.
- If LGND has no ready Sentinel-2 collection over the Madhya Pradesh AOI, first create or select a collection/index from the LGND developer portal/API before running search calls.

To override imagery with local tiles, place files under:

```text
backend/tiles/<epoch-id>/<z>/<y>/<x>.png
```

For example, the current epoch IDs are the imagery dates in `app/data.js`, such as `2025-09-02`.

NISAR is not treated as a direct optical basemap tile provider. Use it as a SAR fallback and temporal feature source: discover/download products from ASF/Earthdata, extract geocoded backscatter/coherence/soil-moisture layers, render derived PNG/COG tiles, and place them under `backend/tiles/nisar-<date>/...` when they are ready for the demo.

## Product Strategy

Use Section 12 as the navigation spine for the demo.

| Section 12 area | Demo surface |
|---|---|
| `12.2.1` Satellite imagery procurement and specification | Multi-date imagery epoch control and source-layer evidence |
| `12.2.2` Ground truth data collection | Field validation feed, GT point markers, QC status, holdout split |
| `12.2.3` Cadastral georeferencing | Parcel-level WebGIS view and boundary verification narrative |
| `12.2.4` Crop acreage and production monitoring | Acreage cards, production estimate, crop-wise summaries |
| `12.2.5` Crop identification | Crop classification layer, parcel crop label, confidence score |
| `12.2.6` Crop health monitoring | NDVI/EVI trend, stress layer, stress cause, alert counts |
| `12.2.7` Crop acreage estimation | District/block/village acreage summaries and export queue |
| `12.2.8` Yield modeling and production estimation | Yield forecast panel and parcel production calculation |
| `12.2.9` MSP procurement planning | Paddy procurement load, PACS demand, token capacity |
| `12.2.10` Drought and dry spell monitoring | Stress-risk layer and dry-spell advisory narrative |
| `12.3` Disaster monitoring and crop loss | Flood/waterlogging and crop-loss flags on parcels |
| `12.4` Advisories | Department, extension officer, and farmer advisory variants |
| `12.5` Paddy procurement module | Procurement planning and digital-token workflow narrative |
| `12.7` Data Analytics Center setup | DAC-style dashboard, monitoring, reports, command view |
| `12.8` DAC, WebGIS, mobile, OGC services | Map-first UI, WMS/WFS/WCS labels, mobile flow, integrations |
| `12.9-12.27` Delivery, cloud, testing, O&M | Coverage matrix, report queue, integration readiness, audit posture |

## What Makes It Useful Now

The useful artifact is not a generic agri dashboard. It is a traceable Section 12 walkthrough:

1. Show the reviewer a requirement badge, for example `RFP 12.2.5`.
2. Show the working demo surface, for example crop classification on parcel polygons.
3. Show the evidence or explanation, for example confidence score, GT link, AI4Agri capability note, and export/report pathway.
4. Move to the next Section 12 capability without requiring the reviewer to inspect the PDF.

This keeps the app static and simple while making it directly useful for tender discussions.

## Data Positioning

- AI4Agri work is evidence of technical capability in remote sensing, crop classification, validation, and reproducible workflows.
- Madhya Pradesh parcels, claim-service hubs, farmer records, GT points, and integration endpoints are demo/mock data unless replaced with real datasets.
- The app should clearly communicate capability shape, delivery understanding, and implementation approach. It should not imply production deployment or live government integration.

## Near-Term Build Priorities

1. Replace demo polygons through `/api/geojson/parcels` after SAM/SamGeo boundary creation.
2. Add a small ML output loader that writes updated parcel class, confidence, NDVI/EVI, and stress by epoch.
3. Add local imagery tiles or a tile cache for the selected Madhya Pradesh AOI and season dates.
4. Keep the Section 12 reviewer flow, badges, and coverage matrix as the demo navigation spine.
5. Move from file-backed APIs to PostGIS/COG/GeoServer only after the professional demo story is stable.

## Non-Goals

- No real auth, cloud deployment, database, or vector search for the immediate demo.
- No fresh model training.
- No real AgriStack, LRMS/Bhuiyan, Food Department, MARKFED, CCB, mandi, weather, Aadhaar, blockchain, or farmer-registration integration.
- No claims of live Madhya Pradesh production, policy, farmer, or claim data unless real data is added later.
