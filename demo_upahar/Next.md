# Next: Section 12 Capability Demonstrator

Last updated: 2026-05-16

## Objective

Reshape `demo_upahar` from a generic agri-AI dashboard into a Section 12-backed tender capability demonstrator.

The app should answer one question quickly: "Where in this demo can I see the capability requested in UPAHAR RFP Section 12?"

## Current State

- [x] Static dashboard exists under `app/`.
- [x] Core demo surfaces exist: map layers, parcels, stress, yield, advisory, field evidence, procurement, integrations, reports.
- [x] Section 12 has been migrated from the knowledge pack into `rfp/`.
- [x] The migrated files include human-readable markdown, outline, and machine-readable JSON.
- [x] RFP badges, reviewer mode, Section 12 coverage matrix, and source requirement drawer exist in the static app.
- [x] Map now uses same-area Chhattisgarh imagery tiles with geospatially projected demo parcel overlays.
- [x] AI4Agri ML capability and SAM-assisted boundary workflow panels exist as static demonstrator surfaces.
- [x] Python backend serves the UI, demo payload, GeoJSON layers, imagery metadata, NISAR/SAR positioning, and file-backed tile endpoints.
- [x] UI reads from the backend first and keeps `app/data.js` as a static fallback.

## Source Files

- `rfp/section12.md`: full Section 12 source text for human review.
- `rfp/section12_outline.md`: compact outline for planning.
- `rfp/section12_sections.json`: structured source for UI mapping and requirement badges.
- `app/data.js`: current static demo data.
- `backend/server.py`: file-backed Python backend for API, GeoJSON, SAR metadata, and tiles.
- `docs/keynote_storyline.md`: CEO-facing tender storyline and budget framing.

## Immediate Implementation Plan

### 1. Normalize Section 12 Into Demo Requirements

- [x] Create a curated requirement map in `app/data.js` or a new static file.
- [x] For each important Section 12 item, include:
  - `section`: for example `12.2.5`
  - `title`
  - `summary`
  - `demoSurface`
  - `evidence`
  - `status`: `shown`, `mocked`, or `planned`

Keep this curated. Do not expose every paragraph as UI.

### 2. Add RFP Badges Across the UI

- [x] Add small badges such as `RFP 12.2.5` to relevant panels.
- [x] Start with:
  - Crop classification: `12.2.5`
  - Crop health: `12.2.6`
  - Acreage: `12.2.7`
  - Yield: `12.2.8`
  - MSP procurement: `12.2.9`, `12.5`
  - Disaster/crop loss: `12.3`
  - Advisories: `12.4`
  - DAC/WebGIS/mobile: `12.7`, `12.8`

### 3. Build Reviewer Mode

- [x] Add a guided checklist panel or top-level tab.
- [x] The flow should be:
  - Satellite imagery to crop map
  - Parcel-level crop confidence
  - Crop health and stress
  - Ground truth validation
  - Advisory generation
  - MSP procurement planning
  - DAC/WebGIS/mobile readiness
  - Reports, exports, integrations, O&M

Each step should select or highlight the matching demo panel.

### 4. Add Section 12 Coverage Matrix

- [x] Replace or improve the existing compliance list with a Section 12 coverage matrix.
- [x] Columns:
  - RFP section
  - Requirement
  - Demo proof
  - Evidence type
  - Status
- [x] Make rows clickable where practical.

### 5. Add Source Requirement Drawer

- [x] Let a reviewer click an RFP badge or matrix row.
- [x] Show:
  - Section title
  - Page range from the knowledge pack
  - Short requirement summary
  - Matching demo surface
  - Link/label to `rfp/section12.md`

This does not need search or chat. Static excerpts are enough.

## Next Action Items: Professional Demo Upgrade

The next phase should make this look like a serious tender-review artifact, not a hackathon dashboard. Keep the backend file-backed and lightweight, but make the imagery, ML evidence, product narrative, and interaction design feel deliberate.

### 1. Imagery Options That Stay Inside Section 12.2.1

- [x] Build an imagery decision table in `README.md` or `Next.md` with columns: provider/source, native GSD, spectral bands, revisit/cadence, cloud/SAR fallback, AOI availability, licensing, demo use.

