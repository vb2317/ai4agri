const apiBase = window.UPAHAR_API_BASE || "";
let data = window.UPAHAR_DEMO_DATA;
let state;
let cropLegend;
let requirementIndex;
const mapViewBox = { width: 1000, height: 606 };
const productTabs = [
  {
    id: "fields",
    eyebrow: "Step 01",
    title: "Fields",
    label: "Fields",
    body: "Detect field boundaries from the imagery, save them, then read crop and risk.",
    focus: ["Detect fields", "Save to portfolio", "Run analysis", "Crop & risk"],
    layers: { crop: true, stress: true, yield: false, lgnd: false, sam: true, gt: false, procurement: false },
    mapMode: "edit",
    target: "samPanel"
  },
  {
    id: "lgnd",
    eyebrow: "Step 02",
    title: "Similar Field Review",
    label: "Similar Field Review",
    body: "For a flagged field, pull up visually similar fields to confirm or dismiss the alert.",
    focus: ["Flagged field", "Similar fields", "Confirm or dismiss", "Faster review"],
    layers: { crop: false, stress: true, yield: false, lgnd: true, sam: false, gt: false, procurement: false },
    mapMode: "predict",
    target: "lgndPanel"
  }
];

function initializeState() {
  state = {
    activeProductTab: "fields",
    activeLayers: {
      ...Object.fromEntries(data.layers.map((layer) => [layer.id, false])),
      ...productTabs.find((tab) => tab.id === "fields").layers
    },
    epochIndex: Math.min(2, data.epochs.length - 1),
    selectedParcelId: data.parcels[0]?.id || null,
    selectedPanel: "parcel",
    mapMode: "predict",
    userParcels: [],
    nextUserParcelNumber: 1,
    selectedModel: "hgb-temporal",
    mlRunning: false,
    activeReviewerStep: data.reviewerSteps[0].id,
    activeSamStage: data.samBoundaryDemo?.stages?.[1]?.id || "prompt",
    samSourceParcelId: data.parcels[0]?.id || "AOI",
    samChipCenter: null,
    samDraftPoints: [],
    samTool: "point",
    samPrompts: [],
    samCandidateReady: false,
    samQcAccepted: false,
    samPublishedParcelId: null,
    samSuggestions: [],
    selectedSamMaskId: null,
    selectedSamMaskIds: [],
    samChipViewBox: { x: 0, y: 0, width: 640, height: 360 },
    samDrag: null,
    samBackendNote: "",
    samLoading: false,
    selectedRequirementId: null,
    highlightTimer: null,
    lgndStatus: { configured: false, checked: false },
    mlValidation: { available: false },
    mlPredictions: { available: false, predictions: [] },
    similar: { available: false, results: [] },
    similarDecisions: {},
    similarLoading: false
  };

  cropLegend = Object.entries(data.crops).map(([name, crop]) => ({
    label: name,
    color: crop.color
  }));

  requirementIndex = new Map(data.requirements.map((requirement) => [requirement.section, requirement]));
}

async function loadDemoData() {
  try {
    const response = await fetch(`${apiBase}/api/demo-data`, { cache: "no-store" });
    if (response.ok) {
      return response.json();
    }
  } catch {
    // Opening app/index.html directly still works by falling back to app/data.js.
  }
  return window.UPAHAR_DEMO_DATA;
}

async function loadLgndStatus() {
  const statusUrl = data.api?.lgndStatus || "/api/lgnd/status";
  try {
    const response = await fetch(`${apiBase}${statusUrl}`, { cache: "no-store" });
    if (response.ok) {
      return { ...(await response.json()), checked: true };
    }
  } catch {
    // Static file mode has no backend proxy, so LGND remains a documented integration flow.
  }
  return {
    configured: false,
    checked: true,
    envVar: "LGND_TOKEN",
    browserKeyExposure: "never",
    error: "Backend LGND proxy unavailable"
  };
}

async function loadMlArtifact(urlKey, fallbackUrl) {
  const url = data.api?.[urlKey] || fallbackUrl;
  try {
    const response = await fetch(`${apiBase}${url}`, { cache: "no-store" });
    if (response.ok) {
      return response.json();
    }
  } catch {
    // Static file mode has no backend; the ML card stays hidden.
  }
  return { available: false };
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function selectedParcel() {
  return (
    state.userParcels.find((item) => item.id === state.selectedParcelId) ||
    data.parcels.find((item) => item.id === state.selectedParcelId) ||
    state.userParcels[0] ||
    data.parcels[0]
  );
}

function parcelGt(parcel) {
  return data.groundTruth.find((point) => point.id === parcel.validation);
}

function parcelEpochState(parcel) {
  return parcel.epochStates?.[state.epochIndex] ?? {
    cropClass: parcel.crop,
    confidence: parcel.confidence,
    stress: parcel.stress,
    stressScore: parcel.stressScore,
    ndvi: parcel.ndvi[state.epochIndex],
    evi: Number((parcel.ndvi[state.epochIndex] * 0.68).toFixed(2)),
    stateNote: parcel.riskCause
  };
}

function requirementById(section) {
  return requirementIndex.get(section);
}

function uniqueRequirements(sections = []) {
  return [...new Set(sections)].filter((section) => requirementById(section));
}

function titleCase(value) {
  return value.slice(0, 1).toUpperCase() + value.slice(1);
}

function statusKey(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "-");
}

function productionEstimate(parcel) {
  return Number.isFinite(parcel.production) ? parcel.production : parcel.acreage * parcel.yield;
}

function modelOptions() {
  return [
    { id: "hgb-temporal", label: "Standard", detail: "Fast read of crop and stress across the season" },
    { id: "extratrees-phenology", label: "Robust", detail: "Steadier read for noisy or partly cloudy fields" },
    { id: "tinyvit-parcel", label: "Detailed", detail: "Closer look for fields under review" }
  ];
}

function polygonAreaHa(points) {
  const xs = points.map(([lon]) => lon);
  const ys = points.map(([, lat]) => lat);
  const widthM = (Math.max(...xs) - Math.min(...xs)) * 111320 * Math.cos((ys.reduce((a, b) => a + b, 0) / ys.length) * Math.PI / 180);
  const heightM = (Math.max(...ys) - Math.min(...ys)) * 111320;
  return Math.max(0.8, Math.abs(widthM * heightM) / 10000);
}

function createAnnotatedParcel(mask) {
  const source = selectedSamParcel();
  const id = `ANNO-${String(state.nextUserParcelNumber).padStart(3, "0")}`;
  // Prefer the backend-provided lon/lat geometry (correct for both prompted and
  // automatic masks); fall back to client conversion only for locally drawn shapes.
  const geometry = mask?.geometry || (mask?.chipPoints ? chipPointsToGeometry(mask.chipPoints, source) : source.geometry);
  const acreage = Number(polygonAreaHa(geometry).toFixed(1));
  return {
    id,
    village: source.village,
    crop: "Pending",
    acreage,
    confidence: 0,
    stress: "Low",
    stressScore: 0,
    yield: 0,
    production: 0,
    stage: "Pending ML",
    sowingWindow: "Pending",
    harvestWindow: "Pending",
    moisture: "Pending",
    riskCause: "Boundary saved; ML prediction not run",
    validation: "Model-only",
    advisory: "Run ML predictions to attach crop, stress, NDVI/EVI, yield, and production.",
    ndvi: [0, 0, 0, 0],
    geometry,
    annotation: {
      sourceParcelId: source.id,
      maskId: mask?.id || "manual-boundary",
      promptCount: state.samPrompts.length,
      status: "Boundary saved"
    }
  };
}

function samChipBounds(parcel) {
  const xs = parcel.geometry.map(([lon]) => lon);
  const ys = parcel.geometry.map(([, lat]) => lat);
  const minLon = Math.min(...xs);
  const maxLon = Math.max(...xs);
  const minLat = Math.min(...ys);
  const maxLat = Math.max(...ys);
  const fallbackCenter = lonLatCentroid(parcel.geometry);
  const center = state.samChipCenter || fallbackCenter;
  const spanLon = Math.max((maxLon - minLon) * 1.68, 0.006);
  const spanLat = Math.max((maxLat - minLat) * 1.68, 0.0034);
  return {
    left: center.lon - spanLon / 2,
    right: center.lon + spanLon / 2,
    bottom: center.lat - spanLat / 2,
    top: center.lat + spanLat / 2,
    spanLon,
    spanLat
  };
}

function lonLatCentroid(points) {
  return points.reduce(
    (sum, [lon, lat]) => ({ lon: sum.lon + lon / points.length, lat: sum.lat + lat / points.length }),
    { lon: 0, lat: 0 }
  );
}

function chipPointsToGeometry(points, parcel = selectedSamParcel()) {
  const bounds = samChipBounds(parcel);
  return points.map(([x, y]) => [
    Number((bounds.left + ((x - 48) / 544) * (bounds.right - bounds.left)).toFixed(7)),
    Number((bounds.bottom + ((312 - y) / 264) * (bounds.top - bounds.bottom)).toFixed(7))
  ]);
}

