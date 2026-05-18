# RFP Brief For Design Review

Source of truth: `rfp/section12.md`.

The designer does not need to read every line first. These are the UI-relevant requirements that the demo must make visible.

## 12.2.1 Satellite Imagery

The system must use multi-date satellite imagery for crop monitoring. The RFP asks for at least 3 m or better optical imagery, four dates per crop season, key growth stages, complete agricultural coverage, preprocessing, and SAR/microwave fallback during cloudy or extreme weather periods.

UI implication: show imagery date/epoch, source metadata, spatial-resolution posture, and SAR fallback status. Be explicit when current imagery is demo-grade.

## 12.2.2 Ground Truth

Ground truth surveys must cover 1-2% of sown area per season, use stratified sampling, collect crop attributes and geotagged photos, pass QC, reserve 30% for independent validation, and integrate into WebGIS.

UI implication: field evidence, GT points, QC status, holdout/validation language, and photo/audit trace should be visible but not clutter the map.

## 12.2.3 Cadastral Maps

The SI must acquire cadastral maps from Chhattisgarh DLR in geo-referenced vector format and use them as available.

UI implication: parcel boundaries should be framed as DLR/Bhuiyan/LRMS import first, with independent delineation as fallback where cadastral data is missing.

## 12.2.5 Crop Identification

The system must provide parcel-level crop classification, confidence score per parcel, multi-temporal phenology, vegetation indices, hybrid ML/rule-based refinement, multi-cropping/intercropping where feasible, confusion matrices, and GIS-compatible outputs.

UI implication: every selected parcel should show crop class, confidence, evidence, temporal signal, and methodology/provenance.

## Boundary Creation

If cadastral data is unavailable, the agency must delineate farm boundaries independently. Generated parcel boundaries must be topologically clean, with no overlaps or gaps.

UI implication: boundary creation workflow should show candidate boundary, human QC, topology cleanup, and publish-to-map. Do not present SAM as the classifier; it is an annotation accelerator.

## 12.2.6 Crop Health

The system must produce pixel-level and parcel-level crop health maps using NDVI/EVI/SAVI/NDWI and detect stress, moisture, nutrient deficiency, pests/disease, flood/waterlogging, and drought.

UI implication: selected parcel should show stress status, time-series trend, cause, severity, and alert/action path.

## 12.2.7-12.2.9 Acreage, Yield, Procurement

The system must generate crop acreage estimates, detect changes, estimate yield/production, and support MSP procurement planning.

UI implication: area, crop-wise summaries, production estimates, procurement load, and export/report readiness should be visible.

## 12.3 Disaster And Crop Loss

The system must assess flood/drought/crop loss at parcel, village, block, and district levels, with field validation and severity classification.

UI implication: map layers and parcel detail should support disaster/crop-loss flags and triage workflows.

## 12.4 Advisories

The advisory system must produce role-based advisories for department users, extension functionaries, and farmers.

UI implication: selected parcel should demonstrate advisory variants and show how advisories link to parcel geometry and crop state.

## 12.7-12.8 DAC, WebGIS, Mobile

The platform must support DAC dashboards, WebGIS layers, OGC-style services, mobile/offline field workflows, parcel search, cached parcel boundaries, GNSS/GPS boundary capture, and parcel-linked evidence upload.

UI implication: the demo should feel like a command dashboard with map layers, parcel drilldown, source traceability, export/API readiness, and mobile/field workflow references.

## Status Language To Preserve

Use clear statuses:

- `Shown` - visible in the current UI.
- `Demo` - represented with mock/demo data.
- `Planned` - intended but not implemented.
- `Needs source metadata` - requires real imagery/vendor/data provenance before procurement-grade claim.