| Source | Native GSD | Bands / signal | Cadence | Role in demo | Compliance posture |
|---|---:|---|---|---|---|
| PlanetScope ARPS | ~3 m | Blue, green, red, NIR | Near-daily where available | Best candidate for compliant temporal optical ML | Needs vendor access, AOI check, license |
| Maxar optical | 30 cm-class where available | RGB / multispectral by product | Archive/tasking | Boundary and cadastral visual proof | Strong visual proof; quote/license needed |
| Airbus Pléiades Neo | 30 cm native | Multispectral options | Tasking/revisit | Premium visual proof and high-end proposal signal | Quote/license needed |
| Esri Wayback | Varies by source | Visual basemap | Historical tile snapshots | Current same-area visual demo | Not procurement-grade without source metadata |
| Sentinel-2 | 10 m visible/NIR, coarser SWIR | Multispectral optical | 5-day revisit | Temporal ML features and indices | Supports ML, not 3 m optical proof |
| Sentinel-1 | SAR | C-band SAR | 6-12 day revisit | Cloud/monsoon fallback | Supports fallback/disaster story |
| NISAR | SAR products | L-band/S-band SAR products | Mission/product dependent | Future SAR fallback and temporal features | Not optical compliance; product processing needed |

- [x] Shortlist only sources that can satisfy or support the RFP requirement:
  - Planet Analysis-Ready PlanetScope: use if `3 m` orthorectified surface reflectance, near-daily cadence, and blue/green/red/NIR coverage are available for the Chhattisgarh AOI.
  - Maxar optical imagery: use for very-high-resolution boundary/cadastral visual proof where 30 cm-class imagery is available and licensing allows demo display.
  - Airbus Pléiades Neo: use for 30 cm native imagery and reactive tasking/intraday revisit where budget/licensing permits.
  - Esri World Imagery Wayback: keep as temporary visual basemap only; do not treat it as procurement-grade compliance evidence without source metadata.
  - Sentinel-2: keep as temporal multispectral ML input only; it supports 5-day revisit and 10 m RGB/NIR bands, but does not satisfy the 3 m spatial-resolution requirement.
  - Sentinel-1 SAR: use as cloudy/monsoon fallback narrative for flood/waterlogging/dry-spell resilience, not as optical crop-identification proof.
  - NISAR SAR: explore through ASF/Earthdata as a SAR fallback and temporal feature source, not as direct optical XYZ tiles or 3 m imagery compliance.
- [ ] For whichever high-res source VB can access, obtain four same-season AOI images matching early, mid, peak, and late crop stages.
- [ ] Record source metadata per image: acquisition date, native GSD, bands, cloud percentage, processing level, license/display constraints, and provider attribution.
- [ ] Replace Wayback tile IDs with the selected source or pre-rendered static image chips when licensing allows.
- [ ] For NISAR, verify whether the Chhattisgarh AOI has public L-band/S-band products for the target season, then convert any useful geocoded product into local backend tiles rather than trying to consume it as a web basemap.

### 1A. NISAR / SAR Tile Exploration

- [x] Treat NISAR as product files first: ASF/Earthdata search returns SAR products, not ready map tiles.
- [x] Use the backend endpoint `GET /api/sar/nisar` to keep demo positioning explicit: SAR fallback, crop-health/disaster signal, and temporal ML feature source.
- [ ] Prefer Level 2 geocoded or Level 3 analysis-ready products when available; avoid raw/complex SAR products for the first demo unless a specialist preprocessing path is already working.
- [ ] Download one AOI product for Chhattisgarh only after confirming product date, footprint, polarization/band, processing level, and license/access constraints.
- [ ] Convert product layers into demo-ready artifacts:
  - normalized grayscale/false-color PNG tiles for map display;
  - GeoTIFF/COG for future GIS workflows;
  - parcel-level summary JSON with backscatter/coherence/soil-moisture/change metrics.
- [ ] Store rendered tiles as `backend/tiles/nisar-<date>/<z>/<y>/<x>.png` and keep product metadata beside the generated ML output.
- [x] Do not represent NISAR as satisfying the RFP optical imagery requirement; it supports the SAR fallback, cloud resilience, disaster monitoring, and dry-spell/waterlogging story.

### 2. VB Steps To Run ML Models From AI4Agri

- [ ] On RunPod or local GPU, choose one small AOI chip and one fast model path first; do not start with the full competition stack.
- [ ] Reuse AI4Agri preprocessing ideas:
  - nodata/cloud masking discipline;
  - Sentinel-2 temporal stack handling;
  - vegetation indices: NDVI, NDRE, GCVI, EVI, SAVI, MSAVI, NDWI;
  - phenology features: peak date, integrated greenness, growing-season length, harmonic/Fourier summaries.
- [ ] Export a small demo artifact from AI4Agri-style code:
  - `parcel_id`;
  - epoch date;
  - predicted crop class;
  - confidence;
  - NDVI/EVI/NDWI;
  - stress score;
  - change label such as `fallow_to_paddy`, `healthy_to_waterlogged`, or `low_confidence_gt_required`.