function applyDummyPrediction(parcel, index) {
  const modelBias = { "hgb-temporal": 0, "extratrees-phenology": 4, "tinyvit-parcel": 7 }[state.selectedModel] || 0;
  const crops = ["Soybean", "Paddy", "Gram", "Wheat"];
  const stresses = ["Low", "Moderate", "High"];
  const crop = crops[(index + modelBias) % crops.length];
  const confidence = clamp(76 + ((index * 7 + modelBias) % 19), 0, 97);
  const stress = stresses[(index + Math.floor(modelBias / 4)) % stresses.length];
  const stressScore = { Low: 18, Moderate: 48, High: 72 }[stress];
  const yieldValue = { Soybean: 2.1, Paddy: 4.5, Gram: 1.3, Wheat: 3.8 }[crop];
  const ndviPeak = { Soybean: 0.64, Paddy: 0.72, Gram: 0.43, Wheat: 0.69 }[crop];
  return {
    ...parcel,
    crop,
    confidence,
    stress,
    stressScore,
    yield: yieldValue,
    production: Number((parcel.acreage * yieldValue).toFixed(1)),
    stage: "Predicted",
    moisture: stress === "Low" ? "Adequate" : stress === "Moderate" ? "Variable" : "Low",
    riskCause: `${modelOptions().find((item) => item.id === state.selectedModel)?.label} prediction attached`,
    advisory: stress === "High" ? "Prioritize validation and stress advisory." : "Prediction ready for review.",
    ndvi: [0.24, 0.44, ndviPeak, Number((ndviPeak - 0.1).toFixed(2))],
    epochStates: data.epochs.map((epoch, epochIndex) => ({
      cropClass: crop,
      confidence: Math.max(58, confidence - Math.abs(2 - epochIndex) * 6),
      stress,
      stressScore,
      ndvi: [0.24, 0.44, ndviPeak, Number((ndviPeak - 0.1).toFixed(2))][epochIndex],
      evi: Number(([0.24, 0.44, ndviPeak, Number((ndviPeak - 0.1).toFixed(2))][epochIndex] * 0.68).toFixed(2)),
      stateNote: `${epoch.label} ${crop} prediction from ${state.selectedModel}`
    }))
  };
}

function aoiFocusParcel() {
  // No pre-created parcels: the SAM creator frames the AOI so fields can be
  // detected live from the imagery.
  const center = data.basemap.center;
  const dLon = 0.0034;
  const dLat = 0.0019;
  return {
    id: "AOI",
    village: data.insurer?.geography || "Pilot AOI",
    crop: "Pending",
    acreage: 0,
    geometry: [
      [center.lon - dLon, center.lat - dLat],
      [center.lon + dLon, center.lat - dLat],
      [center.lon + dLon, center.lat + dLat],
      [center.lon - dLon, center.lat + dLat]
    ]
  };
}

function selectedSamParcel() {
  return (
    data.parcels.find((item) => item.id === state.samSourceParcelId) ||
    data.parcels[0] ||
    aoiFocusParcel()
  );
}

function samChipPolygon(parcel) {
  const { left, right, bottom, top } = samChipBounds(parcel);

  return parcel.geometry
    .map(([lon, lat]) => {
      const x = 48 + ((lon - left) / (right - left)) * 544;
      const y = 312 - ((lat - bottom) / (top - bottom)) * 264;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function samPromptMarkup() {
  return state.samPrompts
    .map((prompt, index) => {
      if (prompt.kind === "box") {
        return `
          <g class="sam-prompt-box">
            <rect x="${prompt.x - 54}" y="${prompt.y - 34}" width="108" height="68" rx="3" />
            <text x="${prompt.x - 48}" y="${prompt.y - 40}">box ${index + 1}</text>
          </g>
        `;
      }
      return `
        <g class="sam-prompt-point">
          <circle cx="${prompt.x}" cy="${prompt.y}" r="7" />
          <text x="${prompt.x + 11}" y="${prompt.y + 4}">p${index + 1}</text>
        </g>
      `;
    })
    .join("");
}

function samDraftMarkup() {
  if (!state.samDraftPoints.length) {
    return "";
  }
  return `
    <g class="sam-draft-polygon">
      ${state.samDraftPoints.length >= 2 ? `<polyline points="${pointsToString(state.samDraftPoints)}" />` : ""}
      ${state.samDraftPoints.length >= 3 ? `<polygon points="${pointsToString(state.samDraftPoints)}" />` : ""}
      ${state.samDraftPoints
        .map(([x, y], index) => `<circle cx="${x}" cy="${y}" r="6" /><text x="${x + 9}" y="${y + 4}">${index + 1}</text>`)
        .join("")}
    </g>
  `;
}

function pointsToString(points) {
  return points.map(([x, y]) => `${Number(x).toFixed(1)},${Number(y).toFixed(1)}`).join(" ");
}

function polygonPointCentroid(points) {
  return points.reduce(
    (sum, [x, y]) => ({ x: sum.x + x / points.length, y: sum.y + y / points.length }),
    { x: 0, y: 0 }
  );
}

function samSuggestionMarkup() {
  return state.samSuggestions
    .map((mask, index) => {
      const selected = state.selectedSamMaskIds.includes(mask.id) ? "selected" : "";
      const centroid = polygonPointCentroid(mask.chipPoints);
      return `
        <g class="sam-suggested-mask ${selected}" data-sam-sample="${mask.id}" data-sample-index="${index}">
          <polygon points="${pointsToString(mask.chipPoints)}" />
          <text x="${centroid.x.toFixed(1)}" y="${centroid.y.toFixed(1)}">${Math.round(mask.score * 100)}%</text>
        </g>
      `;
    })
    .join("");
}

function samVertexMarkup() {
  return state.samSuggestions
    .filter((mask) => state.selectedSamMaskIds.includes(mask.id))
    .map((mask) =>
      mask.chipPoints
        .map(
          ([x, y], index) => `
            <circle class="sam-vertex-handle" data-sam-mask="${mask.id}" data-vertex-index="${index}" cx="${x}" cy="${y}" r="7" />
          `
        )
        .join("")
    )
    .join("");
}

function samStatusLabel() {
  if (state.samLoading) {
    return "Working…";
  }
  if (state.samPublishedParcelId) {
    return "Published";
  }
  if (state.samQcAccepted) {
    return "QC accepted";
  }
  if (state.samCandidateReady) {
    return "Candidate ready";
  }
  if (state.samPrompts.length > 0) {
    return "Prompts placed";
  }
  return "Ready";
}

function samChipUrl(parcel) {
  const epoch = data.epochs[state.epochIndex];
  const epochId = epoch.id || epoch.date || String(state.epochIndex);
  const center = state.samChipCenter || lonLatCentroid(parcel.geometry);
  return `${apiBase}/api/sam/chip?parcelId=${encodeURIComponent(parcel.id)}&epochId=${encodeURIComponent(epochId)}&centerLon=${encodeURIComponent(center.lon)}&centerLat=${encodeURIComponent(center.lat)}`;
}

function samSvgPoint(event, svg) {
  const rect = svg.getBoundingClientRect();
  const box = state.samChipViewBox;
  return {
    x: box.x + ((event.clientX - rect.left) / rect.width) * box.width,
    y: box.y + ((event.clientY - rect.top) / rect.height) * box.height
  };
}

function toggleSamMask(maskId) {
  if (state.selectedSamMaskIds.includes(maskId)) {
    state.selectedSamMaskIds = state.selectedSamMaskIds.filter((id) => id !== maskId);
  } else {
    state.selectedSamMaskIds = [...state.selectedSamMaskIds, maskId];
    state.selectedSamMaskId = maskId;
  }
  if (!state.selectedSamMaskId || !state.selectedSamMaskIds.includes(state.selectedSamMaskId)) {
    state.selectedSamMaskId = state.selectedSamMaskIds[0] || null;
  }
}

function renderRfpBadges() {
  return "";
}

function formatTemplate(template, parcel) {
  return template.replace(/\{(\w+)\}/g, (_, key) => parcel[key] ?? "");
}

function parcelColor(parcel) {
  const temporal = parcelEpochState(parcel);
  if (state.activeLayers.stress) {
    return data.stressColors[temporal.stress];
  }
  if (state.activeLayers.yield) {
    const intensity = clamp(parcel.yield / 8.5, 0.2, 1);
    return `rgba(46, 112, 126, ${intensity.toFixed(2)})`;
  }
  return data.crops[temporal.cropClass]?.color || "#20a4ad";
}

function lonLatToTile(lon, lat, zoom) {
  const scale = 2 ** zoom;
  const latRad = (lat * Math.PI) / 180;
  return {
    x: ((lon + 180) / 360) * scale,
    y: ((1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2) * scale
  };
}

function mapContainerSize() {
  const container = document.querySelector("#satelliteBasemap");
  return {
    width: container?.clientWidth || mapViewBox.width,
    height: container?.clientHeight || mapViewBox.height
  };
}

function mapPixelOrigin(width, height) {
  const { center, zoom, tileSize } = data.basemap;
  const centerTile = lonLatToTile(center.lon, center.lat, zoom);
  return {
    x: centerTile.x * tileSize - width / 2,
    y: centerTile.y * tileSize - height / 2
  };
}

function projectLonLat(lon, lat) {
  const { zoom, tileSize } = data.basemap;
  const size = mapContainerSize();
  const origin = mapPixelOrigin(size.width, size.height);
  const tile = lonLatToTile(lon, lat, zoom);
  const screenX = tile.x * tileSize - origin.x;
  const screenY = tile.y * tileSize - origin.y;
  return {
    x: (screenX / size.width) * mapViewBox.width,
    y: (screenY / size.height) * mapViewBox.height
  };
}

function projectedPolygon(parcel) {
  return parcel.geometry
    .map(([lon, lat]) => {
      const point = projectLonLat(lon, lat);
      return `${point.x.toFixed(1)},${point.y.toFixed(1)}`;
    })
    .join(" ");
}

function polygonCentroid(points) {
  const projected = points.map(([lon, lat]) => projectLonLat(lon, lat));
  return projected.reduce(
    (sum, point) => ({ x: sum.x + point.x / projected.length, y: sum.y + point.y / projected.length }),
    { x: 0, y: 0 }
  );
}

function basemapTileUrl(epoch, z, y, x) {
  const epochId = epoch.id || epoch.date || String(state.epochIndex);
  const template = data.basemap.backendTileUrl || data.api?.tileTemplate || data.basemap.tileUrl;
  return template
    .replace("{epochId}", encodeURIComponent(epochId))
    .replace("{tileSet}", epoch.tileSet)
    .replace("{z}", z)
    .replace("{y}", y)
    .replace("{x}", x);
}

function renderBasemap() {
  const container = document.querySelector("#satelliteBasemap");
  if (!container) {
    return;
  }

  const epoch = data.epochs[state.epochIndex];
  const { zoom, tileSize } = data.basemap;
  const { width, height } = mapContainerSize();
  const origin = mapPixelOrigin(width, height);
  const startX = Math.floor(origin.x / tileSize) - 1;
  const endX = Math.floor((origin.x + width) / tileSize) + 1;
  const startY = Math.floor(origin.y / tileSize) - 1;
  const endY = Math.floor((origin.y + height) / tileSize) + 1;
  const tiles = [];

  for (let y = startY; y <= endY; y += 1) {
    for (let x = startX; x <= endX; x += 1) {
      tiles.push(`
        <img
          alt=""
          src="${basemapTileUrl(epoch, zoom, y, x)}"
          style="left:${(x * tileSize - origin.x).toFixed(1)}px; top:${(y * tileSize - origin.y).toFixed(1)}px;"
        />
      `);
    }
  }

  container.innerHTML = tiles.join("");
  document.querySelector("#imageryAttribution").innerHTML = `
    <a href="${data.basemap.sourceUrl}" target="_blank" rel="noopener">${data.basemap.provider}</a>
    | ${data.basemap.attribution}
  `;
}

function renderImageryCompliance() {
  const epoch = data.epochs[state.epochIndex];
  document.querySelector("#imageryCompliance").innerHTML = `
    <article>
      <span>AOI</span>
      <strong>${data.basemap.aoi}</strong>
    </article>
    <article>
      <span>Epoch</span>
      <strong>${epoch.label} | ${epoch.date}</strong>
    </article>
    <article>
      <span>Imagery</span>
      <strong>Satellite, updated through the season</strong>
    </article>
  `;
}

function renderStaticSurfaceBadges() {
  document.querySelectorAll("[data-rfp-surface]").forEach((container) => {
    container.innerHTML = "";
  });
}

function activeProductTab() {
  return productTabs.find((tab) => tab.id === state.activeProductTab) || productTabs[0];
}

function renderProductTabs() {
  const container = document.querySelector("#productTabs");
  if (!container) {
    return;
  }
  container.innerHTML = productTabs
    .map((tab) => {
      const active = tab.id === state.activeProductTab ? "active" : "";
      return `
        <button class="product-tab ${active}" type="button" data-product-tab="${tab.id}">
          <span>${tab.eyebrow}</span>
          <strong>${tab.label}</strong>
          <small>${tab.body}</small>
        </button>
      `;
    })
    .join("");

  document.body.dataset.productTab = state.activeProductTab;
  container.querySelectorAll("[data-product-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      applyProductTab(button.dataset.productTab, true);
    });
  });
}

function renderProductFocus() {
  const tab = activeProductTab();
  document.querySelector("#productFocusTitle").textContent = tab.title;
  const container = document.querySelector("#reviewerSteps");
  container.innerHTML = tab.focus
    .map(
      (item, index) => `
        <article class="reviewer-step product-focus-card ${index === 0 ? "active" : ""}">
          <span class="reviewer-index">${String(index + 1).padStart(2, "0")}</span>
          <span class="reviewer-copy">
            <strong>${item}</strong>
            <small>${tab.body}</small>
          </span>
        </article>
      `
    )
    .join("");
}

function applyProductTab(tabId, shouldScroll = false) {
  const tab = productTabs.find((item) => item.id === tabId);
  if (!tab) {
    return;
  }
  state.activeProductTab = tab.id;
  Object.keys(state.activeLayers).forEach((layerId) => {
    state.activeLayers[layerId] = Boolean(tab.layers[layerId]);
  });
  state.mapMode = tab.mapMode;
  if (tab.id === "fields") {
    state.activeSamStage = state.activeSamStage || "prompt";
    state.selectedPanel = "parcel";
  }
  if (tab.id === "lgnd") {
    const flagged = [...data.parcels, ...state.userParcels].find((parcel) => parcelEpochState(parcel).stressScore >= 45);
    state.selectedParcelId = flagged?.id || state.selectedParcelId;
    // Lazy-load similar fields the first time the review tab opens.
    if (!state.similar?.available && !state.similarLoading) {
      refreshSimilarFields();
    }
  }

  renderProductTabs();
  renderProductFocus();
  renderLayerControls();
  renderLegend();
  renderMapModeControls();
  renderMap();
  renderParcelDetails();
  renderSamWorkflow();
  renderLgndFlow();

  if (shouldScroll) {
    document.getElementById(tab.target)?.scrollIntoView({ behavior: "smooth", block: "center" });
    showToast(`${tab.title} active.`);
  }
}

function renderTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.panel === state.selectedPanel);
  });
}

