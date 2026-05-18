# UPAHAR Section 12 Capability Demonstrator

This demo is a tender-reviewer-friendly Agriculture Intelligence Command Dashboard backed by the extracted Section 12 scope from the Chhattisgarh UPAHAR RFP.

The goal is not to overbuild a production platform. The immediate goal is to make the demo useful as a capability walkthrough: a reviewer should be able to see a Section 12 requirement, click the matching demo surface, and understand how the AI4Agri work maps to the requested system.

## Current Source Material

Section 12 was migrated from the doc2llm knowledge pack into `rfp/`:

- `rfp/section12.md`: human-readable Section 12 text with section IDs and page ranges.
- `rfp/section12_outline.md`: compact outline for review and planning.
- `rfp/section12_sections.json`: machine-readable Section 12 sections for app data, badges, and coverage mapping.

These files are the local source of truth for tender traceability. Do not hand-copy requirements from the PDF into the app when they can be derived from these files.

## Demo App

The working prototype lives under `app/`:

- `app/index.html`: dashboard shell.
- `app/styles.css`: operational dashboard styling.
- `app/data.js`: static demo parcels, metrics, evidence, RFP mapping, and workflow data.
- `app/app.js`: layer toggles, SVG parcel map rendering, epoch control, parcel drilldown, advisory generation, and panels.

Run the backend-backed demo locally:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar
python3 backend/server.py
```

Then open `http://localhost:5173`.

The UI now reads from the backend first and falls back to `app/data.js` only when opened directly from disk. The backend is Python and dependency-free so ML/SAM/SamGeo outputs can be dropped in before a production database or map server exists.

Useful local endpoints:

- `GET /api/demo-data`: complete dashboard payload used by the UI.
- `GET /api/imagery/metadata`: AOI, epochs, imagery requirements, and tile template.
- `GET /api/geojson/parcels`: parcel polygons as GeoJSON for ML/SAM updates.
- `GET /api/geojson/ground-truth`: GT points as GeoJSON.
- `GET /api/geojson/procurement-centers`: procurement centers as GeoJSON.
- `GET /api/sar/nisar`: NISAR/SAR product notes, access path, and demo positioning.
- `GET /api/tiles/<epoch-id>/<z>/<y>/<x>.png`: local tile first, remote Wayback fallback.

To override imagery with local tiles, place files under:

```text
backend/tiles/<epoch-id>/<z>/<y>/<x>.png
```

For example, the current epoch IDs are the imagery dates in `app/data.js`, such as `2025-09-04`.

NISAR is not treated as a direct optical basemap tile provider. Use it as a SAR fallback and temporal feature source: discover/download products from ASF/Earthdata, extract geocoded backscatter/coherence/soil-moisture layers, render derived PNG/COG tiles, and place them under `backend/tiles/nisar-<date>/...` when they are ready for the demo.

The previous static option still works for quick inspection:

```bash
cd /Users/vb/dev/projects/ai4agri/demo_upahar/app
python3 -m http.server 5173
```

Then open `http://localhost:5173`.

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
- Chhattisgarh-specific parcels, procurement centers, farmer records, GT points, and integration endpoints are demo/mock data unless replaced with real datasets.
- The app should clearly communicate capability shape, delivery understanding, and implementation approach. It should not imply production deployment or live government integration.

## Near-Term Build Priorities

1. Replace demo polygons through `/api/geojson/parcels` after SAM/SamGeo boundary creation.
2. Add a small ML output loader that writes updated parcel class, confidence, NDVI/EVI, and stress by epoch.
3. Add local imagery tiles or a tile cache for the selected Chhattisgarh AOI and season dates.
4. Keep the Section 12 reviewer flow, badges, and coverage matrix as the demo navigation spine.
5. Move from file-backed APIs to PostGIS/COG/GeoServer only after the professional demo story is stable.

## Non-Goals

- No real auth, cloud deployment, database, or vector search for the immediate demo.
- No fresh model training.
- No real AgriStack, LRMS/Bhuiyan, Food Department, MARKFED, CCB, mandi, weather, Aadhaar, blockchain, or farmer-registration integration.
- No claims of live Chhattisgarh production data unless real data is added later.