- [ ] Convert that artifact to a static JSON file the app can load or copy into `app/data.js`.
- [ ] Start with the fastest defensible model:
  - sampled-pixel HGB or ExtraTrees over temporal summary features for a quick demo output;
  - then one U-Net/FPN/TinyViT visual result only if it materially improves the demo story.
- [ ] Use AI4Agri validation discipline in the app copy: holdout split, confusion matrix, per-class recall, label remapping, nodata handling, and visual mask review.
- [ ] Do not claim production model accuracy unless the AOI has real labels and a real holdout set.

### 3. DLR Cadastral Import

- [ ] Request official village-wise cadastral parcel vectors from Chhattisgarh DLR / Bhuiyan / LRMS before creating new boundaries.
- [ ] Ask for GIS-native formats first: GeoPackage, Shapefile, or GeoJSON, with `district`, `tehsil/block`, `village_code`, `khasra/survey_no`, recorded area, and official parcel/LRMS IDs where available.
- [ ] Confirm source CRS/projection and metadata before import; do not assume WGS84.
- [ ] Ingest raw cadastral data into a staging table such as `dlr_cadastral_raw` and keep that raw layer unchanged for audit.
- [ ] Normalize accepted parcels into the app/backend parcel schema:
  - `parcel_id`;
  - `village_code`;
  - `khasra_no`;
  - official source ID;
  - recorded area;
  - geometry transformed to WGS84 for GeoJSON/API output.
- [ ] Run topology and quality checks before using the layer in classification:
  - invalid geometries and self-intersections;
  - overlaps, gaps, and slivers;
  - missing `khasra_no` or village code;
  - area mismatch versus DLR recorded area;
  - duplicate parcel IDs within a village.
- [ ] Link cadastral parcels to farmer/land records using official parcel/LRMS/Bhuiyan IDs or `village_code + khasra_no`; do not join on owner names.
- [ ] Publish the imported cadastral layer through the backend as GeoJSON for small extracts and vector tiles for full WebGIS display.
- [ ] Replace demo polygons through `/api/geojson/parcels` once a real DLR import is available.
- [ ] Keep the RFP posture explicit: DLR cadastral import is the primary path; SAM/SamGeo and GPS/mobile digitization are fallback or correction workflows when cadastral parcels are missing, stale, or disputed.

### 3A. SAM / SamGeo Boundary Creation

- [x] Use SAM/SamGeo as a parcel-boundary annotation accelerator, not as the crop classifier.
- [x] Add an in-browser SAM annotation demonstrator: point/box prompts, candidate mask preview, human QC, and publish-to-map flow.
- [ ] Prepare a georeferenced high-res AOI chip for one village/block demonstration area.
- [ ] Run prompted segmentation with points or boxes over visible fields; avoid fully automatic masks unless the chip is clean.
- [ ] Export masks to GeoJSON/GPKG, simplify topology, remove slivers, and manually QC boundaries.
- [ ] Store final demo boundaries as lon/lat GeoJSON in the app.
- [x] Keep an explicit workflow label: `SAM-assisted candidate boundaries + human QC + temporal ML classification`.

### 4. Static App Integration

- [ ] Replace hand-authored `epochStates` with generated ML output once VB has the first model artifact.
- [ ] Add a small confusion-matrix or validation-summary card to the AI4Agri ML panel.
- [ ] Add a temporal change legend: class transition, confidence delta, stress delta, and GT-needed flag.
- [x] Keep source provenance visible: imagery provider, date, resolution, band stack, model run ID, and demo/mock status.
- [x] Add one-click demo route: `Review Section 12 -> imagery -> aligned parcel -> temporal model update -> advisory/procurement -> coverage matrix`.
- [x] Add a SAM/SamGeo demo route: `imagery chip -> prompted candidate masks -> human QC -> approved parcel boundary -> temporal ML state`.

### 4A. File-Backed Backend Integration

- [x] Add a backend that serves static UI assets from `app/`.
- [x] Serve the full dashboard payload from `GET /api/demo-data`.
- [x] Serve parcel, ground-truth, and procurement data as GeoJSON.
- [x] Serve imagery metadata and local-first tile endpoints.
- [x] Keep backend implementation Python-native for ML/SAM/SamGeo follow-on work.
- [ ] Move generated ML output into a dedicated `backend/data/` file instead of editing `app/data.js` directly.
- [ ] Add write/update scripts for parcel classes, confidence, stress scores, and temporal change labels.

### 5. Professional UI / VB Apple-Experience Pass

- [x] Apply Apple-style product principles: clarity, restraint, hierarchy, direct manipulation, and calm confidence.
- [ ] Reduce visual noise:
  - [x] badges should support traceability but not dominate the map;
  - [x] avoid crowding every card with all metadata at once;
  - [x] use progressive disclosure through the drawer and selected parcel panel.