function renderReviewerMode() {
  const container = document.querySelector("#reviewerSteps");
  container.innerHTML = data.reviewerSteps
    .map((step) => {
      const active = step.id === state.activeReviewerStep ? "active" : "";
      return `
        <article class="reviewer-step ${active}" data-reviewer-step="${step.id}" role="button" tabindex="0">
          <span class="reviewer-index">${step.step}</span>
          <span class="reviewer-copy">
            <strong>${step.title}</strong>
            <small>${step.body}</small>
            <span class="rfp-badge-row">${renderRfpBadges(step.requirements)}</span>
          </span>
        </article>
      `;
    })
    .join("");
}

function renderLayerControls() {
  const container = document.querySelector("#layerControls");
  container.innerHTML = data.layers
    .map((layer) => {
      const checked = state.activeLayers[layer.id] ? "checked" : "";
      return `
        <div class="layer-toggle">
          <label class="layer-choice">
            <input type="checkbox" data-layer="${layer.id}" ${checked} />
            <span class="layer-copy">
              <strong>${layer.label}</strong>
              <small>${layer.service} ${layer.kind}</small>
            </span>
          </label>
          <span class="rfp-badge-row">${renderRfpBadges(layer.requirements)}</span>
        </div>
      `;
    })
    .join("");

  container.querySelectorAll("input").forEach((input) => {
    input.addEventListener("change", (event) => {
      state.activeLayers[event.target.dataset.layer] = event.target.checked;
      renderMap();
      renderLegend();
    });
  });
}

function renderMetrics() {
  const grid = document.querySelector("#metricGrid");
  grid.innerHTML = data.metrics
    .map(
      (metric) => `
      <article class="metric-card" data-metric="${metric.id}">
        <div class="metric-head">
          <span>${metric.label}</span>
          <span class="rfp-badge-row">${renderRfpBadges(metric.requirements)}</span>
        </div>
        <strong>${metric.value}</strong>
        <p>${metric.detail}</p>
        <small>${metric.trend}</small>
      </article>
    `
    )
    .join("");
}

function renderHeroMetrics() {
  const grid = document.querySelector("#heroMetrics");
  if (!grid) {
    return;
  }
  grid.innerHTML = data.insurer.heroStats
    .map(
      (metric) => `
      <article class="hero-metric">
        <span>${metric.label}</span>
        <strong>${metric.value}</strong>
        <p>${metric.detail}</p>
      </article>
    `
    )
    .join("");
}

function renderLegend() {
  const legend = document.querySelector("#legend");
  const entries = state.activeLayers.stress
    ? Object.entries(data.stressColors).map(([label, color]) => ({ label, color }))
    : cropLegend;

  legend.innerHTML = entries
    .map(
      (entry) => `
      <span class="legend-item">
        <i style="background:${entry.color}"></i>${entry.label}
      </span>
    `
    )
    .join("");
}

