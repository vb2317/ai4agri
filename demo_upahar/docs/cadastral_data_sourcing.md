# Cadastral / Land Parcel Data Sourcing — Investigation Notes

Investigation into how to obtain vectorized land parcel polygons for Chhattisgarh, as required by the Upahar RFP.

## RFP requirement

From `rfp/section12.md` §12.2.3 (Georeferencing of Cadastral Maps), line 102:

> The selected Implementing Agency shall be responsible for acquiring cadastral maps from the **Department of Land Records (DLR), Chhattisgarh**, in **geo-referenced vector formats (e.g., shapefiles)**. The implementing agency will utilize these datasets in the available form, without performing any additional digitization, geo-referencing, or spatial processing.

Related references:
- §12.2.3 (line 131–133) — parcel-level crop classification ≥85%, fallback to village-level if cadastral data unavailable, parcel boundaries must be topologically clean.
- Farmer Registry (line 326–327) — each Khasra is linked to the **LRMS / Bhuiyan portal** (Chhattisgarh land records), with polygon import from cadastral or GPS walk-in.
- Integrations (line 719) — Land Records Management Systems listed as integration source for parcel details + ownership.

Canonical source: **DLR Chhattisgarh** — surfaced publicly via:
- `bhuiyan.cg.nic.in` — text/attribute records (owner, area, Khasra detail)
- `bhunaksha.cg.nic.in` — cadastral map viewer (vector data lives behind this)

## What each portal exposes

### `bhuiyan.cg.nic.in`
Attribute-only. URL patterns observed:
- `https://revenue.cg.nic.in/bhuiyanuser/User/Selection_Report_For_KhasraDetail.aspx?villno={giscode}&khasrano={n}` — Khasra detail (owner, area)
- `https://revenue.cg.nic.in/bhuiyanuser/User/ctz_SaskiyaReport_forall.aspx` — Government khasras
- `https://revenue.cg.nic.in/citizenui/` — B1/PII documents
- `https://revenue.cg.nic.in/revcase/` — Revenue court cases

No geometry data here.

### `bhunaksha.cg.nic.in`
Map viewer. Vector polygons are **not directly exposed**, but several endpoints surface partial data.

**Raster (WMS) — server renders polygons as PNG, not vector:**
- `GET /WMS?REQUEST=GetMap&LAYERS=VILLAGE_MAP&state=22&gis_code={giscode}&BBOX=...&CRS=EPSG:3857` — entire village rendered
- `GET /WMS?REQUEST=GetMap&LAYERS=PLOT_LIST&plot_id={opaque_id}&STYLES=PLOT_SELECTION` — single highlighted plot
- `GET /WMS?REQUEST=GetMap&LAYERS=SAME_OWNER_PLOT_LIST&plot_no={n}&STYLES=OWNER_PLOTS` — all plots of one owner
- No WFS endpoint exists (all `WFS`, `wfs`, `ows`, `geoserver/wfs` paths return 404).

**JSON click-test endpoints (attributes + bbox only, no polygon):**
- `GET /ScalarDatahandler?OP=4&state=22&levels={d,t,r,v,}&x={mercX}&y={mercY}` → returns:
  ```json
  {"plotNo":"480","ID":"3OdO...","gisCode":"570801.029","xmin":542035.27,"ymin":2478460.37,"xmax":542467.32,"ymax":2478842.00,"plotInfoLinks":"...","info":"खसरा नंबर : 480..."}
  ```
  Bounding box only, not actual polygon.
- `POST /rest/MapInfo/getPlotAtXY` with `state=22&giscode=...&x=...&y=...` → returns `{id, kide}`.
- `POST /rest/Layers/getLayers` with `state=22&layerType=TABLE_LAYER_MASTER&giscode=...` → layer metadata.

**Hierarchical IDs (state=22 = Chhattisgarh):**
- `giscode` format: `RRTTRI.VVV` (e.g. `570801.029` = district 57 / tehsil 08 / RI 01 / village 029)
- `levels` format: `RR,TT,RI,VVV,`
- `plot_id` is an opaque, hashed string (e.g. `3OdOfefXSueFtSCq4jiyLg`)