- [x] Make the first viewport feel executive-grade:
  - [x] map and selected parcel should be the hero workflow;
  - [x] reviewer mode should be compact and purposeful;
  - [x] controls should read like instrumentation, not form clutter.
- [x] Move keynote-style evidence, report, mobile, and integration narrative out of the primary UI.
- [x] Tighten copy:
  - avoid words like `synthetic` in visible UI except where clearly explaining mock/demo data;
  - use `aligned demo parcel overlay`, `same-area imagery`, `temporal model state`, and `procurement-grade metadata pending`.
- [ ] Check mobile/tablet layout so text does not wrap awkwardly inside controls or badges.
- [ ] Use fewer, stronger status labels: `Shown`, `Demo`, `Planned`, `Needs source metadata`.
- [ ] Before every demo, open the app cold and verify the reviewer can understand the product in under 10 seconds.

### 6. CEO / Keynote Storyline

- [x] Create a CEO-facing storyline that frames the tender as product strategy and business opportunity, not only engineering.
- [x] Include product positioning, demo narrative, delivery phases, budget ranges, decision gates, and risks.
- [x] Generate initial 10-slide executive deck draft: https://slidesgpt.com/view/bcb1ec26b807
- [x] Add detailed costing appendix in `docs/cost_breakdown.md`.
- [ ] Convert the storyline into a polished Keynote/PPT deck after the CEO narrative is approved.
- [x] Add budget sensitivity framework for imagery, GT, cloud/GPU, integrations, and O&M.
- [ ] Replace placeholder imagery and GT ranges once vendor quotes and sample design are known.

## Source Links To Keep Handy

- Esri World Imagery Wayback: https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/mapping/use-world-imagery-wayback/
- Planet Analysis-Ready PlanetScope: https://docs.planet.com/data/imagery/arps/
- Maxar optical imagery: https://www.maxar.com/maxar-intelligence/products/optical-imagery
- Airbus Pléiades Neo: https://space-solutions.airbus.com/imagery/pleiades-neo/
- ESA Sentinel-2 facts: https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2
- USGS Sentinel-2 band/resolution reference: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-sentinel-2
- NASA NISAR data overview: https://science.nasa.gov/mission/nisar/data/
- ASF NISAR access overview: https://nisar-docs.asf.alaska.edu/access-overview/
- ASF NISAR product overview: https://nisar-docs.asf.alaska.edu/products-overview/
- ASF NISAR data format: https://nisar-docs.asf.alaska.edu/data-format/
- NRSC Bhoonidhi NISAR details: https://bhoonidhi.nrsc.gov.in/NISAR/
- SamGeo / Segment Geospatial: https://github.com/opengeos/segment-geospatial

## Useful Demo Storyline

Use this sequence during demos:

1. Open with the map-first command dashboard.
2. Show `12.2.5` crop identification by toggling crop classification and clicking a parcel.
3. Show `12.2.6` crop health with the stress layer and NDVI/EVI trend.
4. Show `12.2.2` ground truth validation from the parcel evidence tab.
5. Show `12.4` advisories by generating department, extension, and farmer messages.
6. Show `12.2.9 / 12.5` procurement planning from paddy acreage and PACS load.
7. Show `12.7 / 12.8` DAC/WebGIS/mobile readiness through the layer stack, exports, mobile flow, and integration panels.
8. Close with the coverage matrix so the reviewer sees Section 12 traceability.

## Keep It Lean

Keep these constrained:

- Backend: keep file-backed and Python-native until ML outputs justify a database.
- Database: defer PostGIS until real AOI/GT/model outputs are available.
- Login/auth: defer until a hosted stakeholder demo is required.
- Real map server: defer GeoServer/COG tiling until source imagery is licensed.
- Vector chat over the tender: defer; Section 12 traceability is already explicit.
- New ML training: start with small AI4Agri-style model artifacts, not full production training.
- Cloud deployment: defer until CEO approves bid/pilot budget.

The app becomes useful sooner if it remains a crisp, backend-backed walkthrough with strong RFP traceability and honest source provenance.

## Acceptance Criteria

- [x] A reviewer can start from Section 12 and find the matching demo capability in under 10 seconds.
- [x] Every major dashboard panel has at least one RFP Section 12 badge.
- [x] The coverage matrix distinguishes `shown`, `mocked`, and `planned`.
- [x] Mock data is still clearly labeled as demo data.
- [x] The demo still runs from static fallback or the Python backend.
- [x] No database, auth, cloud deployment, or production map server is required.
- [ ] CEO-facing budget and bid story are reviewed and approved.
- [ ] At least one real imagery or SAR-derived local tile set is added when source access is resolved.