function renderMapModeControls() {
  const container = document.querySelector("#mapModeControls");
  if (!container) {
    return;
  }
  container.innerHTML = `
    <div class="mode-toggle" role="group" aria-label="Web GIS mode">
      <button class="${state.mapMode === "edit" ? "active" : ""}" type="button" data-map-mode="edit">Add parcels</button>
      <button class="${state.mapMode === "predict" ? "active" : ""}" type="button" data-map-mode="predict">Run claims ML</button>
    </div>
    <div class="model-runner ${state.mapMode === "predict" ? "visible" : ""}">
      <label>
        Model
        <select id="modelSelect">
          ${modelOptions()
            .map((model) => `<option value="${model.id}" ${model.id === state.selectedModel ? "selected" : ""}>${model.label}</option>`)
            .join("")}
        </select>
      </label>
      <button class="run-ml-button" type="button" id="runMlButton" ${state.userParcels.length && !state.mlRunning ? "" : "disabled"}>
        ${state.mlRunning ? "Running..." : "Run"}
      </button>
    </div>
  `;

  container.querySelectorAll("[data-map-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.mapMode = button.dataset.mapMode;
      renderMapModeControls();
      renderMap();
      showToast(state.mapMode === "edit" ? "Parcel editing mode active." : "Claims ML mode active.");
    });
  });

  container.querySelector("#modelSelect")?.addEventListener("change", (event) => {
    state.selectedModel = event.target.value;
    const model = modelOptions().find((item) => item.id === state.selectedModel);
    showToast(`Selected model: ${model.label}.`);
  });

  container.querySelector("#runMlButton")?.addEventListener("click", runMlPredictions);
}

function runMlPredictions() {
  if (!state.userParcels.length || state.mlRunning) {
    return;
  }
  state.mlRunning = true;
  renderMapModeControls();
  renderMap();
  showToast("Analyzing fields…");
  window.setTimeout(() => {
    state.userParcels = state.userParcels.map((parcel, index) => applyDummyPrediction(parcel, index));
    state.mlRunning = false;
    state.mapMode = "predict";
    state.selectedParcelId = state.userParcels[0].id;
    state.selectedPanel = "parcel";
    renderMapModeControls();
    renderLegend();
    renderMap();
    renderParcelDetails();
    showToast("Demo ML predictions generated for saved parcels.");
  }, 3000);
}

