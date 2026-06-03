const UPAHAR_DEMO_DATA = {
  basemap: {
    provider: "Satellite imagery",
    service: "COG/STAC with WMTS fallback",
    aoi: "Madhya Pradesh demo AOI: Narmadapuram-Sehore insured agriculture corridor",
    attribution: "Sentinel-2 signal: Copernicus/ESA. Visual basemap: Esri World Imagery.",
    sourceUrl: "https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2",
    tileUrl: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    zoom: 16,
    tileSize: 256,
    displayMetersPerPixel: 10,
    center: { lat: 22.70, lon: 77.73 },
    rfpSpatialRequirement: "Sentinel-2 10 m MSI operational imagery",
    rfpTemporalRequirement: "5-day revisit with four crop-stage dates per season",
    rfpBandRequirement: "B2/B3/B4/B8 visible+NIR, red-edge/SWIR indices, and SAR fallback when cloudy",
    complianceNote: "This insurer demo moves the operational analytic stack to Sentinel-2. The visible basemap remains a fallback until Sentinel-2 COG/XYZ tiles are rendered into backend/tiles."
  },
  insurer: {
    name: "Aviral General Insurance",
    geography: "Madhya Pradesh pilot portfolio",
    product: "PMFBY plus parametric crop-loss workflow",
    riskCrop: "Soybean",
    heroStats: [
      { label: "Insured exposure", value: "₹184Cr", detail: "Kharif portfolio in pilot AOI" },
      { label: "Claims pre-flagged", value: "1,426", detail: "Satellite-first triage queue" },
      { label: "Field visits saved", value: "62%", detail: "Low-risk packets auto-routed" },
      { label: "Review window", value: "5 days", detail: "How often fields are re-checked" }
    ],
    claimSummary: [
      { label: "Soybean area", value: "108.6 ha" },
      { label: "Exposure at risk", value: "₹42.8Cr" },
      { label: "Open claim packets", value: "3,650" }
    ]
  },
  epochs: [
    { label: "Early season", date: "2025-06-24", tileSet: "48925", note: "Sowing emergence, insured acreage activation, and first crop signature separation" },
    { label: "Mid season", date: "2025-07-29", tileSet: "49999", note: "Canopy development, moisture stress, and claim watchlist formation" },
    { label: "Peak season", date: "2025-09-02", tileSet: "52304", note: "Maximum vegetation signal, yield expectation, and loss-baseline freeze" },
    { label: "Late season", date: "2025-10-17", tileSet: "20512", note: "Harvest readiness, claim liability finalization, and loss assessment" }
  ],
  layers: [
    { id: "crop", label: "Insured crop classification", kind: "polygon", active: true, service: "WMS/WFS", requirements: ["12.2.5", "12.2.7"] },
    { id: "stress", label: "Loss and stress severity", kind: "polygon", active: true, service: "WMS", requirements: ["12.2.6", "12.2.10", "12.3"] },
    { id: "yield", label: "Liability and yield intensity", kind: "polygon", active: false, service: "WCS", requirements: ["12.2.7", "12.2.8"] },
    { id: "lgnd", label: "LGND changed-chip search", kind: "embedding", active: false, service: "LGND API", requirements: ["12.2.6", "12.3", "12.14"] },
    { id: "sam", label: "SAM boundary candidates", kind: "polygon", active: false, service: "GeoJSON/GPKG", requirements: ["12.2.3", "12.8"] },
    { id: "gt", label: "Field loss validation", kind: "point", active: true, service: "WFS", requirements: ["12.2.2"] },
    { id: "procurement", label: "Claim service hubs", kind: "point", active: true, service: "REST", requirements: ["12.2.9", "12.5"] }
  ],
  metrics: [
    { id: "exposure", label: "Insured exposure", value: "₹184Cr", detail: "Madhya Pradesh pilot crop portfolio", trend: "₹42.8Cr at risk", requirements: ["12.2.4", "12.2.7"] },
    { id: "confidence", label: "Crop ID confidence", value: "87.4%", detail: "Sentinel-2 temporal classifier confidence", trend: ">=85%", requirements: ["12.2.5"] },
    { id: "stress", label: "Loss alerts", value: "142", detail: "Moisture, pest, drought, and delayed sowing", trend: "31 severe", requirements: ["12.2.6", "12.2.10", "12.3"] },
    { id: "yield", label: "Liability forecast", value: "₹27.6Cr", detail: "Expected payout exposure under stress", trend: "-3.1% yield", requirements: ["12.2.8"] },
    { id: "gt", label: "Field validation", value: "1.6%", detail: "Stratified loss assessment sample", trend: "30% holdout", requirements: ["12.2.2"] },
    { id: "lgnd", label: "LGND matches", value: "83", detail: "Changed chips queued for analyst review", trend: "top-k scan", requirements: ["12.3", "12.14"] }
  ],
  crops: {
    Soybean: { color: "#58d68d", short: "SY" },
    Paddy: { color: "#4ecdc4", short: "PD" },
    Maize: { color: "#f2c94c", short: "MZ" },
    Gram: { color: "#c084fc", short: "GR" },
    Wheat: { color: "#f5d36f", short: "WH" },
    Fallow: { color: "#9ca3af", short: "FL" },
    Pending: { color: "#20a4ad", short: "ML" }
  },
  stressColors: {
    Low: "#4f9d69",
    Moderate: "#d1a533",
    High: "#c55a4a",
    Severe: "#8f2f38"
  },
  parcels: [],
  groundTruth: [
    { id: "GT-1042", lon: 77.7211165, lat: 22.6991804, crop: "Paddy", status: "Validated", split: "Training", gps: "1.8 m", officer: "VAA Narmadapuram-04" },
    { id: "GT-1088", lon: 77.7244210, lat: 22.6990605, crop: "Soybean", status: "Validated", split: "Validation holdout", gps: "2.1 m", officer: "VAA Itarsi-02" },
    { id: "GT-1121", lon: 77.7287555, lat: 22.6990605, crop: "Gram", status: "QC review", split: "Validation holdout", gps: "2.7 m", officer: "VAA Itarsi-07" },
    { id: "GT-1190", lon: 77.7309871, lat: 22.6986607, crop: "Paddy", status: "Pending revisit", split: "Training", gps: "3.4 m", officer: "VAA Seoni Malwa-03" },
    { id: "GT-1233", lon: 77.7351498, lat: 22.6986207, crop: "Fallow", status: "Validated", split: "Validation holdout", gps: "1.5 m", officer: "VAA Babai-01" }
  ],
  procurementCenters: [
    { id: "CLM-BAN-12", name: "Bankhedi Claim Desk", lon: 77.7240133, lat: 22.7019589, load: 82, arrivals: "₹14.2Cr exposure", tokens: 1260, risk: "High", status: "Desk surge" },
    { id: "CLM-ITA-04", name: "Itarsi Survey Cell", lon: 77.7326822, lat: 22.7002199, load: 64, arrivals: "₹9.8Cr exposure", tokens: 870, risk: "Normal", status: "Normal triage" },
    { id: "CLM-BAB-08", name: "Babai Loss Unit", lon: 77.7376818, lat: 22.6988606, load: 91, arrivals: "₹18.8Cr exposure", tokens: 1520, risk: "High", status: "Add survey teams" }
  ],
  advisoryTemplates: {
    department: "Prioritize {village} for {riskCause}. Current insured {crop} acreage is {acreage} ha with {confidence}% model confidence and {stress} stress. Route high-risk packets to survey teams before payout review.",
    extension: "Visit parcel {id} during the current {stage} stage. Confirm crop condition, moisture status ({moisture}), and farmer-reported symptoms. Upload geo-tagged image evidence and close the claim QC loop.",
    farmer: "Your insured {crop} parcel is in {stage}. Current advisory: {advisory} Expected harvest window: {harvestWindow}. Keep field photos ready if an officer requests claim validation."
  },
  mobileFlow: [
    { step: "01", title: "Pin or walk parcel boundary", body: "Farmer or VAA captures GPS boundary, draws polygon on satellite basemap, or verifies cadastral import.", requirements: ["12.2.3", "12.8.7"] },
    { step: "02", title: "Validate crop and stage", body: "Mobile app compares farmer crop claim with satellite crop classification and NDVI/EVI trend.", requirements: ["12.2.2", "12.2.5", "12.8.7"] },
    { step: "03", title: "Upload field evidence", body: "Geo-tagged photos, short videos, notes, pest/disease observations, and damage records sync to the insurer command center.", requirements: ["12.2.2", "12.3", "12.8.7"] },
    { step: "04", title: "Receive claim guidance", body: "Parcel-specific sowing, stress, irrigation, pest, weather, harvest, disaster, and claim-status guidance are pushed back.", requirements: ["12.4", "12.8.7"] }
  ],
  integrations: [
    { name: "AgriStack / NFR", status: "Planned API", detail: "UFID, farmer registry, demographic sync", requirements: ["12.4", "12.9"] },
    { name: "MP Land Records / Khasra", status: "Planned API", detail: "Khasra, parcel geometry, ownership link", requirements: ["12.2.3", "12.9"] },
    { name: "Soil Health Card", status: "Planned API", detail: "Soil parameters for nutrient advisory", requirements: ["12.4", "12.9"] },
    { name: "IMD / AWS Weather", status: "Planned API", detail: "Rainfall, temperature, humidity, wind", requirements: ["12.2.8", "12.4", "12.9"] },
    { name: "Insurer Core / Claims", status: "Planned API", detail: "Policy ID, premium, claim packet, payout status", requirements: ["12.2.9", "12.5", "12.9"] },
    { name: "LGND Embeddings API", status: "Planned API", detail: "Collections, indexes, changed chips, geometry search", requirements: ["12.3", "12.14"] },
    { name: "Disaster Systems", status: "Planned API", detail: "Flood, drought, crop loss, compensation", requirements: ["12.3", "12.9"] }
  ],
  reports: [
    { name: "Insured acreage estimation", cadence: "Two times per season", formats: "PDF, CSV, GeoJSON", status: "Ready", requirements: ["12.2.7", "12.27"] },
    { name: "Yield and liability estimate", cadence: "Two times per season", formats: "PDF, XLSX", status: "Ready", requirements: ["12.2.8", "12.27"] },
    { name: "Crop stress and health", cadence: "Weekly", formats: "PDF, GeoTIFF", status: "Scheduled", requirements: ["12.2.6", "12.27"] },
    { name: "Drought / flood / crop loss", cadence: "Event occurrence", formats: "PDF, GeoJSON, GeoTIFF", status: "Event-driven", requirements: ["12.2.10", "12.3", "12.27"] },
    { name: "Claim triage packet", cadence: "Daily during event", formats: "PDF, CSV, JSON", status: "Scheduled", requirements: ["12.3", "12.4", "12.27"] }
  ],
  evidence: [
    {
      title: "Multi-temporal Sentinel-2 workflows",
      body: "AI4Agri work already handles 34-date Sentinel-2 time series, vegetation indices, phenology features, masks, and model review artifacts.",
      requirements: ["12.2.1", "12.2.5", "12.2.6"]
    },
    {
      title: "Crop classification and validation discipline",
      body: "Competition pipelines include leakage-aware crop classification, confusion metrics, class handling, and reproducible packaging checks.",
      requirements: ["12.2.2", "12.2.5", "12.15/12.19"]
    },
    {
      title: "Remote-sensing product thinking",
      body: "The demo translates model outputs into parcel maps, confidence, stress layers, acreage, advisories, and decision-support dashboards.",
      requirements: ["12.2.7", "12.2.8", "12.4", "12.8"]
    },
    {
      title: "Insurer-safe positioning",
      body: "Madhya Pradesh parcels, claims centers, and farmer records are demo data; AI4Agri artifacts are used as technical proof of capability.",
      requirements: ["12.1", "12.9", "12.23/12.24"]
    }
  ],
  mlCapabilities: [
    {
      title: "Multi-temporal Sentinel-2 stack",
      metric: "34 frames",
      body: "AI4Agri work handled multi-date Sentinel-2 sequences with 10-band inputs, nodata masking, temporal aggregation, and per-pixel model outputs.",
      tags: ["Sentinel-2", "Time series", "Nodata masks"],
      requirements: ["12.2.1", "12.2.5", "12.2.6"]
    },
    {
      title: "Vegetation and phenology features",
      metric: "9+ indices",
      body: "Feature design includes NDVI, NDRE, GCVI, EVI, SAVI, MSAVI, NDWI, peak timing, integrated greenness, season length, and Fourier signals.",
      tags: ["NDVI", "EVI", "Phenology"],
      requirements: ["12.2.5", "12.2.6", "12.2.8"]
    },
    {
      title: "Model portfolio",
      metric: "HGB | U-Net | TinyViT",
      body: "The repo includes sampled-pixel gradient boosting, U-Net/FPN-style spatial models, TinyViT experiments, ordinal decoding, TTA, and ensemble post-processing.",
      tags: ["Classification", "Segmentation", "Ensemble"],
      requirements: ["12.2.5", "12.2.8", "12.15/12.19"]
    },
    {
      title: "Validation discipline",
      metric: "Holdout + QC",
      body: "Competition work exposed label remapping, nodata handling, class recall, confusion review, visual mask inspection, and package validation before submission.",
      tags: ["Holdout", "Confusion matrix", "Audit"],
      requirements: ["12.2.2", "12.2.5", "12.15/12.19"]
    }
  ],
  lgndFlow: [
    {
      step: "01",
      title: "Create MP Sentinel-2 AOI collection",
      endpoint: "create_collection",
      body: "Create a LGND collection for the insured Narmadapuram-Sehore AOI and Kharif date range. The collection generates embeddings from open Sentinel-2 imagery and keeps chips tied to capture timestamps.",
      status: "Credential required"
    },
    {
      step: "02",
      title: "Build a vector index",
      endpoint: "indexes",
      body: "Once the collection is READY, build the LGND index so every 128 px or 256 px Sentinel-2 chip can be searched by location, similarity, or concept.",
      status: "Planned"
    },
    {
      step: "03",
      title: "Filter insured parcels by geometry",
      endpoint: "filter-by-geometry",
      body: "Submit claim cluster polygons or parcel envelopes to retrieve intersecting chip IDs, sorted by acquisition date, and attach them to the claim packet.",
      status: "Demo flow"
    },
    {
      step: "04",
      title: "Run changed-chip search",
      endpoint: "search-changed-chips",
      body: "Compare past healthy-crop chips against current stressed or bare-soil chips. Results return changed chip pairs with scores for analyst triage.",
      status: "Demo flow"
    },
    {
      step: "05",
      title: "Route to field survey or fast close",
      endpoint: "claims API",
      body: "High-score changed chips trigger survey assignment; stable chips support low-risk auto-close or lower-priority review in the insurer core system.",
      status: "Product path"
    }
  ],
  samWorkflow: [
    { step: "01", title: "Clip same-area high-res imagery", body: "Prepare a georeferenced high-resolution chip for one village/block AOI and preserve CRS, acquisition date, native GSD, and provider attribution." },
    { step: "02", title: "Prompt SAM / SamGeo", body: "Use point or box prompts over visible field edges to produce candidate masks. SAM is an annotation accelerator, not the crop classifier." },
    { step: "03", title: "Vectorize and QC boundaries", body: "Convert masks to GeoJSON/GPKG, simplify topology, remove slivers, repair overlaps, and send uncertain edges for human review." },
    { step: "04", title: "Attach temporal ML state", body: "Join approved parcel boundaries to Sentinel-2 temporal features, then publish crop, confidence, stress, NDVI/EVI, and production estimates." }
  ],
  samBoundaryDemo: {
    label: "Field detection",
    headline: "Detect field boundaries from the imagery, then save the ones you want.",
    body: "Tap Detect fields to outline every field in view, review the candidates, and save the ones that matter. Crop type and risk are added when you run analysis.",
    stages: [
      {
        id: "chip",
        step: "01",
        title: "Georeferenced chip",
        output: "Input",
        body: "Clip a village AOI from procured high-resolution imagery or the current same-area visual basemap. Keep CRS, bounds, date, source, and display rights with the chip.",
        tags: ["High-res image", "CRS retained", "Source metadata"]
      },
      {
        id: "prompt",
        step: "02",
        title: "Prompted masks",
        output: "SAM/SamGeo",
        body: "An operator places points or boxes around visible field parcels. SAM/SamGeo returns candidate masks that speed up digitization but do not decide crop type.",
        tags: ["Point prompts", "Box prompts", "Candidate masks"]
      },
      {
        id: "qc",
        step: "03",
        title: "Human QC",
        output: "Boundary approval",
        body: "Reviewers simplify geometry, remove slivers, repair overlaps, and mark low-certainty edges for field validation or cadastral comparison.",
        tags: ["Topology repair", "Sliver removal", "QC flags"]
      },
      {
        id: "publish",
        step: "04",
        title: "Publish parcels",
        output: "GeoJSON/GPKG",
        body: "Approved boundaries are exported as GIS layers and joined to temporal ML outputs: crop, confidence, stress, NDVI/EVI, acreage, yield, and production.",
        tags: ["GeoJSON", "GPKG", "ML join key"]
      }
    ],
    proof: [
      { label: "Role", value: "Annotation acceleration", note: "Speeds parcel boundary creation from imagery; it is not used to infer crop class." },
      { label: "Output", value: "Candidate polygon layer", note: "Demo overlay shows candidate boundaries ready for topology cleanup and QC." },
      { label: "Control", value: "Human approval required", note: "Accepted boundaries are audited before WebGIS publication or ML attachment." },
      { label: "Next join", value: "Temporal ML state", note: "Crop, stress, NDVI/EVI, and production estimates remain model outputs from temporal features." }
    ]
  },
  requirements: [
    {
      section: "12.1",
      title: "Brief scope and UPAHAR platform framing",
      pages: "22-25",
      summary: "Design, develop, integrate, operate, and maintain UPAHAR as a unified agriculture platform with documentation, data acquisition, decision support, advisory, and reporting services.",
      demoSurface: "Whole static dashboard and insurer-safe capability positioning",
      evidence: "The dashboard presents the platform shape while clearly labelling state-specific records and integrations as demo data.",
      evidenceType: "Demo positioning",
      status: "shown",
      sourceExcerpt: "Section 12.1 frames UPAHAR as an integrated platform covering applications, data, decision support, advisories, reports, DAC, operations, and maintenance."
    },
    {
      section: "12.2.1",
      title: "Satellite imagery source and specification",
      pages: "25-26",
      summary: "Use multi-date imagery for each season, including early, mid, peak, and late crop stages, with agricultural coverage and preprocessing discipline.",
      demoSurface: "Season epoch slider, Sentinel-2 temporal index positioning, LGND collection flow, and remote-sensing evidence cards",
      evidence: "The demo positions Sentinel-2 as the insurer-grade temporal analytic source and keeps the visible basemap labelled as a fallback until Sentinel-2 tiles are rendered locally.",
      evidenceType: "Shown imagery workflow",
      status: "shown",
      sourceExcerpt: "The RFP asks for four multi-date imagery sets per crop season across key growth stages, with preprocessing and coverage controls."
    },
    {
      section: "12.2.2",
      title: "Field survey for ground truth data collection",
      pages: "26-27",
      summary: "Collect stratified GT samples, validate quality, reserve independent holdout data, and integrate GT evidence into the Web-GIS platform.",
      demoSurface: "Ground truth markers, field validation feed, parcel evidence tab, and mobile upload flow",
      evidence: "GT points show status, GPS accuracy, validation holdout, officer attribution, and linked parcel drilldown.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP calls for 1-2% GT coverage, QC checks, geotagged evidence, and 30% GT reservation for independent accuracy assessment."
    },
    {
      section: "12.2.3",
      title: "Georeferencing of cadastral maps",
      pages: "27",
      summary: "Use cadastral vector data from the land-records authority and integrate parcel boundaries into the spatial workflow.",
      demoSurface: "Parcel-level map, boundary query, and Land Records / Bhuiyan integration card",
      evidence: "Demo parcel polygons are geospatially aligned to visible same-area imagery while the integration card labels official land-record linkage as planned.",
      evidenceType: "Aligned demo geometry",
      status: "mocked",
      sourceExcerpt: "The RFP expects use of geo-referenced cadastral maps from the official land-records authority in vector formats."
    },
    {
      section: "12.2.4",
      title: "Crop acreage and production monitoring",
      pages: "27",
      summary: "Continuously map cultivated areas and produce crop-wise acreage and production estimates for planning.",
      demoSurface: "Mapped acreage KPI, parcel acreage, production fields, and crop-wise report queue",
      evidence: "Parcel drilldown combines acreage, yield, and production while the report queue shows acreage outputs.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP emphasizes timely acreage information, crop-wise estimates, and summary reports for resource planning."
    },
    {
      section: "12.2.5",
      title: "Crop identification",
      pages: "27-28",
      summary: "Classify crops at parcel level using multi-date remote sensing, vegetation indices, GT validation, confidence scores, and GIS-compatible outputs.",
      demoSurface: "Crop classification layer, parcel crop labels, confidence metric, and parcel evidence",
      evidence: "The map colors parcels by crop and the selected parcel shows crop class, confidence, source layers, NDVI trend, and GT status.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP sets a parcel-level crop classification accuracy target, requires confidence scores, and calls for crop-wise maps and acreage estimates."
    },
    {
      section: "12.2.6",
      title: "Crop health monitoring",
      pages: "28-29",
      summary: "Track crop condition with multi-temporal imagery, vegetation indices, change detection, stress severity, alerts, and Web-GIS layers.",
      demoSurface: "Stress layer, stress KPI, parcel NDVI trend, risk cause, and crop health report queue",
      evidence: "Stress severity changes parcel colors and the parcel panel explains the detected stress cause and advisory path.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP asks for crop health maps, vegetation indices, stress categories, alerts, GT integration, and GIS-compatible outputs."
    },
    {
      section: "12.2.7",
      title: "Crop acreage estimation",
      pages: "29-30",
      summary: "Generate continuous crop-wise acreage estimates across village, block, district, and seasonal reporting levels.",
      demoSurface: "Acreage KPI, acreage/yield layer, parcel acreage, and acreage export queue",
      evidence: "The demo shows district-level acreage KPI, parcel-level acreage, and export formats such as CSV, GeoJSON, and GeoTIFF.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP asks for continuous acreage estimation, change detection, village-wise maps, summaries, heatmaps, and GIS deliverables."
    },
    {
      section: "12.2.8",
      title: "Crop yield modeling and production estimation",
      pages: "30-31",
      summary: "Combine acreage, spectral trends, weather, soil, and agronomic signals to estimate yield and production before and after harvest.",
      demoSurface: "Yield forecast KPI, yield layer, parcel production calculation, and yield report queue",
      evidence: "Parcel details expose yield and production while the yield metric and report queue show forecast and reporting readiness.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP expects yield models using spectral, weather, soil, and agronomic inputs with forecast and final yield reports."
    },
    {
      section: "12.2.9",
      title: "Claim and portfolio planning",
      pages: "31",
      summary: "Use crop acreage, stress, and production estimates to support insurer claim triage and branch workload planning.",
      demoSurface: "Exposure and claim load panel with service-center map markers",
      evidence: "The claim panel turns insured acreage and stress into claim desk load, exposure, open claim packets, and center-level risk.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The source RFP connects remote-sensing crop estimates to operational planning; this insurer version maps the same evidence pattern to claim workload."
    },
    {
      section: "12.2.10",
      title: "Drought and dry spell monitoring",
      pages: "31",
      summary: "Monitor dry spells and drought-like stress signals using crop health, moisture, and anomaly indicators.",
      demoSurface: "Stress-risk layer, severe fallow/failed crop parcel, and event-driven report queue",
      evidence: "High and severe stress parcels carry moisture and risk-cause narratives suitable for field inspection and dry-spell review.",
      evidenceType: "Mocked event scenario",
      status: "mocked",
      sourceExcerpt: "The RFP includes drought and dry-spell monitoring as part of satellite-based agriculture assessment."
    },
    {
      section: "12.3",
      title: "Drone-satellite disaster monitoring and crop loss",
      pages: "31-32",
      summary: "Support flood, waterlogging, and crop-loss assessment with remote sensing and field validation when required.",
      demoSurface: "Waterlogging parcel, crop-loss advisory, field evidence feed, and event-driven disaster report",
      evidence: "The demo flags flood-waterlogging and failed/unsown signatures, then routes them to validation and event reports.",
      evidenceType: "Mocked event scenario",
      status: "mocked",
      sourceExcerpt: "Section 12.3 covers hybrid disaster monitoring, including flood mapping and crop-loss assessment when required."
    },
    {
      section: "12.4",
      title: "Advisories",
      pages: "32-35",
      summary: "Generate advisories for departments, extension functionaries, and farmers, connected to crop condition and allied services.",
      demoSurface: "Parcel advisory tab and advisory KPI",
      evidence: "The selected parcel can generate department, extension, and farmer advisory variants from the same evidence record.",
      evidenceType: "Interactive demo",
      status: "shown",
      sourceExcerpt: "The RFP separates advisory audiences across department, extension functionaries, and farmers and links advisories to crop conditions."
    },
    {
      section: "12.5",
      title: "Claims workflow module",
      pages: "35-36",
      summary: "Provide a unified interface for farmer policy lookup, claim evidence, survey assignment, and payout workflow status.",
      demoSurface: "Exposure and claim load panel plus mobile claim evidence narrative",
      evidence: "The demo shows claim-center load and open claim packets with planned insurer-core integration.",
      evidenceType: "Mocked operational workflow",
      status: "mocked",
      sourceExcerpt: "Section 12.5 describes an operational module pattern; this insurer dashboard reuses that pattern for crop-insurance claims."
    },
    {
      section: "12.7",
      title: "Data Analytics Center setup",
      pages: "37-39",
      summary: "Establish the DAC command and control capability, including facilities, monitoring posture, and decision-support operations.",
      demoSurface: "Map-first command dashboard, KPI strip, reviewer mode, and reporting surfaces",
      evidence: "The current UI is a command dashboard that combines map, KPIs, evidence, reports, and integration readiness in one review surface.",
      evidenceType: "Shown product shape",
      status: "shown",
      sourceExcerpt: "Section 12.7 establishes the DAC command and control unit and its operational facilities."
    },
    {
      section: "12.8",
      title: "DAC, Web-GIS, digital web platform, and mobile platform",
      pages: "39-45",
      summary: "Deliver DAC functions, geospatial infrastructure, Web-GIS portal, performant map rendering, digital platform, and mobile platform.",
      demoSurface: "Layer stack, Web-GIS viewer, standards tags, mobile flow, and integration panels",
      evidence: "The static app demonstrates the Web-GIS interaction model, OGC layer labels, mobile field flow, and platform navigation.",
      evidenceType: "Shown product shape",
      status: "shown",
      sourceExcerpt: "Section 12.8 covers DAC functional requirements, GIS services, Web-GIS integration, map performance, web platform, and mobile platform."
    },
    {
      section: "12.8.7",
      title: "Mobile platform",
      pages: "43-45",
      summary: "Support mobile field workflows including offline field use, evidence capture, synchronization, and field officer/farmer interactions.",
      demoSurface: "Farmer and Field Officer Flow panel",
      evidence: "The mobile flow shows boundary capture, crop validation, evidence upload, sync to DAC, and advisory receipt.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP expects a mobile platform and mobile application for rural field workflows and synchronized data capture."
    },
    {
      section: "12.9",
      title: "Integrations",
      pages: "45-46",
      summary: "Integrate with satellite verification, Digital Crop Survey, Farmer Database/AgriStack, and future state or central systems.",
      demoSurface: "Integration Readiness cards",
      evidence: "Integration cards identify AgriStack, land records, soil, weather, insurer-core claims, LGND, and disaster systems as planned APIs.",
      evidenceType: "Planned integration map",
      status: "planned",
      sourceExcerpt: "Section 12.9 requires APIs and future integration support for relevant government and allied systems."
    },
    {
      section: "12.13",
      title: "Standards and interoperability",
      pages: "50-51",
      summary: "Use interoperable standards and open geospatial/data exchange interfaces across the system.",
      demoSurface: "Open Interfaces tags and layer service labels",
      evidence: "Layer controls label WMS, WFS, WCS, REST, GeoJSON, and GeoTIFF paths used by the demo surfaces.",
      evidenceType: "Shown architecture cue",
      status: "shown",
      sourceExcerpt: "Section 12.13 covers standards and interoperability expectations for the platform."
    },
    {
      section: "12.14",
      title: "API approach",
      pages: "51",
      summary: "Expose integration-ready APIs for platform interoperability and future system connections.",
      demoSurface: "Integration Readiness cards and REST API interface labels",
      evidence: "The demo labels external system touchpoints as planned APIs without claiming live connectivity.",
      evidenceType: "Planned integration map",
      status: "planned",
      sourceExcerpt: "Section 12.14 covers the API approach needed for integration and interoperability."
    },
    {
      section: "12.15/12.19",
      title: "Testing, security, and performance testing",
      pages: "53-59",
      summary: "Plan unit, performance, UAT, security, audit, and performance testing for the full platform.",
      demoSurface: "Evidence cards, validation holdout labels, export actions, and audit-ready workflow labels",
      evidence: "The demo shows validation discipline and audit posture but does not implement production security or performance testing.",
      evidenceType: "Planned delivery control",
      status: "planned",
      sourceExcerpt: "The RFP includes unit, load, UAT, security, audit, and performance testing expectations."
    },
    {
      section: "12.20/12.22",
      title: "Change management, capacity building, and training",
      pages: "59-60",
      summary: "Support adoption through change management, stakeholder training, and handholding.",
      demoSurface: "Reviewer mode and mobile workflow narrative",
      evidence: "The guided checklist doubles as a training walkthrough for tender reviewers and future operating users.",
      evidenceType: "Planned adoption support",
      status: "planned",
      sourceExcerpt: "The RFP covers change management, training, handholding, and capacity-building obligations."
    },
    {
      section: "12.23/12.24",
      title: "Operation, maintenance, and exit management",
      pages: "60-61",
      summary: "Operate and maintain the integrated system, then support structured exit and handover.",
      demoSurface: "Coverage matrix, report queue, and insurer-safe delivery posture",
      evidence: "The matrix identifies what is shown, mocked, or planned so delivery and handover gaps are explicit.",
      evidenceType: "Planned delivery control",
      status: "planned",
      sourceExcerpt: "The RFP includes four-year operation and maintenance plus exit management and project handover duties."
    },
    {
      section: "12.27",
      title: "Summary reports of deliverables",
      pages: "64-67",
      summary: "Submit web/mobile deliverables and remote-sensing data-processing reports within defined reporting timelines.",
      demoSurface: "Operational Report Queue and export controls",
      evidence: "The report queue lists acreage, yield, crop health, disaster, and advisory outputs with cadence and formats.",
      evidenceType: "Shown deliverable map",
      status: "shown",
      sourceExcerpt: "Section 12.27 summarizes deliverables for web/mobile application work and remote-sensing data-processing reports."
    }
  ],
  surfaceRequirements: {
    topbar: ["12.1", "12.7"],
    reviewer: ["12.1", "12.7", "12.8"],
    layers: ["12.8", "12.13"],
    epoch: ["12.2.1"],
    standards: ["12.13", "12.14"],
    map: ["12.2.5", "12.2.6", "12.8"],
    metrics: ["12.2.4", "12.2.5", "12.2.6", "12.2.8"],
    parcel: ["12.2.5", "12.2.6", "12.2.7", "12.2.8"],
    advisory: ["12.4"],
    field: ["12.2.2", "12.8.7"],
    procurement: ["12.2.9", "12.5"],
    evidence: ["12.1", "12.2.5", "12.15/12.19"],
    ml: ["12.2.1", "12.2.5", "12.2.6", "12.2.8", "12.15/12.19"],
    lgnd: ["12.2.1", "12.2.6", "12.3", "12.14"],
    sam: ["12.2.3", "12.8", "12.13"],
    coverage: ["12.1", "12.23/12.24"],
    reports: ["12.27"],
    mobile: ["12.8.7"],
    integrations: ["12.9", "12.14"]
  },
  reviewerSteps: [
    {
      id: "imagery",
      step: "01",
      title: "Sentinel-2 to crop-risk map",
      body: "Use the epoch control and crop layer to show 5-day Sentinel-2 season imagery turning into the parcel risk map.",
      target: "mapStage",
      requirements: ["12.2.1", "12.2.5", "12.8"],
      epochIndex: 2,
      panel: "parcel",
      parcelId: "MP-NAR-001",
      layers: { crop: true, stress: false, yield: false, lgnd: false, sam: false, gt: false, procurement: false }
    },
    {
      id: "lgnd-scan",
      step: "02",
      title: "LGND change discovery",
      body: "Show how a Sentinel-2 AOI collection becomes a changed-chip search lane for claim triage.",
      target: "lgndPanel",
      requirements: ["12.2.1", "12.3", "12.14"],
      epochIndex: 2,
      panel: "parcel",
      parcelId: "MP-NAR-002",
      layers: { crop: false, stress: true, yield: false, lgnd: true, sam: false, gt: false, procurement: false }
    },
    {
      id: "confidence",
      step: "03",
      title: "Parcel crop confidence",
      body: "Inspect a selected parcel for crop class, acreage, confidence, source layers, and NDVI trend.",
      target: "detailPanel",
      requirements: ["12.2.5", "12.2.7"],
      panel: "parcel",
      parcelId: "MP-NAR-001",
      layers: { crop: true, stress: false, yield: true, lgnd: false, sam: false, gt: true, procurement: false }
    },
    {
      id: "health",
      step: "04",
      title: "Stress and evidence",
      body: "Switch to the stress layer and inspect a waterlogged parcel with its validation evidence.",
      target: "detailPanel",
      requirements: ["12.2.2", "12.2.6", "12.2.10", "12.3"],
      panel: "field",
      parcelId: "MP-NAR-006",
      layers: { crop: false, stress: true, yield: false, lgnd: false, sam: false, gt: true, procurement: false }
    },
    {
      id: "advisory",
      step: "05",
      title: "Advisory generation",
      body: "Use the advisory tab to show department, extension, and farmer messages from the same parcel evidence.",
      target: "detailPanel",
      requirements: ["12.4"],
      panel: "advisory",
      parcelId: "MP-NAR-006",
      layers: { crop: false, stress: true, yield: false, lgnd: false, sam: false, gt: true, procurement: false }
    },
    {
      id: "claims",
      step: "06",
      title: "Claim workload planning",
      body: "Show insured crop area, exposure, open claims, and claim desk load as claim-planning evidence.",
      target: "procurementPanel",
      requirements: ["12.2.9", "12.5"],
      panel: "parcel",
      parcelId: "MP-NAR-004",
      layers: { crop: true, stress: false, yield: true, lgnd: false, sam: false, gt: false, procurement: true }
    }
  ]
};

if (typeof window !== "undefined") {
  window.UPAHAR_DEMO_DATA = UPAHAR_DEMO_DATA;
}

if (typeof module !== "undefined") {
  module.exports = UPAHAR_DEMO_DATA;
}
