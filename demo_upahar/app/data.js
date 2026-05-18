const UPAHAR_DEMO_DATA = {
  basemap: {
    provider: "Esri World Imagery Wayback",
    service: "WMTS",
    aoi: "Chhattisgarh demo AOI: Raipur-Tilda-Arang agriculture corridor",
    attribution: "Imagery: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
    sourceUrl: "https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/mapping/use-world-imagery-wayback/",
    tileUrl: "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/GoogleMapsCompatible/MapServer/tile/{tileSet}/{z}/{y}/{x}",
    zoom: 16,
    tileSize: 256,
    displayMetersPerPixel: 2.23,
    center: { lat: 21.32, lon: 81.81 },
    rfpSpatialRequirement: "<=3 m optical imagery",
    rfpTemporalRequirement: "5-7 day optical cadence with four crop-stage dates per season",
    rfpBandRequirement: "Blue, Green, Red, NIR minimum; SAR fallback in cloudy periods",
    complianceNote: "This demo uses real same-area Wayback imagery at <=3 m display scale. Final tender compliance still requires procured source metadata for acquisition date, native GSD, spectral bands, and cadence."
  },
  epochs: [
    { label: "Early season", date: "2025-06-26", tileSet: "48925", note: "Sowing emergence and first crop signature separation" },
    { label: "Mid season", date: "2025-07-31", tileSet: "49999", note: "Canopy development, moisture stress, and acreage stabilization" },
    { label: "Peak season", date: "2025-09-04", tileSet: "52304", note: "Maximum vegetation signal and procurement planning baseline" },
    { label: "Late season", date: "2025-10-23", tileSet: "20512", note: "Harvest readiness, yield finalization, and loss assessment" }
  ],
  layers: [
    { id: "crop", label: "Crop classification", kind: "polygon", active: true, service: "WMS/WFS", requirements: ["12.2.5", "12.2.7"] },
    { id: "stress", label: "Crop health and stress", kind: "polygon", active: true, service: "WMS", requirements: ["12.2.6", "12.2.10", "12.3"] },
    { id: "yield", label: "Acreage and yield intensity", kind: "polygon", active: false, service: "WCS", requirements: ["12.2.7", "12.2.8"] },
    { id: "sam", label: "SAM boundary candidates", kind: "polygon", active: false, service: "GeoJSON/GPKG", requirements: ["12.2.3", "12.8"] },
    { id: "gt", label: "Ground truth validation", kind: "point", active: true, service: "WFS", requirements: ["12.2.2"] },
    { id: "procurement", label: "Procurement centers", kind: "point", active: true, service: "REST", requirements: ["12.2.9", "12.5"] }
  ],
  metrics: [
    { id: "acreage", label: "Mapped acreage", value: "64.8L ha", detail: "Kharif, Rabi, and summer coverage model", trend: "+6.4%", requirements: ["12.2.4", "12.2.7"] },
    { id: "confidence", label: "Crop ID confidence", value: "87.4%", detail: "Demo target aligned to 85% RFP threshold", trend: ">=85%", requirements: ["12.2.5"] },
    { id: "stress", label: "Stress alerts", value: "142", detail: "Moisture, pest, drought, and delayed sowing", trend: "31 high", requirements: ["12.2.6", "12.2.10", "12.3"] },
    { id: "yield", label: "Yield forecast", value: "5.2 Mt", detail: "Acreage plus vegetation and weather signal", trend: "-3.1%", requirements: ["12.2.8"] },
    { id: "gt", label: "GT coverage", value: "1.6%", detail: "Stratified sample of sown area", trend: "30% holdout", requirements: ["12.2.2"] },
    { id: "advisories", label: "Advisories", value: "18.4K", detail: "Department, extension, and farmer messages", trend: "weekly", requirements: ["12.4"] }
  ],
  crops: {
    Paddy: { color: "#3f8f57", short: "PD" },
    Maize: { color: "#c9a227", short: "MZ" },
    Pulses: { color: "#9a6cc2", short: "PL" },
    Fallow: { color: "#9ca3af", short: "FL" },
    Vegetables: { color: "#2f8ca3", short: "VG" }
  },
  stressColors: {
    Low: "#4f9d69",
    Moderate: "#d1a533",
    High: "#c55a4a",
    Severe: "#8f2f38"
  },
  parcels: [
    {
      id: "KH-RAI-001",
      village: "Bhatapara",
      crop: "Paddy",
      acreage: 42.6,
      confidence: 91,
      stress: "Low",
      stressScore: 18,
      yield: 4.4,
      production: 187.4,
      stage: "Panicle initiation",
      sowingWindow: "12-20 Jun",
      harvestWindow: "20-30 Oct",
      moisture: "Adequate",
      riskCause: "Normal canopy trajectory",
      validation: "GT-1042",
      advisory: "Maintain current irrigation interval; monitor late-season leaf folder risk.",
      ndvi: [0.28, 0.48, 0.71, 0.62],
      geometry: [
        [81.8000866, 21.3201399],
        [81.801653, 21.3202599],
        [81.8022323, 21.3192004],
        [81.8019748, 21.318121],
        [81.800344, 21.318101],
        [81.7994428, 21.3190205]
      ],
      epochStates: [
        { cropClass: "Fallow", confidence: 64, stress: "Low", stressScore: 18, ndvi: 0.28, evi: 0.18, stateNote: "Bare/wet preparation signal before stable paddy emergence" },
        { cropClass: "Paddy", confidence: 82, stress: "Low", stressScore: 20, ndvi: 0.48, evi: 0.32, stateNote: "Phenology curve separates paddy from fallow and maize" },
        { cropClass: "Paddy", confidence: 91, stress: "Low", stressScore: 18, ndvi: 0.71, evi: 0.49, stateNote: "Peak vegetation confirms high-confidence paddy extent" },
        { cropClass: "Paddy", confidence: 90, stress: "Low", stressScore: 21, ndvi: 0.62, evi: 0.42, stateNote: "Late-season decline remains inside normal harvest trajectory" }
      ]
    },
    {
      id: "KH-RAI-002",
      village: "Bhatapara",
      crop: "Maize",
      acreage: 31.8,
      confidence: 84,
      stress: "Moderate",
      stressScore: 47,
      yield: 3.1,
      production: 98.6,
      stage: "Vegetative",
      sowingWindow: "18-26 Jun",
      harvestWindow: "08-18 Oct",
      moisture: "Declining",
      riskCause: "Mid-season moisture and nitrogen signal",
      validation: "GT-1088",
      advisory: "Schedule field inspection for water stress and nutrient deficiency confirmation.",
      ndvi: [0.22, 0.42, 0.58, 0.46],
      geometry: [
        [81.8031765, 21.31998],
        [81.8053222, 21.32002],
        [81.805966, 21.3190205],
        [81.8054295, 21.3179211],
        [81.8033481, 21.318081],
        [81.80264, 21.3191405]
      ],
      epochStates: [
        { cropClass: "Fallow", confidence: 58, stress: "Low", stressScore: 16, ndvi: 0.22, evi: 0.14, stateNote: "Early season signal is ambiguous before maize canopy closure" },
        { cropClass: "Maize", confidence: 75, stress: "Moderate", stressScore: 41, ndvi: 0.42, evi: 0.27, stateNote: "Mid-season spectral rise supports maize with moisture caution" },
        { cropClass: "Maize", confidence: 84, stress: "Moderate", stressScore: 47, ndvi: 0.58, evi: 0.37, stateNote: "Classifier stabilizes on maize but stress remains above watch threshold" },
        { cropClass: "Maize", confidence: 81, stress: "Moderate", stressScore: 52, ndvi: 0.46, evi: 0.29, stateNote: "Late-season decline indicates harvest approach and water stress" }
      ]
    },
    {
      id: "KH-RAI-003",
      village: "Tilda",
      crop: "Pulses",
      acreage: 26.4,
      confidence: 78,
      stress: "High",
      stressScore: 72,
      yield: 1.2,
      production: 31.7,
      stage: "Flowering",
      sowingWindow: "25 Jun-05 Jul",
      harvestWindow: "25 Sep-05 Oct",
      moisture: "Low",
      riskCause: "Spectral deviation and pest-risk cluster",
      validation: "GT-1121",
      advisory: "Issue pest scouting advisory; spectral deviation indicates possible infestation.",
      ndvi: [0.19, 0.34, 0.41, 0.27],
      geometry: [
        [81.8075967, 21.3203398],
        [81.8098069, 21.3203798],
        [81.8102575, 21.3189406],
        [81.8093563, 21.3177012],
        [81.8073392, 21.318181],
        [81.8069959, 21.3194603]
      ],
      epochStates: [
        { cropClass: "Fallow", confidence: 55, stress: "Low", stressScore: 12, ndvi: 0.19, evi: 0.12, stateNote: "Weak early greenness before pulses become separable" },
        { cropClass: "Pulses", confidence: 68, stress: "Moderate", stressScore: 44, ndvi: 0.34, evi: 0.21, stateNote: "Pulses candidate appears, but spectral separation is incomplete" },
        { cropClass: "Pulses", confidence: 78, stress: "High", stressScore: 72, ndvi: 0.41, evi: 0.24, stateNote: "Peak-season curve underperforms expected vigor; pest scouting required" },
        { cropClass: "Pulses", confidence: 73, stress: "High", stressScore: 78, ndvi: 0.27, evi: 0.16, stateNote: "Late drop supports crop stress or damage assessment workflow" }
      ]
    },
    {
      id: "KH-RAI-004",
      village: "Tilda",
      crop: "Paddy",
      acreage: 55.1,
      confidence: 94,
      stress: "Low",
      stressScore: 12,
      yield: 4.8,
      production: 264.5,
      stage: "Grain filling",
      sowingWindow: "10-18 Jun",
      harvestWindow: "22 Oct-02 Nov",
      moisture: "Adequate",
      riskCause: "High confidence paddy extent",
      validation: "Model-only",
      advisory: "Expected strong procurement availability; align token capacity before harvest.",
      ndvi: [0.31, 0.55, 0.76, 0.68],
      geometry: [
        [81.8101717, 21.31998],
        [81.8119741, 21.3201999],
        [81.8125749, 21.3187407],
        [81.8116737, 21.3170815],
        [81.8098713, 21.3174214],
        [81.8093134, 21.3189406]
      ],
      epochStates: [
        { cropClass: "Paddy", confidence: 70, stress: "Low", stressScore: 16, ndvi: 0.31, evi: 0.2, stateNote: "Early paddy signature appears after field wetting" },
        { cropClass: "Paddy", confidence: 88, stress: "Low", stressScore: 13, ndvi: 0.55, evi: 0.36, stateNote: "Canopy expansion confirms paddy extent for acreage rollup" },
        { cropClass: "Paddy", confidence: 94, stress: "Low", stressScore: 12, ndvi: 0.76, evi: 0.52, stateNote: "Strong peak-season paddy signal supports procurement forecast" },
        { cropClass: "Paddy", confidence: 93, stress: "Low", stressScore: 15, ndvi: 0.68, evi: 0.46, stateNote: "Late-season stability maintains paddy supply estimate" }
      ]
    },
    {
      id: "KH-RAI-005",
      village: "Arang",
      crop: "Vegetables",
      acreage: 18.7,
      confidence: 82,
      stress: "Moderate",
      stressScore: 54,
      yield: 8.3,
      production: 155.2,
      stage: "Harvest window",
      sowingWindow: "Staggered",
      harvestWindow: "Rolling",
      moisture: "Variable",
      riskCause: "Localized irrigation variability",
      validation: "Model-only",
      advisory: "Personalized irrigation advisory recommended from soil moisture estimate.",
      ndvi: [0.27, 0.46, 0.62, 0.49],
      geometry: [
        [81.8123603, 21.3239578],
        [81.8143559, 21.3241177],
        [81.8149138, 21.3225786],
        [81.8141199, 21.3211394],
        [81.8121029, 21.3213792],
        [81.811502, 21.3228584]
      ],
      epochStates: [
        { cropClass: "Vegetables", confidence: 63, stress: "Low", stressScore: 22, ndvi: 0.27, evi: 0.17, stateNote: "Small-field mixed crop signal appears earlier than cereal fields" },
        { cropClass: "Vegetables", confidence: 76, stress: "Moderate", stressScore: 42, ndvi: 0.46, evi: 0.31, stateNote: "Staggered growth pattern suggests vegetable block, not single cereal crop" },
        { cropClass: "Vegetables", confidence: 82, stress: "Moderate", stressScore: 54, ndvi: 0.62, evi: 0.4, stateNote: "Localized irrigation variability drives advisory generation" },
        { cropClass: "Vegetables", confidence: 79, stress: "Moderate", stressScore: 58, ndvi: 0.49, evi: 0.32, stateNote: "Rolling harvest keeps class stable with variable moisture" }
      ]
    },
    {
      id: "KH-RAI-006",
      village: "Arang",
      crop: "Paddy",
      acreage: 48.9,
      confidence: 89,
      stress: "High",
      stressScore: 69,
      yield: 3.7,
      production: 180.9,
      stage: "Tillering",
      sowingWindow: "16-24 Jun",
      harvestWindow: "26 Oct-05 Nov",
      moisture: "Waterlogged",
      riskCause: "Flood-waterlogging anomaly",
      validation: "GT-1190",
      advisory: "Flood-waterlogging anomaly detected; prioritize ground validation.",
      ndvi: [0.29, 0.52, 0.64, 0.38],
      geometry: [
        [81.8144847, 21.3200999],
        [81.8165231, 21.31998],
        [81.8170596, 21.3184009],
        [81.8159009, 21.3169616],
        [81.814034, 21.3175613],
        [81.8135834, 21.3191005]
      ],
      epochStates: [
        { cropClass: "Paddy", confidence: 67, stress: "Low", stressScore: 18, ndvi: 0.29, evi: 0.19, stateNote: "Early wet field pattern consistent with paddy establishment" },
        { cropClass: "Paddy", confidence: 86, stress: "Moderate", stressScore: 38, ndvi: 0.52, evi: 0.34, stateNote: "Mid-season paddy class stabilizes; moisture anomaly begins" },
        { cropClass: "Paddy", confidence: 89, stress: "High", stressScore: 69, ndvi: 0.64, evi: 0.39, stateNote: "Waterlogging anomaly triggers disaster and GT validation path" },
        { cropClass: "Paddy", confidence: 76, stress: "High", stressScore: 74, ndvi: 0.38, evi: 0.22, stateNote: "Late NDVI drop supports crop-loss assessment workflow" }
      ]
    },
    {
      id: "KH-RAI-007",
      village: "Abhanpur",
      crop: "Maize",
      acreage: 34.2,
      confidence: 86,
      stress: "Low",
      stressScore: 22,
      yield: 3.4,
      production: 116.3,
      stage: "Cob formation",
      sowingWindow: "20-28 Jun",
      harvestWindow: "12-20 Oct",
      moisture: "Adequate",
      riskCause: "Stable phenology curve",
      validation: "Model-only",
      advisory: "Normal crop growth; next advisory at late-season harvest window.",
      ndvi: [0.24, 0.43, 0.61, 0.55],
      geometry: [
        [81.816609, 21.3219389],
        [81.8184114, 21.321799],
        [81.818862, 21.3201799],
        [81.8175746, 21.3189206],
        [81.8160296, 21.3196402],
        [81.8157507, 21.3210994]
      ],
      epochStates: [
        { cropClass: "Fallow", confidence: 60, stress: "Low", stressScore: 16, ndvi: 0.24, evi: 0.15, stateNote: "Early vegetation is too weak for confident crop assignment" },
        { cropClass: "Maize", confidence: 77, stress: "Low", stressScore: 21, ndvi: 0.43, evi: 0.28, stateNote: "Maize class emerges from temporal texture and canopy rise" },
        { cropClass: "Maize", confidence: 86, stress: "Low", stressScore: 22, ndvi: 0.61, evi: 0.39, stateNote: "Peak-season profile confirms maize with healthy canopy" },
        { cropClass: "Maize", confidence: 84, stress: "Low", stressScore: 24, ndvi: 0.55, evi: 0.34, stateNote: "Late-season signal remains consistent with harvest readiness" }
      ]
    },
    {
      id: "KH-RAI-008",
      village: "Abhanpur",
      crop: "Fallow",
      acreage: 22.9,
      confidence: 88,
      stress: "Severe",
      stressScore: 91,
      yield: 0.2,
      production: 4.6,
      stage: "Unsown/failed",
      sowingWindow: "Missed",
      harvestWindow: "Not expected",
      moisture: "Severe deficit",
      riskCause: "Failed crop or unsown fallow signature",
      validation: "GT-1233",
      advisory: "Likely failed or unsown patch; flag for compensation and farmer verification.",
      ndvi: [0.16, 0.18, 0.22, 0.19],
      geometry: [
        [81.818111, 21.3246574],
        [81.8203855, 21.3244975],
        [81.8206215, 21.3225786],
        [81.8194414, 21.3214592],
        [81.8176175, 21.3219789],
        [81.8172098, 21.323618]
      ],
      epochStates: [
        { cropClass: "Fallow", confidence: 72, stress: "Moderate", stressScore: 42, ndvi: 0.16, evi: 0.09, stateNote: "Low greenness suggests unsown or delayed sowing condition" },
        { cropClass: "Fallow", confidence: 81, stress: "High", stressScore: 68, ndvi: 0.18, evi: 0.1, stateNote: "No expected canopy rise; dry-spell flag is raised" },
        { cropClass: "Fallow", confidence: 88, stress: "Severe", stressScore: 91, ndvi: 0.22, evi: 0.12, stateNote: "Persistent low vegetation supports failed/unsown classification" },
        { cropClass: "Fallow", confidence: 90, stress: "Severe", stressScore: 88, ndvi: 0.19, evi: 0.1, stateNote: "Late-season persistence routes parcel to compensation verification" }
      ]
    }
  ],
  groundTruth: [
    { id: "GT-1042", lon: 81.8011165, lat: 21.3191804, crop: "Paddy", status: "Validated", split: "Training", gps: "1.8 m", officer: "VAA Raipur-04" },
    { id: "GT-1088", lon: 81.804421, lat: 21.3190605, crop: "Maize", status: "Validated", split: "Validation holdout", gps: "2.1 m", officer: "VAA Tilda-02" },
    { id: "GT-1121", lon: 81.8087555, lat: 21.3190605, crop: "Pulses", status: "QC review", split: "Validation holdout", gps: "2.7 m", officer: "VAA Tilda-07" },
    { id: "GT-1190", lon: 81.8109871, lat: 21.3186607, crop: "Paddy", status: "Pending revisit", split: "Training", gps: "3.4 m", officer: "VAA Arang-03" },
    { id: "GT-1233", lon: 81.8151498, lat: 21.3186207, crop: "Fallow", status: "Validated", split: "Validation holdout", gps: "1.5 m", officer: "VAA Abhanpur-01" }
  ],
  procurementCenters: [
    { id: "PC-RAI-12", name: "Bhatapara PACS", lon: 81.8040133, lat: 21.3219589, load: 82, arrivals: "18.2K q", tokens: 1260, risk: "High", status: "High demand" },
    { id: "PC-TIL-04", name: "Tilda Procurement Yard", lon: 81.8126822, lat: 21.3202199, load: 64, arrivals: "12.7K q", tokens: 870, risk: "Normal", status: "Normal" },
    { id: "PC-ABH-08", name: "Abhanpur Society", lon: 81.8176818, lat: 21.3188606, load: 91, arrivals: "21.5K q", tokens: 1520, risk: "High", status: "Add token slots" }
  ],
  advisoryTemplates: {
    department: "Prioritize {village} for {riskCause}. Current {crop} acreage is {acreage} ha with {confidence}% model confidence and {stress} stress. Schedule validation where confidence or stress risk requires intervention.",
    extension: "Visit parcel {id} during the current {stage} stage. Confirm crop condition, moisture status ({moisture}), and farmer-reported symptoms. Upload geo-tagged image evidence and close the QC loop.",
    farmer: "Your {crop} parcel is in {stage}. Current advisory: {advisory} Expected harvest window: {harvestWindow}. Keep field photos ready if an officer requests validation."
  },
  mobileFlow: [
    { step: "01", title: "Pin or walk parcel boundary", body: "Farmer or VAA captures GPS boundary, draws polygon on satellite basemap, or verifies cadastral import.", requirements: ["12.2.3", "12.8.7"] },
    { step: "02", title: "Validate crop and stage", body: "Mobile app compares farmer crop claim with satellite crop classification and NDVI/EVI trend.", requirements: ["12.2.2", "12.2.5", "12.8.7"] },
    { step: "03", title: "Upload field evidence", body: "Geo-tagged photos, short videos, notes, pest/disease observations, and damage records sync to DAC.", requirements: ["12.2.2", "12.3", "12.8.7"] },
    { step: "04", title: "Receive advisory", body: "Parcel-specific sowing, stress, irrigation, pest, weather, harvest, and disaster advisories are pushed back.", requirements: ["12.4", "12.8.7"] }
  ],
  integrations: [
    { name: "AgriStack / NFR", status: "Planned API", detail: "UFID, farmer registry, demographic sync", requirements: ["12.4", "12.9"] },
    { name: "Land Records / Bhuiyan", status: "Planned API", detail: "Khasra, parcel geometry, ownership link", requirements: ["12.2.3", "12.9"] },
    { name: "Soil Health Card", status: "Planned API", detail: "Soil parameters for nutrient advisory", requirements: ["12.4", "12.9"] },
    { name: "IMD / AWS Weather", status: "Planned API", detail: "Rainfall, temperature, humidity, wind", requirements: ["12.2.8", "12.4", "12.9"] },
    { name: "Food Dept / MARKFED", status: "Planned API", detail: "MSP, procurement center, arrivals", requirements: ["12.2.9", "12.5", "12.9"] },
    { name: "Disaster Systems", status: "Planned API", detail: "Flood, drought, crop loss, compensation", requirements: ["12.3", "12.9"] }
  ],
  reports: [
    { name: "Crop acreage estimation", cadence: "Two times per season", formats: "PDF, CSV, GeoJSON", status: "Ready", requirements: ["12.2.7", "12.27"] },
    { name: "Crop yield estimation", cadence: "Two times per season", formats: "PDF, XLSX", status: "Ready", requirements: ["12.2.8", "12.27"] },
    { name: "Crop stress and health", cadence: "Weekly", formats: "PDF, GeoTIFF", status: "Scheduled", requirements: ["12.2.6", "12.27"] },
    { name: "Drought / flood / crop loss", cadence: "Event occurrence", formats: "PDF, GeoJSON, GeoTIFF", status: "Event-driven", requirements: ["12.2.10", "12.3", "12.27"] },
    { name: "Pest and disease advisory", cadence: "Fortnight/event", formats: "PDF, CSV", status: "Scheduled", requirements: ["12.4", "12.27"] }
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
      title: "Tender-safe positioning",
      body: "Chhattisgarh parcels, procurement centers, and farmer records are demo data; AI4Agri artifacts are used as technical proof of capability.",
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
  samWorkflow: [
    { step: "01", title: "Clip same-area high-res imagery", body: "Prepare a georeferenced high-resolution chip for one village/block AOI and preserve CRS, acquisition date, native GSD, and provider attribution." },
    { step: "02", title: "Prompt SAM / SamGeo", body: "Use point or box prompts over visible field edges to produce candidate masks. SAM is an annotation accelerator, not the crop classifier." },
    { step: "03", title: "Vectorize and QC boundaries", body: "Convert masks to GeoJSON/GPKG, simplify topology, remove slivers, repair overlaps, and send uncertain edges for human review." },
    { step: "04", title: "Attach temporal ML state", body: "Join approved parcel boundaries to Sentinel-2 temporal features, then publish crop, confidence, stress, NDVI/EVI, and production estimates." }
  ],
  samBoundaryDemo: {
    label: "Boundary annotation accelerator",
    headline: "SAM/SamGeo produces candidate parcel boundaries; crop class comes later from temporal ML.",
    body: "For the demo, the cyan overlay represents SAM-assisted candidate boundaries over the same-area imagery. A human QC step approves geometry before crop identification, stress scoring, and production estimation are attached.",
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
      demoSurface: "Whole static dashboard and tender-safe capability positioning",
      evidence: "The dashboard presents the platform shape while clearly labelling state-specific records and integrations as demo data.",
      evidenceType: "Demo positioning",
      status: "shown",
      sourceExcerpt: "Section 12.1 frames UPAHAR as an integrated platform covering applications, data, decision support, advisories, reports, DAC, operations, and maintenance."
    },
    {
      section: "12.2.1",
      title: "Satellite imagery procurement and specification",
      pages: "25-26",
      summary: "Use multi-date imagery for each season, including early, mid, peak, and late crop stages, with agricultural coverage and preprocessing discipline.",
      demoSurface: "Season epoch slider, same-area Wayback imagery, Sentinel-2 temporal index positioning, and remote-sensing evidence cards",
      evidence: "The demo uses Chhattisgarh AOI imagery dates at a <=3 m display scale and explicitly separates Sentinel-2 temporal indices from final procured 3 m imagery compliance.",
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
      sourceExcerpt: "The RFP expects use of geo-referenced cadastral maps from DLR Chhattisgarh in vector formats."
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
      title: "Support for MSP procurement planning",
      pages: "31",
      summary: "Use paddy acreage and production estimates to support procurement planning and institutional load management.",
      demoSurface: "Paddy procurement load panel and procurement center map markers",
      evidence: "The procurement panel turns paddy acreage and production into PACS load, forecast supply, token capacity, and center-level risk.",
      evidenceType: "Shown workflow",
      status: "shown",
      sourceExcerpt: "The RFP connects remote-sensing crop estimates to MSP procurement planning and paddy availability assessment."
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
      title: "Paddy procurement module",
      pages: "35-36",
      summary: "Provide a unified interface for farmer onboarding, procurement tracking, society-level activities, and digital token workflows.",
      demoSurface: "Paddy procurement load panel and mobile digital-token narrative",
      evidence: "The demo shows procurement center load and token capacity with planned Food Department and MARKFED integration.",
      evidenceType: "Mocked operational workflow",
      status: "mocked",
      sourceExcerpt: "Section 12.5 describes the paddy procurement module, digital tokens, reports, and institutional support delivery tracking."
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
      evidence: "Integration cards identify AgriStack, land records, soil, weather, Food/MARKFED, and disaster systems as planned APIs.",
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
      demoSurface: "Coverage matrix, report queue, and tender-safe delivery posture",
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
      title: "Satellite imagery to crop map",
      body: "Use the epoch control and crop layer to show multi-date imagery turning into the parcel crop map.",
      target: "mapStage",
      requirements: ["12.2.1", "12.2.5", "12.8"],
      epochIndex: 2,
      panel: "parcel",
      parcelId: "KH-RAI-001",
      layers: { crop: true, stress: false, yield: false, sam: false, gt: false, procurement: false }
    },
    {
      id: "sam-boundaries",
      step: "02",
      title: "SAM-assisted boundaries",
      body: "Show SAM/SamGeo as a prompted boundary accelerator, followed by human QC before crop ML is attached.",
      target: "samPanel",
      requirements: ["12.2.3", "12.8", "12.13"],
      epochIndex: 2,
      panel: "parcel",
      parcelId: "KH-RAI-002",
      layers: { crop: false, stress: false, yield: false, sam: true, gt: false, procurement: false }
    },
    {
      id: "confidence",
      step: "03",
      title: "Parcel crop confidence",
      body: "Inspect a selected parcel for crop class, acreage, confidence, source layers, and NDVI trend.",
      target: "detailPanel",
      requirements: ["12.2.5", "12.2.7"],
      panel: "parcel",
      parcelId: "KH-RAI-001",
      layers: { crop: true, stress: false, yield: true, sam: false, gt: true, procurement: false }
    },
    {
      id: "health",
      step: "04",
      title: "Stress and evidence",
      body: "Switch to the stress layer and inspect a waterlogged parcel with its validation evidence.",
      target: "detailPanel",
      requirements: ["12.2.2", "12.2.6", "12.2.10", "12.3"],
      panel: "field",
      parcelId: "KH-RAI-006",
      layers: { crop: false, stress: true, yield: false, sam: false, gt: true, procurement: false }
    },
    {
      id: "advisory",
      step: "05",
      title: "Advisory generation",
      body: "Use the advisory tab to show department, extension, and farmer messages from the same parcel evidence.",
      target: "detailPanel",
      requirements: ["12.4"],
      panel: "advisory",
      parcelId: "KH-RAI-006",
      layers: { crop: false, stress: true, yield: false, sam: false, gt: true, procurement: false }
    },
    {
      id: "procurement",
      step: "06",
      title: "MSP procurement planning",
      body: "Show paddy area, forecast supply, token capacity, and PACS load as procurement planning evidence.",
      target: "procurementPanel",
      requirements: ["12.2.9", "12.5"],
      panel: "parcel",
      parcelId: "KH-RAI-004",
      layers: { crop: true, stress: false, yield: true, sam: false, gt: false, procurement: true }
    }
  ]
};

if (typeof window !== "undefined") {
  window.UPAHAR_DEMO_DATA = UPAHAR_DEMO_DATA;
}

if (typeof module !== "undefined") {
  module.exports = UPAHAR_DEMO_DATA;
}