function sparkline(points) {
  const width = 180;
  const height = 58;
  const coords = points
    .map((value, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - value * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return `
    <svg class="sparkline" viewBox="0 0 ${width} ${height}" aria-label="NDVI trend">
      <polyline points="${coords}" />
      ${points
        .map((value, index) => {
          const x = (index / (points.length - 1)) * width;
          const y = height - value * height;
          return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" />`;
        })
        .join("")}
    </svg>
  `;
}

function renderParcelDetails() {
  const parcel = selectedParcel();
  if (!parcel) {
    document.querySelector("#parcelTitle").textContent = "No field selected";
    document.querySelector("#parcelDetails").innerHTML = `<p class="muted-text">Detect fields below and save them, then run analysis to see crop and risk here.</p>`;
    return;
  }
  const temporal = parcelEpochState(parcel);
  const epoch = data.epochs[state.epochIndex];
  const gt = parcelGt(parcel);
  const production = productionEstimate(parcel);
  const confidence = clamp(temporal.confidence, 0, 100);
  const stressScore = clamp(temporal.stressScore, 0, 100);
  const parcelView = {
    ...parcel,
    crop: temporal.cropClass,
    confidence: temporal.confidence,
    stress: temporal.stress,
    stressScore: temporal.stressScore,
    riskCause: temporal.stateNote
  };
  document.querySelector("#parcelTitle").textContent = `${parcel.id} | ${parcel.village}`;
  renderTabs();

  const views = {
    parcel: `
      <div class="rfp-badge-row inline">${renderRfpBadges(data.surfaceRequirements.parcel)}</div>
      <div class="parcel-click-summary">
        <span>Click parcel result</span>
        <strong>${temporal.cropClass} | ${confidence}% confidence | ${temporal.stress} stress | ${production.toFixed(1)} t production</strong>
      </div>
      <div class="parcel-summary grouped">
        <article class="parcel-metric primary">
          <span>Crop</span>
          <strong>${temporal.cropClass}</strong>
          <small>Parcel-level classification</small>
        </article>
        <article class="parcel-metric">
          <span>Confidence</span>
          <strong>${confidence}%</strong>
          <meter min="0" max="100" value="${confidence}"></meter>
        </article>
        <article class="parcel-metric stress-${statusKey(temporal.stress)}">
          <span>Stress</span>
          <strong>${temporal.stress}</strong>
          <meter min="0" max="100" value="${stressScore}"></meter>
          <small>Score ${stressScore}/100</small>
        </article>
        <article class="parcel-metric">
          <span>Crop vigor</span>
          <strong>${Math.round(temporal.ndvi * 100)}%</strong>
          <small>${epoch.label} greenness</small>
        </article>
        <article class="parcel-metric">
          <span>Area</span>
          <strong>${parcel.acreage.toFixed(1)} ha</strong>
          <small>Insured area</small>
        </article>
        <article class="parcel-metric">
          <span>Yield</span>
          <strong>${parcel.yield.toFixed(1)} t/ha</strong>
          <small>Expected this season</small>
        </article>
        <article class="parcel-metric production">
          <span>Expected production</span>
          <strong>${production.toFixed(1)} t</strong>
          <small>${parcel.acreage.toFixed(1)} ha × ${parcel.yield.toFixed(1)} t/ha</small>
        </article>
        <article class="parcel-metric">
          <span>Season</span>
          <strong>${epoch.label}</strong>
          <small>${epoch.date}</small>
        </article>
      </div>
      ${sparkline(parcel.ndvi)}
      <p class="advisory-text">${temporal.stateNote}. ${parcel.advisory}</p>
    `,
    advisory: `
      <div class="advisory-actions">
        ${Object.entries(data.advisoryTemplates)
          .map(
            ([audience, template]) => `
            <article class="advisory-card">
              <span>${audience}</span>
              <span class="rfp-badge-row">${renderRfpBadges(data.surfaceRequirements.advisory)}</span>
              <p>${formatTemplate(template, parcelView)}</p>
              <button type="button" class="mini-action" data-advisory="${audience}">Queue ${audience}</button>
            </article>
          `
          )
          .join("")}
      </div>
    `,
    field: `
      <div class="rfp-badge-row inline">${renderRfpBadges(data.surfaceRequirements.field)}</div>
      <div class="field-detail">
        <div class="field-photo">${gt ? gt.crop.slice(0, 2).toUpperCase() : "AI"}</div>
        <div>
          <strong>${gt ? gt.id : "No GT point yet"} | ${gt ? gt.status : "Model-only evidence"}</strong>
          <p>${gt ? `${gt.officer} captured crop=${gt.crop}, GPS=${gt.gps}, split=${gt.split}.` : "Parcel is pending field validation; model confidence and stress layers drive the current advisory."}</p>
        </div>
      </div>
      <div class="evidence-checks">
        <span>Geo-tagged photo</span>
        <span>GPS accuracy check</span>
        <span>30% validation holdout</span>
        <span>QC audit trail</span>
      </div>
    `
  };

  document.querySelector("#parcelDetails").innerHTML = views[state.selectedPanel];

  document.querySelectorAll(".mini-action").forEach((button) => {
    button.addEventListener("click", () => {
      showToast(`${button.dataset.advisory} advisory queued for ${parcel.id}.`);
    });
  });
}

function renderProcurement() {
  document.querySelector("#procurementSummary").innerHTML = data.insurer.claimSummary
    .map((item) => `<div><span>${item.label}</span><strong>${item.value}</strong></div>`)
    .join("");

  const list = document.querySelector("#procurementList");
  list.innerHTML = data.procurementCenters
    .map(
      (center) => `
      <article class="procurement-item">
        <div>
          <strong>${center.name}</strong>
          <span>${center.id} | ${center.arrivals}</span>
        </div>
        <span class="rfp-badge-row">${renderRfpBadges(data.surfaceRequirements.procurement)}</span>
        <meter min="0" max="100" value="${center.load}"></meter>
        <small>${center.load}% workload | ${center.tokens.toLocaleString()} open packets | ${center.status}</small>
      </article>
    `
    )
    .join("");
}

function renderEvidence() {
  document.querySelector("#evidenceList").innerHTML = data.evidence
    .map(
      (item) => `
      <article class="evidence-item">
        <strong>${item.title}</strong>
        <span class="rfp-badge-row">${renderRfpBadges(item.requirements)}</span>
        <p>${item.body}</p>
      </article>
    `
    )
    .join("");
}

function renderMlCapabilities() {
  document.querySelector("#mlCapabilityGrid").innerHTML = data.mlCapabilities
    .map(
      (item) => `
      <article class="ml-card">
        <div>
          <strong>${item.title}</strong>
          <span>${item.metric}</span>
        </div>
        <span class="rfp-badge-row">${renderRfpBadges(item.requirements)}</span>
        <p>${item.body}</p>
        <div class="tag-list compact">
          ${item.tags.map((tag) => `<span>${tag}</span>`).join("")}
        </div>
      </article>
    `
    )
    .join("");
}

const changeLegend = {
  fallow_to_paddy: { label: "Fallow → Paddy", tone: "transition" },
  fallow_to_soybean: { label: "Fallow → Soybean", tone: "transition" },
  fallow_to_gram: { label: "Fallow → Gram", tone: "transition" },
  fallow_to_wheat: { label: "Fallow → Wheat", tone: "transition" },
  healthy_to_waterlogged: { label: "Healthy → Waterlogged", tone: "loss" },
  healthy_to_stressed: { label: "Healthy → Stressed", tone: "loss" },
  canopy_to_harvest: { label: "Canopy → Harvest decline", tone: "neutral" },
  stable_season: { label: "Stable season", tone: "stable" }
};

function changeLegendEntry(key) {
  return changeLegend[key] || { label: key.replace(/_/g, " "), tone: "neutral" };
}

function renderMlValidation() {
  const container = document.querySelector("#mlValidationCard");
  if (!container) {
    return;
  }
  const validation = state.mlValidation || {};
  const predictions = state.mlPredictions?.predictions || [];
  if (!validation.available) {
    container.innerHTML = `
      <article class="ml-validation status-planned">
        <div class="ml-validation-head">
          <strong>Model validation</strong>
          <span class="ml-status-pill planned">Artifact pending</span>
        </div>
        <p class="muted-text">Run <code>backend/scripts/ingest_sentinel2.py</code> then <code>run_ml_predictions.py</code> to populate crop/stress predictions and this validation card.</p>
      </article>
    `;
    return;
  }

  const classes = validation.classes || [];
  const matrix = validation.confusionMatrix || [];
  const recall = validation.perClassRecall || {};
  const matrixRows = classes
    .map((cropClass, rowIndex) => {
      const cells = (matrix[rowIndex] || [])
        .map((value, colIndex) => `<td class="${rowIndex === colIndex ? "diag" : ""}">${value}</td>`)
        .join("");
      const recallValue = recall[cropClass]?.recall;
      return `<tr><th>${cropClass}</th>${cells}<td class="recall">${recallValue == null ? "—" : Math.round(recallValue * 100) + "%"}</td></tr>`;
    })
    .join("");

  // Temporal change legend: class transition, confidence/stress deltas, GT-needed.
  const changeCounts = predictions.reduce((acc, prediction) => {
    acc[prediction.changeLabel] = (acc[prediction.changeLabel] || 0) + 1;
    return acc;
  }, {});
  const changeChips = Object.entries(changeCounts)
    .map(([key, count]) => {
      const entry = changeLegendEntry(key);
      return `<span class="change-chip tone-${entry.tone}">${entry.label}<small>${count}</small></span>`;
    })
    .join("");
  const gtNeeded = predictions.filter((prediction) => prediction.gtNeeded).length;

  const overall = Math.round((validation.overallAccuracy || 0) * 100);
  const sample = validation.sampleSize || predictions.length;
  container.innerHTML = `
    <article class="ml-validation status-demo">
      <div class="ml-validation-metrics">
        <div><span>Crop type match</span><strong>${overall}%</strong></div>
        <div><span>Fields checked</span><strong>${sample}</strong></div>
        <div><span>Needs a field check</span><strong>${gtNeeded}</strong></div>
      </div>
      <div class="change-legend" aria-label="What changed this season">
        <span class="change-legend-label">Changed this season</span>
        ${changeChips}
      </div>
    </article>
  `;
}

async function loadSimilarFields() {
  const url = data.api?.similarFields || "/api/review/similar";
  try {
    const response = await fetch(`${apiBase}${url}?limit=9`, { cache: "no-store" });
    if (response.ok) {
      return response.json();
    }
  } catch {
    // Static file mode has no backend; the review tab shows a quiet empty state.
  }
  return { available: false, results: [] };
}

async function refreshSimilarFields() {
  state.similarLoading = true;
  renderLgndFlow();
  state.similar = await loadSimilarFields();
  state.similarDecisions = {};
  state.similarLoading = false;
  renderLgndFlow();
}

function renderLgndFlow() {
  const container = document.querySelector("#lgndFlow");
  if (!container) {
    return;
  }
  const review = state.similar || { available: false, results: [] };
  const decisions = state.similarDecisions || {};

  if (state.similarLoading) {
    container.innerHTML = `<div class="review-empty"><strong>Finding similar fields…</strong><p>Scanning the field library for the closest matches.</p></div>`;
    return;
  }
  if (!review.available || !review.results.length) {
    container.innerHTML = `
      <div class="review-empty">
        <strong>No similar fields to review right now</strong>
        <p>When the model flags a field, its closest visual matches appear here for a quick confirm-or-dismiss.</p>
        <button type="button" class="review-refresh" data-review-action="refresh">Find similar fields</button>
      </div>`;
    container.querySelector("[data-review-action='refresh']")?.addEventListener("click", refreshSimilarFields);
    return;
  }

  const reviewed = Object.keys(decisions).length;
  const cards = review.results
    .map((item) => {
      const decision = decisions[item.id];
      return `
        <article class="review-card ${decision || ""}">
          <div class="review-thumb" style="background-image:url('${apiBase}${item.thumb}')"></div>
          <div class="review-card-body">
            <strong>${item.similarity}% similar</strong>
            <span>${item.date || "recent"}</span>
          </div>
          <div class="review-actions">
            <button type="button" data-review-id="${item.id}" data-review-action="confirm">${decision === "confirm" ? "Confirmed" : "Confirm"}</button>
            <button type="button" data-review-id="${item.id}" data-review-action="dismiss">${decision === "dismiss" ? "Dismissed" : "Dismiss"}</button>
          </div>
        </article>`;
    })
    .join("");

  container.innerHTML = `
    <div class="review-intro">
      <div>
        <strong>Closest matches to the flagged field</strong>
        <p>Confirm the ones that look like the same problem, dismiss the rest. ${reviewed}/${review.results.length} reviewed.</p>
      </div>
      <div class="review-query">
        <div class="review-thumb" style="background-image:url('${apiBase}${review.query.thumb}')"></div>
        <span>Flagged field</span>
      </div>
    </div>
    <div class="review-grid">${cards}</div>
    <button type="button" class="review-refresh" data-review-action="refresh">Refresh matches</button>
  `;

  container.querySelector("[data-review-action='refresh']")?.addEventListener("click", refreshSimilarFields);
  container.querySelectorAll("[data-review-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.reviewId;
      const action = button.dataset.reviewAction;
      state.similarDecisions[id] = state.similarDecisions[id] === action ? undefined : action;
      if (!state.similarDecisions[id]) {
        delete state.similarDecisions[id];
      }
      renderLgndFlow();
    });
  });
}

function renderSamWorkflow() {
  const container = document.querySelector("#samWorkflow");
  const demo = data.samBoundaryDemo;
  const activeStage = demo?.stages.find((stage) => stage.id === state.activeSamStage) || demo?.stages[0];
  const parcel = selectedSamParcel();
  const selectedMask = state.samSuggestions.find((mask) => mask.id === state.selectedSamMaskId) || state.samSuggestions[0];
  const candidatePoints = selectedMask?.chipPoints || [];
  const candidateVisible = candidatePoints.length > 0 && (state.samCandidateReady || state.samQcAccepted || state.samPublishedParcelId === parcel.id);
  const chipBox = state.samChipViewBox;

  container.innerHTML = `
    <div class="sam-positioning">
      <span>${demo.label}</span>
      <strong>${demo.headline}</strong>
      <p>${demo.body}</p>
    </div>
    <section class="sam-annotation-tool" aria-label="SAM annotation tool">
      <div class="sam-tool-header">
        <div>
          <span>Annotation chip</span>
          <strong>${parcel.id} | ${parcel.village}</strong>
        </div>
        <em>${samStatusLabel()}</em>
      </div>
      <div class="sam-tool-body">
        <svg id="samChip" class="sam-chip sam-tool-${state.samTool}" viewBox="${chipBox.x} ${chipBox.y} ${chipBox.width} ${chipBox.height}" role="img" aria-label="SAM prompt annotation chip">
          <rect width="640" height="360" fill="#1b2623" />
          <image href="${samChipUrl(parcel)}" x="0" y="0" width="640" height="360" preserveAspectRatio="none" />
          ${state.samSuggestions.length === 0 ? `<polygon class="sam-source-boundary" points="${samChipPolygon(parcel)}" />` : ""}
          ${samSuggestionMarkup()}
          ${candidateVisible ? `<polygon class="sam-mask-preview ${state.samQcAccepted ? "accepted" : ""}" points="${pointsToString(candidatePoints)}" />` : ""}
          ${samPromptMarkup()}
          ${samDraftMarkup()}
          ${samVertexMarkup()}
        </svg>
        <div class="sam-tool-panel">
          <div class="sam-tool-toggle" role="group" aria-label="Prompt tool">
            <button class="${state.samTool === "point" ? "active" : ""}" type="button" data-sam-tool="point">Point</button>
            <button class="${state.samTool === "box" ? "active" : ""}" type="button" data-sam-tool="box">Box</button>
            <button class="${state.samTool === "draw" ? "active" : ""}" type="button" data-sam-tool="draw">Draw</button>
            <button class="${state.samTool === "edit" ? "active" : ""}" type="button" data-sam-tool="edit">Edit</button>
            <button class="${state.samTool === "pan" ? "active" : ""}" type="button" data-sam-tool="pan">Pan</button>
          </div>
          <div class="sam-tool-actions">
            <button type="button" data-sam-action="run" ${state.samLoading ? "disabled" : ""}>Detect fields</button>
            <button type="button" data-sam-action="save-draft" ${state.samDraftPoints.length >= 3 ? "" : "disabled"}>Save drawn</button>
            <button type="button" data-sam-action="publish" ${state.selectedSamMaskIds.length ? "" : "disabled"}>Save selected</button>
            <button type="button" data-sam-action="reset-view">Reset view</button>
            <button type="button" data-sam-action="clear-draw">Clear draw</button>
            <button type="button" data-sam-action="reset">Reset</button>
          </div>
          <div class="sam-tool-readout">
            <article><span>Prompts</span><strong>${state.samPrompts.length}</strong></article>
            <article><span>Masks</span><strong>${state.samSuggestions.length || "Pending"}</strong></article>
            <article><span>Selected</span><strong>${state.selectedSamMaskIds.length}</strong></article>
            <article><span>Output</span><strong>${state.samPublishedParcelId ? "GeoJSON" : "Not published"}</strong></article>
          </div>
          ${state.samBackendNote ? `<p class="sam-backend-note">${state.samBackendNote}</p>` : ""}
        </div>
      </div>
    </section>
    <div class="sam-stage-grid" role="tablist" aria-label="SAM boundary workflow stages">
      ${demo.stages
        .map(
          (stage) => `
          <button class="sam-stage ${stage.id === activeStage.id ? "active" : ""}" type="button" data-sam-stage="${stage.id}">
            <span>${stage.step}</span>
            <strong>${stage.title}</strong>
          </button>
        `
        )
        .join("")}
    </div>
    <article class="sam-stage-detail">
      <span>${activeStage.output}</span>
      <strong>${activeStage.title}</strong>
      <p>${activeStage.body}</p>
      <div class="tag-list compact">
        ${activeStage.tags.map((tag) => `<span>${tag}</span>`).join("")}
      </div>
    </article>
    <div class="sam-proof-grid">
      ${demo.proof
        .map(
          (item) => `
          <article>
            <span>${item.label}</span>
            <strong>${item.value}</strong>
            <p>${item.note}</p>
          </article>
        `
        )
        .join("")}
    </div>
    <div class="sam-workflow-steps">
      ${data.samWorkflow
        .map(
          (item) => `
          <article class="sam-step">
            <span>${item.step}</span>
            <div>
              <strong>${item.title}</strong>
              <p>${item.body}</p>
            </div>
          </article>
        `
        )
        .join("")}
    </div>
  `;

  container.querySelectorAll("[data-sam-stage]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeSamStage = button.dataset.samStage;
      state.activeLayers.sam = true;
      renderLayerControls();
      renderMap();
      renderSamWorkflow();
      showToast(`SAM/SamGeo stage selected: ${button.textContent.trim().replace(/\s+/g, " ")}.`);
    });
  });

  container.querySelectorAll("[data-sam-tool]").forEach((button) => {
    button.addEventListener("click", () => {
      state.samTool = button.dataset.samTool;
      renderSamWorkflow();
    });
  });

  const chip = container.querySelector("#samChip");
  chip?.addEventListener("pointerdown", (event) => {
    const point = samSvgPoint(event, chip);
    const vertex = event.target.closest("[data-sam-mask][data-vertex-index]");
    const sample = event.target.closest("[data-sam-sample]");

    if (vertex) {
      state.samDrag = {
        type: "vertex",
        maskId: vertex.dataset.samMask,
        vertexIndex: Number(vertex.dataset.vertexIndex)
      };
      chip.setPointerCapture(event.pointerId);
      event.preventDefault();
      return;
    }

    if (state.samTool === "pan") {
      state.samDrag = {
        type: "pan",
        startX: event.clientX,
        startY: event.clientY,
        viewBox: { ...state.samChipViewBox }
      };
      chip.setPointerCapture(event.pointerId);
      event.preventDefault();
      return;
    }

    // Clicking a detected candidate toggles its selection (multi-select). It must
    // stop here — falling through to prompt placement would reset the candidate
    // state and disable QC accept, so saved fields never reach the map.
    if (sample && state.samTool !== "draw") {
      toggleSamMask(sample.dataset.samSample);
      renderSamWorkflow();
      event.preventDefault();
      return;
    }

    if (state.samTool === "draw") {
      state.samDraftPoints.push([Number(point.x.toFixed(1)), Number(point.y.toFixed(1))]);
      renderSamWorkflow();
      return;
    }

    if (state.samTool === "point" || state.samTool === "box") {
      state.samPrompts.push({
        kind: state.samTool,
        x: Number(point.x.toFixed(1)),
        y: Number(point.y.toFixed(1))
      });
      state.samCandidateReady = false;
      state.samQcAccepted = false;
      state.samPublishedParcelId = null;
      state.activeSamStage = "prompt";
      renderSamWorkflow();
    }
  });

  chip?.addEventListener("pointermove", (event) => {
    if (!state.samDrag) {
      return;
    }
    if (state.samDrag.type === "pan") {
      const rect = chip.getBoundingClientRect();
      const dx = ((event.clientX - state.samDrag.startX) / rect.width) * state.samDrag.viewBox.width;
      const dy = ((event.clientY - state.samDrag.startY) / rect.height) * state.samDrag.viewBox.height;
      state.samChipViewBox = {
        ...state.samDrag.viewBox,
        x: state.samDrag.viewBox.x - dx,
        y: state.samDrag.viewBox.y - dy
      };
      chip.setAttribute("viewBox", `${state.samChipViewBox.x} ${state.samChipViewBox.y} ${state.samChipViewBox.width} ${state.samChipViewBox.height}`);
      return;
    }
    if (state.samDrag.type === "vertex") {
      const point = samSvgPoint(event, chip);
      const mask = state.samSuggestions.find((item) => item.id === state.samDrag.maskId);
      if (mask) {
        mask.chipPoints[state.samDrag.vertexIndex] = [
          Number(point.x.toFixed(1)),
          Number(point.y.toFixed(1))
        ];
        mask.geometry = chipPointsToGeometry(mask.chipPoints, parcel);
        state.samQcAccepted = false;
        event.target.setAttribute("cx", point.x.toFixed(1));
        event.target.setAttribute("cy", point.y.toFixed(1));
        chip.querySelector(`[data-sam-sample="${mask.id}"] polygon`)?.setAttribute("points", pointsToString(mask.chipPoints));
        chip.querySelector(".sam-mask-preview")?.setAttribute("points", pointsToString(mask.chipPoints));
      }
    }
  });

  chip?.addEventListener("pointerup", () => {
    if (state.samDrag) {
      if (state.samDrag.type === "pan") {
        const bounds = samChipBounds(parcel);
        state.samChipCenter = {
          lon: (state.samChipCenter || lonLatCentroid(parcel.geometry)).lon + (state.samChipViewBox.x / 640) * bounds.spanLon,
          lat: (state.samChipCenter || lonLatCentroid(parcel.geometry)).lat - (state.samChipViewBox.y / 360) * bounds.spanLat
        };
        state.samChipViewBox = { x: 0, y: 0, width: 640, height: 360 };
      }
      state.samDrag = null;
      renderSamWorkflow();
    }
  });

  chip?.addEventListener("pointercancel", () => {
    state.samDrag = null;
  });

  container.querySelectorAll("[data-sam-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.dataset.samAction;
      if (action === "run") {
        await runBackendSam();
        return;
      }
      if (action === "accept") {
        state.samQcAccepted = true;
        state.activeSamStage = "qc";
        showToast(`${state.selectedSamMaskIds.length} boundary candidate(s) accepted after human QC.`);
      }
      if (action === "publish") {
        const selectedMasks = state.samSuggestions.filter((mask) => state.selectedSamMaskIds.includes(mask.id));
        const parcels = selectedMasks.map((mask) => {
          const parcel = createAnnotatedParcel(mask);
          state.nextUserParcelNumber += 1;
          return parcel;
        });
        state.userParcels.push(...parcels);
        state.selectedParcelId = parcels[0]?.id || state.selectedParcelId;
        state.samPublishedParcelId = parcels[0]?.id || null;
        state.activeLayers.sam = true;
        state.activeSamStage = "publish";
        state.mapMode = "edit";
        renderLayerControls();
        renderMapModeControls();
        renderMap();
        renderParcelDetails();
        renderLegend();
        showToast(`${parcels.length} polygon(s) saved from annotation and added to Web-GIS.`);
      }
      if (action === "save-draft") {
        const parcel = createAnnotatedParcel({
          id: "drawn-polygon",
          chipPoints: [...state.samDraftPoints],
          geometry: chipPointsToGeometry(state.samDraftPoints, selectedSamParcel())
        });
        state.userParcels.push(parcel);
        state.nextUserParcelNumber += 1;
        state.selectedParcelId = parcel.id;
        state.samPublishedParcelId = parcel.id;
        state.samDraftPoints = [];
        state.mapMode = "edit";
        renderMapModeControls();
        renderMap();
        renderParcelDetails();
        renderLegend();
        showToast(`${parcel.id} saved from drawn polygon.`);
      }
      if (action === "reset-view") {
        state.samChipViewBox = { x: 0, y: 0, width: 640, height: 360 };
        state.samChipCenter = null;
      }
      if (action === "clear-draw") {
        state.samDraftPoints = [];
      }
      if (action === "reset") {
        state.samPrompts = [];
        state.samCandidateReady = false;
        state.samQcAccepted = false;
        state.samPublishedParcelId = null;
        state.samSuggestions = [];
        state.selectedSamMaskId = null;
        state.selectedSamMaskIds = [];
        state.samChipViewBox = { x: 0, y: 0, width: 640, height: 360 };
        state.samChipCenter = null;
        state.samDraftPoints = [];
        state.samBackendNote = "";
        state.activeSamStage = "prompt";
        renderMap();
      }
      renderSamWorkflow();
    });
  });
}

async function runBackendSam() {
  const parcel = selectedSamParcel();
  const epoch = data.epochs[state.epochIndex];
  state.samLoading = true;
  renderSamWorkflow();

  // Point/box prompts refine a single field; with none, segment every probable
  // field boundary in the viewport (SAM automatic mask generation).
  const useAuto = state.samPrompts.length === 0;
  const endpoint = useAuto ? "/api/sam/auto" : "/api/sam/suggest";

  try {
    const response = await fetch(`${apiBase}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        parcelId: parcel.id,
        epochId: epoch.id || epoch.date || String(state.epochIndex),
        center: state.samChipCenter || lonLatCentroid(parcel.geometry),
        prompts: state.samPrompts
      })
    });
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    const result = await response.json();
    state.samSuggestions = result.masks || [];
    // Auto mode shows all candidates unselected for the analyst to QC and pick;
    // prompted mode preselects the top mask.
    if (useAuto) {
      state.selectedSamMaskId = null;
      state.selectedSamMaskIds = [];
    } else {
      state.selectedSamMaskId = state.samSuggestions[0]?.id || null;
      state.selectedSamMaskIds = state.selectedSamMaskId ? [state.selectedSamMaskId] : [];
    }
    state.samBackendNote = result.model?.note || "";
    state.samCandidateReady = state.samSuggestions.length > 0;
    state.samQcAccepted = false;
    state.activeSamStage = "qc";
    state.activeLayers.sam = true;
    renderLayerControls();
    renderMap();
    const verb = useAuto ? "Found" : "Suggested";
    showToast(`${verb} ${state.samSuggestions.length} field boundaries.`);
  } catch (error) {
    state.samBackendNote = error.message;
    showToast(`SAM backend request failed: ${error.message}`);
  } finally {
    state.samLoading = false;
    renderSamWorkflow();
  }
}