## The vector path: PDF reports

The plot-report page (`/22/plotreportCG.jsp?state=22&giscode={giscode}&plotno={n}`) embeds a **vector PDF** of the cadastral map. Discovered via:

- `POST /rest/CGReport/cgPlotreportPDF` with `{state, giscode, plotno, sameownerplotreport, allplotsofvillage, derivedlayerids, selectedlayerids, scaletextfield, moduleid}` → returns **base64-encoded PDF** for a single plot (with neighbor context).
- `POST /rest/PlotMapsQueueService/setPlotsMapQueueReport` with `allplotsofvillage: true` → queues async **whole-village PDF** job, returns an id.
- `POST /rest/PlotMapsQueueService/PlotMapQueueList` → returns `[{id, gisinfo, request_time, status, execution_time}, ...]`. Status `S` = ready.
- `POST /rest/PlotMapsQueueService/downloadPDF` with `{state, id}` → returns the assembled village PDF.
- `POST /rest/PlotMapsQueueService/deletePlotsMapQueueReport` → cleanup.

These PDFs are believed (not yet verified) to contain real vector paths rather than embedded rasters — government cadastral PDFs from this generator typically are vector.

## Proposed extraction pipeline

For a target village (e.g. `giscode=570801.029`):

1. **Acquire** — POST `setPlotsMapQueueReport` with `allplotsofvillage:true`; poll `PlotMapQueueList` until `status=S`; `downloadPDF`.
2. **Parse** — open with PyMuPDF, walk drawing commands, collect closed polygons + nearest text label (the printed Khasra number per parcel).
3. **Georeference** — solve affine transform from PDF coords → EPSG:3857. Anchors: per-plot bboxes from `ScalarDatahandler OP=4` (we already have plot 480: xmin/ymin/xmax/ymax in EPSG:3857). Two well-separated plots are enough to fit the transform; more for least-squares robustness.
4. **Enrich** — for each polygon's `plotno`, call `ScalarDatahandler OP=4` for owner/attributes; optionally scrape `Selection_Report_For_KhasraDetail.aspx` for full Khasra detail.
5. **Output** — `backend/data/cadastral/{giscode}.geojson`, one feature per parcel: `{plotNo, plot_id, owner_html, geometry}` in EPSG:4326.

Validation step before writing the scraper: fetch one `cgPlotreportPDF`, open with PyMuPDF, confirm vector paths exist (not just a raster image). 30-second check, needs a live `JSESSIONID` cookie.

## Known constraints + risks

- **Auth / ToS** — `.gov.in` revenue portal, no published API or scraping permission. Rate-limited polite scraping of one village's public records is the working assumption, but not formally sanctioned.
- **Session cookie** — `JSESSIONID` rotates; the scraper needs to maintain a session and re-acquire on rotation.
- **PDF format risk** — if PDFs turn out to be embedded rasters instead of vector paths, the fallback is OpenCV contour extraction from `WMS VILLAGE_MAP` at max resolution, georeferenced via `BBOX`, with plot labels resolved by calling `getPlotAtXY` on each centroid.
- **Topology** — RFP requires topologically clean parcel boundaries (no overlaps/gaps). Post-processing with `shapely.make_valid` + snapping will be needed regardless of source.
- **Production answer** — for a real Upahar deployment, the supported path is a formal data request to DLR Chhattisgarh for shapefiles, not scraping. Scraping is acceptable for demo / proof-of-concept.

## Status

- [x] Identified RFP requirement and canonical source
- [x] Mapped bhuiyan + bhunaksha endpoints
- [x] Found PDF-based vector path
- [ ] Verify PDFs contain vector paths (not rasters)
- [ ] Implement village PDF acquisition + queue polling
- [ ] Implement PDF → GeoJSON conversion
- [ ] Georeference + topology cleanup
- [ ] Attribute enrichment