function renderFieldFeed() {
  document.querySelector("#fieldFeed").innerHTML = data.groundTruth
    .map(
      (point) => `
      <article class="field-item ${point.split === "Validation holdout" ? "holdout" : ""}" data-gt="${point.id}">
        <div class="photo-token">${point.crop.slice(0, 2).toUpperCase()}</div>
        <div>
          <strong>${point.id} | ${point.crop}</strong>
          <span class="rfp-badge-row">${renderRfpBadges(data.surfaceRequirements.field)}</span>
          <p>${point.status} by ${point.officer}</p>
          <span>${point.split} | GPS ${point.gps}</span>
        </div>
      </article>
    `
    )
    .join("");

  document.querySelectorAll(".field-item").forEach((item) => {
    item.addEventListener("click", (event) => {
      if (event.target.closest(".rfp-badge")) {
        return;
      }
      const parcel = data.parcels.find((candidate) => candidate.validation === item.dataset.gt);
      if (parcel) {
        state.selectedParcelId = state.userParcels[0]?.id || parcel.id;
        state.selectedPanel = "field";
        renderMap();
        renderParcelDetails();
      }
    });
  });
}

function renderCompliance() {
  const container = document.querySelector("#complianceList");
  const rows = data.requirements
    .map(
      (item) => `
      <article class="coverage-row status-${item.status}" data-requirement="${item.section}" tabindex="0" aria-label="View RFP Section ${item.section}">
        <span class="coverage-section">RFP ${item.section}</span>
        <div class="coverage-requirement">
          <strong>${item.title}</strong>
          <p>${item.summary}</p>
        </div>
        <span class="coverage-proof">${item.evidence}</span>
        <span class="coverage-evidence">${item.evidenceType}</span>
        <em>${item.status}</em>
      </article>
    `
    )
    .join("");

  container.innerHTML = `
    <div class="coverage-header" aria-hidden="true">
      <span>RFP section</span>
      <span>Requirement</span>
      <span>Demo proof</span>
      <span>Evidence type</span>
      <span>Status</span>
    </div>
    ${rows}
  `;

  container.querySelectorAll(".coverage-row").forEach((row) => {
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openRequirementDrawer(row.dataset.requirement);
      }
    });
  });
}

function renderReports() {
  document.querySelector("#reportQueue").innerHTML = data.reports
    .map(
      (report) => `
      <article class="report-item">
        <div>
          <strong>${report.name}</strong>
          <span>${report.cadence}</span>
          <span class="rfp-badge-row">${renderRfpBadges(report.requirements)}</span>
        </div>
        <small>${report.formats}</small>
        <em>${report.status}</em>
      </article>
    `
    )
    .join("");
}

function renderMobileFlow() {
  document.querySelector("#mobileFlow").innerHTML = data.mobileFlow
    .map(
      (step) => `
      <article class="mobile-step">
        <span>${step.step}</span>
        <div>
          <strong>${step.title}</strong>
          <span class="rfp-badge-row">${renderRfpBadges(step.requirements)}</span>
          <p>${step.body}</p>
        </div>
      </article>
    `
    )
    .join("");
}

function renderIntegrations() {
  document.querySelector("#integrationGrid").innerHTML = data.integrations
    .map(
      (integration) => `
      <article class="integration-card">
        <strong>${integration.name}</strong>
        <span>${integration.status}</span>
        <span class="rfp-badge-row">${renderRfpBadges(integration.requirements)}</span>
        <p>${integration.detail}</p>
      </article>
    `
    )
    .join("");
}

function renderMap() {
  const svg = document.querySelector("#mapSvg");
  const epoch = data.epochs[state.epochIndex];
  const tab = activeProductTab();
  document.querySelector("#epochText").textContent = `${epoch.label}: ${epoch.date} - ${epoch.note}`;
  document.querySelector("#mapStatus").textContent = `${epoch.label} ${epoch.date} imagery active`;
  document.querySelector("#imageryStatus").textContent = `${tab.title} · Insured fields`;
  renderBasemap();
  renderImageryCompliance();

  const allParcels = [...data.parcels, ...state.userParcels];
  // Only saved fields appear on the map; on the merged Fields tab that is the
  // live-created portfolio, coloured by crop/risk once analysis is run.
  const visibleParcels = tab.id === "lgnd"
    ? allParcels.filter((parcel) => parcelEpochState(parcel).stressScore >= 45 || parcel.id === state.selectedParcelId)
    : allParcels;

  const parcelMarkup = visibleParcels
    .map((parcel) => {
      const selected = parcel.id === state.selectedParcelId ? "selected" : "";
      const temporal = parcelEpochState(parcel);
      const cropShort = data.crops[temporal.cropClass]?.short || "ML";
      const opacity = state.activeLayers.crop || state.activeLayers.stress || state.activeLayers.yield ? 0.5 : 0.2;
      const centroid = polygonCentroid(parcel.geometry);
      const showLabel = selected || tab.id === "lgnd";
      return `
        <g class="parcel-group user-parcel ${selected}" data-parcel="${parcel.id}">
          <polygon points="${projectedPolygon(parcel)}" fill="${parcelColor(parcel)}" fill-opacity="${opacity}" />
          ${showLabel ? `<text x="${centroid.x.toFixed(1)}" y="${centroid.y.toFixed(1)}">${cropShort}</text>` : ""}
        </g>
      `;
    })
    .join("");

  const lgndMarkup = state.activeLayers.lgnd
    ? visibleParcels
        .filter((parcel) => parcelEpochState(parcel).stressScore >= 45)
        .map((parcel) => {
          const temporal = parcelEpochState(parcel);
          const centroid = polygonCentroid(parcel.geometry);
          const radius = 28 + temporal.stressScore * 0.34;
          return `
        <g class="lgnd-hotspot" data-parcel="${parcel.id}">
          <circle cx="${centroid.x.toFixed(1)}" cy="${centroid.y.toFixed(1)}" r="${radius.toFixed(1)}" />
          <text x="${centroid.x.toFixed(1)}" y="${(centroid.y - radius - 8).toFixed(1)}">Similar chip queue</text>
        </g>
      `;
        })
        .join("")
    : "";

  const samMarkup = state.activeLayers.sam
    ? state.userParcels
        .map((parcel) => {
          const selected = parcel.id === state.selectedParcelId ? "selected" : "";
          const published = "published";
          const centroid = polygonCentroid(parcel.geometry);
          return `
        <g class="sam-candidate ${selected} ${published}" data-parcel="${parcel.id}">
          <polygon points="${projectedPolygon(parcel)}" />
          <text x="${centroid.x.toFixed(1)}" y="${(centroid.y + 24).toFixed(1)}">${published ? "SAM OK" : "SAM QC"}</text>
        </g>
      `;
        })
        .join("")
    : "";

  const gtMarkup = state.activeLayers.gt && tab.id !== "lgnd"
    ? data.groundTruth
        .map((point) => {
          const projected = projectLonLat(point.lon, point.lat);
          return `
        <g class="gt-point ${point.id === selectedParcel().validation ? "selected" : ""}" data-gt="${point.id}">
          <circle cx="${projected.x.toFixed(1)}" cy="${projected.y.toFixed(1)}" r="10" />
          <text x="${(projected.x + 14).toFixed(1)}" y="${(projected.y + 4).toFixed(1)}">${point.id}</text>
        </g>
      `;
        })
        .join("")
    : "";

  const procurementMarkup = state.activeLayers.procurement && tab.id !== "lgnd"
    ? data.procurementCenters
        .map((center) => {
          const projected = projectLonLat(center.lon, center.lat);
          return `
        <g class="procurement-point">
          <rect x="${(projected.x - 10).toFixed(1)}" y="${(projected.y - 10).toFixed(1)}" width="20" height="20" />
          <text x="${(projected.x + 16).toFixed(1)}" y="${(projected.y + 5).toFixed(1)}">${center.name}</text>
        </g>
      `;
        })
        .join("")
    : "";

  svg.innerHTML = `
    <rect width="${mapViewBox.width}" height="${mapViewBox.height}" fill="rgba(255, 255, 255, 0.04)" />
    <rect class="boundary" x="20" y="20" width="${mapViewBox.width - 40}" height="${mapViewBox.height - 40}" rx="18" />
    ${visibleParcels.length ? "" : `<text class="map-empty-state" x="500" y="303">Use the boundary annotation tool to save parcels</text>`}
    ${lgndMarkup}
    ${parcelMarkup}
    ${samMarkup}
    ${gtMarkup}
    ${procurementMarkup}
  `;

  svg.querySelectorAll(".parcel-group").forEach((group) => {
    group.addEventListener("click", () => {
      state.selectedParcelId = group.dataset.parcel;
      state.selectedPanel = "parcel";
      state.samPrompts = [];
      state.samCandidateReady = false;
      state.samQcAccepted = false;
      state.samSuggestions = [];
      state.selectedSamMaskId = null;
      state.selectedSamMaskIds = [];
      state.samBackendNote = "";
      renderMap();
      renderParcelDetails();
      renderSamWorkflow();
      const parcel = selectedParcel();
      const temporal = parcelEpochState(parcel);
      showToast(`${parcel.id} selected: ${temporal.cropClass}, ${temporal.confidence}% confidence, ${temporal.stress} stress.`);
    });
  });

  svg.querySelectorAll(".gt-point").forEach((point) => {
    point.addEventListener("click", () => {
      const parcel = data.parcels.find((candidate) => candidate.validation === point.dataset.gt);
      if (parcel) {
        state.selectedParcelId = parcel.id;
        state.selectedPanel = "field";
        renderMap();
        renderParcelDetails();
      }
    });
  });
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 3600);
}

function highlightSurface(element) {
  if (!element) {
    return;
  }
  document.querySelectorAll(".surface-highlight").forEach((target) => target.classList.remove("surface-highlight"));
  window.clearTimeout(state.highlightTimer);
  element.classList.add("surface-highlight");
  state.highlightTimer = window.setTimeout(() => {
    element.classList.remove("surface-highlight");
  }, 2400);
}

function syncEpochSlider() {
  const slider = document.querySelector("#epochSlider");
  if (slider) {
    slider.value = String(state.epochIndex);
  }
}

function applyReviewerStep(stepId) {
  const step = data.reviewerSteps.find((item) => item.id === stepId);
  if (!step) {
    return;
  }

  state.activeReviewerStep = step.id;
  if (step.layers) {
    Object.entries(step.layers).forEach(([layerId, isActive]) => {
      if (layerId in state.activeLayers) {
        state.activeLayers[layerId] = isActive;
      }
    });
  }
  if (Number.isInteger(step.epochIndex)) {
    state.epochIndex = step.epochIndex;
  }
  if (step.parcelId) {
    state.selectedParcelId = step.parcelId;
    if (data.parcels.some((parcel) => parcel.id === step.parcelId)) {
      state.samSourceParcelId = step.parcelId;
    }
  }
  if (step.panel) {
    state.selectedPanel = step.panel;
  }

  renderReviewerMode();
  renderLayerControls();
  renderLegend();
  renderMap();
  renderParcelDetails();
  syncEpochSlider();

  const target = document.getElementById(step.target);
  if (target) {
    target.scrollIntoView({ behavior: "smooth", block: "center" });
    highlightSurface(target);
  }
  showToast(`${step.step}. ${step.title}`);
}

function openRequirementDrawer(section) {
  const requirement = requirementById(section);
  if (!requirement) {
    showToast(`No curated Section 12 mapping found for ${section}.`);
    return;
  }

  state.selectedRequirementId = section;
  document.querySelector("#drawerEyebrow").textContent = `RFP ${requirement.section} | pages ${requirement.pages}`;
  document.querySelector("#drawerTitle").textContent = requirement.title;
  document.querySelector("#drawerBody").innerHTML = `
    <div class="drawer-status-row">
      <span class="status-pill status-${requirement.status}">${titleCase(requirement.status)}</span>
      <span>${requirement.evidenceType}</span>
    </div>
    <section>
      <h3>Requirement summary</h3>
      <p>${requirement.summary}</p>
    </section>
    <section>
      <h3>Matching demo surface</h3>
      <p>${requirement.demoSurface}</p>
    </section>
    <section>
      <h3>Demo proof</h3>
      <p>${requirement.evidence}</p>
    </section>
    <section>
      <h3>Source note</h3>
      <p>${requirement.sourceExcerpt}</p>
      <a href="../rfp/section12.md" target="_blank" rel="noopener">Open rfp/section12.md</a>
    </section>
  `;

  document.querySelector("#requirementOverlay").hidden = false;
  const drawer = document.querySelector("#requirementDrawer");
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  document.querySelector("#drawerClose").focus();
}

function closeRequirementDrawer() {
  state.selectedRequirementId = null;
  document.querySelector("#requirementOverlay").hidden = true;
  const drawer = document.querySelector("#requirementDrawer");
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
}

function setupControls() {
  const slider = document.querySelector("#epochSlider");
  slider.addEventListener("input", (event) => {
    state.epochIndex = Number(event.target.value);
    renderMap();
  });

  document.addEventListener(
    "click",
    (event) => {
      const requirementTarget = event.target.closest("[data-requirement]");
      if (!requirementTarget) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      openRequirementDrawer(requirementTarget.dataset.requirement);
    },
    true
  );

  document.querySelector("#reviewerSteps").addEventListener("click", (event) => {
    const step = event.target.closest("[data-reviewer-step]");
    if (step) {
      applyReviewerStep(step.dataset.reviewerStep);
    }
  });

  document.querySelector("#reviewerSteps").addEventListener("keydown", (event) => {
    const step = event.target.closest("[data-reviewer-step]");
    if (step && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      applyReviewerStep(step.dataset.reviewerStep);
    }
  });

  document.querySelector("#requirementOverlay").addEventListener("click", closeRequirementDrawer);
  document.querySelector("#drawerClose").addEventListener("click", closeRequirementDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeRequirementDrawer();
    }
  });

  document.querySelectorAll(".export-action").forEach((button) => {
    button.addEventListener("click", () => {
      showToast(`${button.dataset.export} export requested for crop, stress, yield, GT, LGND, and claim layers.`);
    });
  });

  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedPanel = button.dataset.panel;
      renderParcelDetails();
    });
  });
}

async function boot() {
  data = await loadDemoData();
  if (!data) {
    throw new Error("Dashboard data could not be loaded from the backend or static fallback.");
  }
  initializeState();
  state.lgndStatus = await loadLgndStatus();
  state.mlValidation = await loadMlArtifact("mlValidation", "/api/ml/validation");
  state.mlPredictions = await loadMlArtifact("mlPredictions", "/api/ml/predictions");
  renderStaticSurfaceBadges();
  renderProductTabs();
  renderProductFocus();
  renderLayerControls();
  renderMetrics();
  renderHeroMetrics();
  renderLegend();
  renderMapModeControls();
  renderMap();
  renderParcelDetails();
  renderProcurement();
  renderEvidence();
  renderMlCapabilities();
  renderMlValidation();
  renderLgndFlow();
  renderSamWorkflow();
  renderFieldFeed();
  renderCompliance();
  renderReports();
  renderMobileFlow();
  renderIntegrations();
  syncEpochSlider();
  setupControls();
  window.addEventListener("resize", renderMap);

  // Deep-link to a tab: ?tab=parcel|sentinel|lgnd
  const requestedTab = new URLSearchParams(window.location.search).get("tab");
  if (requestedTab && productTabs.some((tab) => tab.id === requestedTab)) {
    applyProductTab(requestedTab, false);
  }
}

boot().catch((error) => {
  console.error(error);
  document.body.innerHTML = `
    <main class="app-shell">
      <section class="detail-panel">
        <p class="eyebrow">Backend unavailable</p>
        <h1>Dashboard data could not be loaded</h1>
        <p class="muted-text">Start the backend with <code>python3 backend/server.py</code>, or open the app with app/data.js available.</p>
      </section>
    </main>
  `;
});
