#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import mimetypes
import os
import re
from io import BytesIO
from urllib.error import HTTPError, URLError
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
RFP_DIR = ROOT_DIR / "rfp"
TILE_DIR = ROOT_DIR / "backend" / "tiles"
MODEL_DIR = ROOT_DIR / "backend" / "models"
SAM_CHECKPOINT = MODEL_DIR / "sam_vit_b_01ec64.pth"
# ML artifacts: freshly generated outputs (gitignored data/) take priority, with
# committed seed/ copies as the out-of-the-box fallback. See backend/scripts/.
GENERATED_DATA_DIR = ROOT_DIR / "backend" / "data" / "generated"
SEED_DATA_DIR = ROOT_DIR / "backend" / "seed"


def load_env_file(path: Path) -> None:
  if not path.is_file():
    return
  for raw_line in path.read_text().splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
      continue
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")
    if key and key not in os.environ:
      os.environ[key] = value


load_env_file(ROOT_DIR / ".env")

PORT = int(os.environ.get("PORT", "5173"))
LGND_API_BASE = os.environ.get("LGND_API_BASE", "https://embeddings.api.lgnd.ai/v1")
LGND_TOKEN_ENV = "LGND_TOKEN"
SAM_PREDICTOR = None
SAM_RUNTIME = None


def load_demo_data() -> dict:
  text = (APP_DIR / "data.js").read_text()
  match = re.search(r"const UPAHAR_DEMO_DATA = (\{.*?\});\n\nif", text, re.S)
  if not match:
    raise RuntimeError("Could not locate UPAHAR_DEMO_DATA in app/data.js")

  object_literal = match.group(1)
  json_text = re.sub(
    r"([\{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:",
    lambda item: f'{item.group(1)}"{item.group(2)}":',
    object_literal,
  )
  return json.loads(json_text)


DEMO_DATA = load_demo_data()


def parcel_geojson() -> dict:
  features = []
  for parcel in DEMO_DATA["parcels"]:
    properties = {key: value for key, value in parcel.items() if key != "geometry"}
    features.append(
      {
        "type": "Feature",
        "id": parcel["id"],
        "properties": properties,
        "geometry": {
          "type": "Polygon",
          "coordinates": [parcel["geometry"] + [parcel["geometry"][0]]],
        },
      }
    )
  return {"type": "FeatureCollection", "name": "upahar_demo_parcels", "features": features}


def point_geojson(name: str, points: list[dict]) -> dict:
  features = []
  for point in points:
    properties = {key: value for key, value in point.items() if key not in {"lon", "lat"}}
    features.append(
      {
        "type": "Feature",
        "id": point["id"],
        "properties": properties,
        "geometry": {"type": "Point", "coordinates": [point["lon"], point["lat"]]},
      }
    )
  return {"type": "FeatureCollection", "name": name, "features": features}


def polygon_bounds(points: list[list[float]]) -> tuple[float, float, float, float]:
  lons = [point[0] for point in points]
  lats = [point[1] for point in points]
  return min(lons), min(lats), max(lons), max(lats)


def polygon_centroid(points: list[list[float]]) -> tuple[float, float]:
  return (
    sum(point[0] for point in points) / len(points),
    sum(point[1] for point in points) / len(points),
  )


def scale_polygon(points: list[list[float]], scale: float) -> list[list[float]]:
  center_lon, center_lat = polygon_centroid(points)
  return [
    [
      center_lon + (lon - center_lon) * scale,
      center_lat + (lat - center_lat) * scale,
    ]
    for lon, lat in points
  ]


def chip_points(points: list[list[float]], bounds: tuple[float, float, float, float]) -> list[list[float]]:
  min_lon, min_lat, max_lon, max_lat = bounds
  pad_lon = (max_lon - min_lon) * 0.34 or 0.001
  pad_lat = (max_lat - min_lat) * 0.34 or 0.001
  left = min_lon - pad_lon
  right = max_lon + pad_lon
  bottom = min_lat - pad_lat
  top = max_lat + pad_lat
  return [
    [
      round(48 + ((lon - left) / (right - left)) * 544, 1),
      round(312 - ((lat - bottom) / (top - bottom)) * 264, 1),
    ]
    for lon, lat in points
  ]


def chip_points_to_geometry(points: list[list[float]], bounds: tuple[float, float, float, float]) -> list[list[float]]:
  min_lon, min_lat, max_lon, max_lat = bounds
  pad_lon = (max_lon - min_lon) * 0.34 or 0.001
  pad_lat = (max_lat - min_lat) * 0.34 or 0.001
  left = min_lon - pad_lon
  right = max_lon + pad_lon
  bottom = min_lat - pad_lat
  top = max_lat + pad_lat
  return [
    [
      round(left + ((x - 48) / 544) * (right - left), 7),
      round(bottom + ((312 - y) / 264) * (top - bottom), 7),
    ]
    for x, y in points
  ]


def image_points_to_geometry(points: list[list[float]], bounds: tuple[float, float, float, float]) -> list[list[float]]:
  """Map chip image pixels (0..640 x, 0..360 y, y down) to lon/lat using chip bounds."""
  left, bottom, right, top = bounds
  return [
    [
      round(left + (x / 640.0) * (right - left), 7),
      round(top - (y / 360.0) * (top - bottom), 7),
    ]
    for x, y in points
  ]


def lon_lat_to_global_pixel(lon: float, lat: float, zoom: int, tile_size: int) -> tuple[float, float]:
  scale = 2 ** zoom
  lat_rad = math.radians(lat)
  x = ((lon + 180) / 360) * scale * tile_size
  y = ((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2) * scale * tile_size
  return x, y


def fetch_tile_image(epoch_ident: str, z: int, y: int, x: int):
  from PIL import Image

  tile_path = ensure_local_tile(epoch_ident, str(z), str(y), str(x), "png")
  return Image.open(tile_path).convert("RGB")


def ensure_local_tile(epoch_ident: str, z: str, y: str, x: str, ext: str) -> Path:
  tile_path = safe_path(TILE_DIR, epoch_ident, z, y, f"{x}.{ext}")
  if tile_path and tile_path.is_file():
    return tile_path

  fallback = remote_tile_url(epoch_ident, z, y, x)
  if not fallback:
    raise RuntimeError(f"No tile source for epoch {epoch_ident}")
  if tile_path is None:
    raise RuntimeError("Unsafe tile path")

  tile_path.parent.mkdir(parents=True, exist_ok=True)
  # Esri World Imagery rejects the default urllib User-Agent, so set a browser UA.
  request = Request(fallback, headers={"User-Agent": "Mozilla/5.0 (UpaharDemoBackend)"})
  with urlopen(request, timeout=30) as response:
    body = response.read()
  tile_path.write_bytes(body)
  return tile_path


def render_chip_at(center_lon: float, center_lat: float, span_lon: float, span_lat: float, epoch_ident: str):
  """Render a 640x360 imagery chip centered anywhere, from the basemap tile source."""
  from PIL import Image

  zoom = int(DEMO_DATA["basemap"]["zoom"])
  tile_size = int(DEMO_DATA["basemap"]["tileSize"])
  chip_width = 640
  chip_height = 360
  # Match the chip's ground aspect to its pixel aspect (16:9) so the imagery is
  # never stretched: degrees of longitude cover fewer metres than latitude.
  cos_lat = max(0.01, math.cos(math.radians(center_lat)))
  span_lat = span_lon * cos_lat * (chip_height / chip_width)
  left = center_lon - span_lon / 2
  right = center_lon + span_lon / 2
  bottom = center_lat - span_lat / 2
  top = center_lat + span_lat / 2

  global_left, global_top = lon_lat_to_global_pixel(left, top, zoom, tile_size)
  global_right, global_bottom = lon_lat_to_global_pixel(right, bottom, zoom, tile_size)
  start_x = math.floor(global_left / tile_size)
  end_x = math.floor(global_right / tile_size)
  start_y = math.floor(global_top / tile_size)
  end_y = math.floor(global_bottom / tile_size)
  origin_x = start_x * tile_size
  origin_y = start_y * tile_size

  mosaic = Image.new("RGB", ((end_x - start_x + 1) * tile_size, (end_y - start_y + 1) * tile_size))
  for ty in range(start_y, end_y + 1):
    for tx in range(start_x, end_x + 1):
      tile = fetch_tile_image(epoch_ident, zoom, ty, tx)
      mosaic.paste(tile, ((tx - start_x) * tile_size, (ty - start_y) * tile_size))

  crop = mosaic.crop(
    (
      int(global_left - origin_x),
      int(global_top - origin_y),
      int(global_right - origin_x),
      int(global_bottom - origin_y),
    )
  )
  chip = crop.resize((chip_width, chip_height))
  return chip, (left, bottom, right, top)


def render_tile_chip(parcel: dict, epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None):
  min_lon, min_lat, max_lon, max_lat = polygon_bounds(parcel["geometry"])
  default_center_lon, default_center_lat = polygon_centroid(parcel["geometry"])
  chip_center_lon = center_lon if center_lon is not None else default_center_lon
  chip_center_lat = center_lat if center_lat is not None else default_center_lat
  span_lon = max((max_lon - min_lon) * 1.68, 0.006)
  span_lat = max((max_lat - min_lat) * 1.68, 0.0034)
  return render_chip_at(chip_center_lon, chip_center_lat, span_lon, span_lat, epoch_ident)


def get_sam_predictor():
  global SAM_PREDICTOR, SAM_RUNTIME
  if SAM_PREDICTOR is not None:
    return SAM_PREDICTOR, SAM_RUNTIME
  if not SAM_CHECKPOINT.is_file():
    raise RuntimeError(f"SAM checkpoint not found at {SAM_CHECKPOINT}")

  import torch
  from segment_anything import SamPredictor, sam_model_registry

  if torch.cuda.is_available():
    device = "cuda"
  elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    device = "mps"
  else:
    device = "cpu"

  sam = sam_model_registry["vit_b"](checkpoint=str(SAM_CHECKPOINT))
  sam.to(device=device)
  SAM_PREDICTOR = SamPredictor(sam)
  SAM_RUNTIME = {"device": device, "checkpoint": str(SAM_CHECKPOINT), "modelType": "vit_b"}
  return SAM_PREDICTOR, SAM_RUNTIME


SAM_AUTO_GENERATOR = None
SAM_AUTO_RUNTIME = None


def get_sam_auto_generator():
  global SAM_AUTO_GENERATOR, SAM_AUTO_RUNTIME
  if SAM_AUTO_GENERATOR is not None:
    return SAM_AUTO_GENERATOR, SAM_AUTO_RUNTIME
  if not SAM_CHECKPOINT.is_file():
    raise RuntimeError(f"SAM checkpoint not found at {SAM_CHECKPOINT}")

  from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

  # The automatic generator hits a float64 op that Apple MPS rejects, so it runs
  # on CPU (its own model instance, separate from the MPS prompted predictor).
  sam = sam_model_registry["vit_b"](checkpoint=str(SAM_CHECKPOINT))
  sam.to(device="cpu")
  # Fewer sample points keeps CPU latency reasonable for a live demo while still
  # finding every sizable field in the chip.
  SAM_AUTO_GENERATOR = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=12,
    pred_iou_thresh=0.84,
    stability_score_thresh=0.88,
    min_mask_region_area=700,
  )
  SAM_AUTO_RUNTIME = {
    "device": "cpu",
    "checkpoint": str(SAM_CHECKPOINT),
    "modelType": "vit_b",
    "note": "automatic generation pinned to CPU (MPS float64 limitation)",
  }
  return SAM_AUTO_GENERATOR, SAM_AUTO_RUNTIME


def _mask_to_polygon(segmentation, bounds):
  from rasterio.features import shapes as raster_shapes
  from shapely.geometry import shape as to_shape

  binary = segmentation.astype("uint8")
  polygons = [
    to_shape(geometry)
    for geometry, value in raster_shapes(binary, mask=binary.astype(bool))
    if value == 1
  ]
  if not polygons:
    return None, None
  polygon = max(polygons, key=lambda item: item.area)
  tolerance = max(2.0, 0.008 * polygon.length)
  simplified = polygon.simplify(tolerance, preserve_topology=True)
  if simplified.is_empty or simplified.geom_type != "Polygon":
    return None, None
  points = [[round(float(x), 1), round(float(y), 1)] for x, y in list(simplified.exterior.coords)[:-1]]
  if len(points) < 3:
    return None, None
  return points, image_points_to_geometry(points, bounds)


def run_sam_auto_on_chip(parcel: dict, epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None, limit: int = 16) -> dict:
  """Automatic mask generation: segment every probable field in the chip viewport."""
  import numpy as np

  generator, runtime = get_sam_auto_generator()
  chip, bounds = render_tile_chip(parcel, epoch_ident, center_lon, center_lat)
  image = np.array(chip)
  raw_masks = generator.generate(image)

  chip_area = float(image.shape[0] * image.shape[1])
  candidates = []
  for item in raw_masks:
    fraction = float(item.get("area", 0)) / chip_area
    # Drop slivers and the whole-image background mask.
    if fraction < 0.004 or fraction > 0.62:
      continue
    points, geometry = _mask_to_polygon(item["segmentation"], bounds)
    if not points:
      continue
    candidates.append(
      {
        "area": float(item.get("area", 0)),
        "score": round(float(item.get("predicted_iou", 0.0)), 3),
        "stability": round(float(item.get("stability_score", 0.0)), 3),
        "chipPoints": points,
        "geometry": geometry,
      }
    )

  candidates.sort(key=lambda candidate: candidate["area"], reverse=True)
  masks = [
    {
      "id": f"{parcel['id']}-auto-{index + 1}",
      "label": f"Field {index + 1}",
      "score": candidate["score"],
      "stability": candidate["stability"],
      "source": "segment-anything-automatic",
      "chipPoints": candidate["chipPoints"],
      "geometry": candidate["geometry"],
    }
    for index, candidate in enumerate(candidates[:limit])
  ]
  return {"runtime": runtime, "masks": masks}


def sam_auto_suggestions(parcel_id: str, epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> Optional[dict]:
  parcel = resolve_chip_parcel(parcel_id, center_lon, center_lat)
  try:
    result = run_sam_auto_on_chip(parcel, epoch_ident, center_lon, center_lat)
    if not result["masks"]:
      raise RuntimeError("Automatic generation returned no field-sized masks")
    return {
      "parcelId": parcel_id,
      "epochId": epoch_ident,
      "mode": "automatic",
      "model": {
        "name": "Segment Anything ViT-B (automatic)",
        "mode": "backend-auto-mask-generation",
        "note": f"SAM segmented {len(result['masks'])} candidate field boundaries across the chip using {result['runtime']['device']}.",
        **result["runtime"],
      },
      "tileSource": {
        "backend": f"/api/tiles/{quote(epoch_ident)}/{DEMO_DATA['basemap']['zoom']}/{{y}}/{{x}}.png",
        "localTileCache": str(TILE_DIR),
      },
      "masks": result["masks"],
    }
  except Exception as error:
    # Fall back to prompted suggestions so the tab still demonstrates the flow.
    fallback = sam_mask_suggestions(parcel_id, [], epoch_ident, center_lon, center_lat) or {}
    fallback["mode"] = "automatic-fallback"
    model = fallback.get("model", {})
    model["note"] = f"Automatic SAM unavailable ({error}); returned deterministic demo masks."
    fallback["model"] = model
    return fallback


def run_sam_on_tile_chip(parcel: dict, prompts: list[dict], epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> dict:
  import numpy as np
  from rasterio.features import shapes as raster_shapes
  from shapely.geometry import shape as to_shape

  predictor, runtime = get_sam_predictor()
  chip, bounds = render_tile_chip(parcel, epoch_ident, center_lon, center_lat)
  image = np.array(chip)
  predictor.set_image(image)

  parcel_chip_points = chip_points(parcel["geometry"], bounds)
  xs = [point[0] for point in parcel_chip_points]
  ys = [point[1] for point in parcel_chip_points]
  box = np.array([min(xs), min(ys), max(xs), max(ys)], dtype=np.float32)

  point_prompts = [prompt for prompt in prompts if prompt.get("kind") == "point"]
  point_coords = None
  point_labels = None
  if point_prompts:
    point_coords = np.array([[float(prompt["x"]), float(prompt["y"])] for prompt in point_prompts], dtype=np.float32)
    point_labels = np.ones(len(point_prompts), dtype=np.int32)

  masks, scores, _ = predictor.predict(
    point_coords=point_coords,
    point_labels=point_labels,
    box=box,
    multimask_output=True,
  )

  suggestions = []
  for index, mask in enumerate(masks):
    binary = mask.astype("uint8")
    if int(binary.sum()) == 0:
      continue
    # Vectorize the mask without OpenCV: rasterio gives pixel-space polygons,
    # shapely simplifies them (Douglas-Peucker, like approxPolyDP).
    polygons = [
      to_shape(geometry)
      for geometry, value in raster_shapes(binary, mask=binary.astype(bool))
      if value == 1
    ]
    if not polygons:
      continue
    polygon = max(polygons, key=lambda item: item.area)
    tolerance = max(2.0, 0.01 * polygon.length)
    simplified = polygon.simplify(tolerance, preserve_topology=True)
    if simplified.is_empty or simplified.geom_type != "Polygon":
      continue
    exterior = list(simplified.exterior.coords)[:-1]
    points = [[round(float(x), 1), round(float(y), 1)] for x, y in exterior]
    if len(points) < 3:
      continue
    suggestions.append(
      {
        "id": f"{parcel['id']}-sam-{index + 1}",
        "label": f"SAM mask {index + 1}",
        "score": round(float(scores[index]), 3),
        "source": "segment-anything-vit-b",
        "chipPoints": points,
        "geometry": chip_points_to_geometry(points, bounds),
      }
    )

  if not suggestions:
    raise RuntimeError("SAM did not return polygon contours")

  return {
    "runtime": runtime,
    "masks": suggestions,
  }


def resolve_chip_parcel(parcel_id: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> dict:
  """Return the named parcel, or synthesize an AOI frame so SAM can run on the
  open imagery before any parcels exist (live-demo field creation)."""
  parcel = next((item for item in DEMO_DATA["parcels"] if item["id"] == parcel_id), None)
  if parcel:
    return parcel
  center = DEMO_DATA["basemap"]["center"]
  lon = center_lon if center_lon is not None else center["lon"]
  lat = center_lat if center_lat is not None else center["lat"]
  d_lon, d_lat = 0.0034, 0.0019
  return {
    "id": parcel_id or "AOI",
    "village": DEMO_DATA.get("insurer", {}).get("geography", "Pilot AOI"),
    "geometry": [
      [lon - d_lon, lat - d_lat],
      [lon + d_lon, lat - d_lat],
      [lon + d_lon, lat + d_lat],
      [lon - d_lon, lat + d_lat],
    ],
  }


def sam_mask_suggestions(parcel_id: str, prompts: list[dict], epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> Optional[dict]:
  parcel = resolve_chip_parcel(parcel_id, center_lon, center_lat)

  try:
    sam_result = run_sam_on_tile_chip(parcel, prompts, epoch_ident, center_lon, center_lat)
    return {
      "parcelId": parcel_id,
      "epochId": epoch_ident,
      "model": {
        "name": "Segment Anything ViT-B",
        "mode": "backend-tile-inference",
        "note": f"SAM ran on an imagery chip composed from backend tile source using {sam_result['runtime']['device']}.",
        **sam_result["runtime"],
      },
      "tileSource": {
        "backend": f"/api/tiles/{quote(epoch_ident)}/{DEMO_DATA['basemap']['zoom']}/{{y}}/{{x}}.png",
        "localTileCache": str(TILE_DIR),
      },
      "prompts": prompts,
      "masks": sam_result["masks"],
    }
  except Exception as error:
    fallback_error = str(error)

  geometry = parcel["geometry"]
  bounds = polygon_bounds(geometry)
  prompt_count = len(prompts)
  masks = []
  for index, scale in enumerate([1.0, 0.92, 1.08], start=1):
    mask_geometry = scale_polygon(geometry, scale)
    masks.append(
      {
        "id": f"{parcel_id}-sam-{index}",
        "label": ["Primary field edge", "Inner bund candidate", "Expanded edge candidate"][index - 1],
        "score": round(min(0.96, 0.78 + prompt_count * 0.04 - abs(1 - scale) * 0.25), 2),
        "source": "backend-tile-sam-suggestion",
        "chipPoints": chip_points(mask_geometry, bounds),
        "geometry": mask_geometry,
      }
    )

  tile_url = remote_tile_url(epoch_ident, str(DEMO_DATA["basemap"]["zoom"]), "auto", "auto")
  return {
    "parcelId": parcel_id,
    "epochId": epoch_ident,
    "model": {
      "name": "SAM/SamGeo backend adapter",
      "mode": "deterministic-demo-fallback",
      "note": f"Real SAM inference failed, so the backend returned deterministic demo masks. Error: {fallback_error}",
    },
    "tileSource": {
      "backend": f"/api/tiles/{quote(epoch_ident)}/{DEMO_DATA['basemap']['zoom']}/{{y}}/{{x}}.png",
      "fallback": tile_url,
      "localTileCache": str(TILE_DIR),
    },
    "prompts": prompts,
    "masks": masks,
  }


def epoch_id(epoch: dict, index: int) -> str:
  return str(epoch.get("id") or epoch.get("date") or index)


def data_with_backend_urls(host: str) -> dict:
  payload = dict(DEMO_DATA)
  payload["api"] = {
    "demoData": "/api/demo-data",
    "imageryMetadata": "/api/imagery/metadata",
    "parcelsGeoJson": "/api/geojson/parcels",
    "groundTruthGeoJson": "/api/geojson/ground-truth",
    "procurementGeoJson": "/api/geojson/procurement-centers",
    "tileTemplate": "/api/tiles/{epochId}/{z}/{y}/{x}.png",
    "lgndStatus": "/api/lgnd/status",
    "lgndTenants": "/api/lgnd/tenants",
    "lgndCollections": "/api/lgnd/collections",
    "lgndIndexes": "/api/lgnd/indexes",
    "lgndFilterByGeometry": "/api/lgnd/filter-by-geometry",
    "lgndSearchByLocation": "/api/lgnd/search-by-location",
    "lgndSearchChangedChips": "/api/lgnd/search-changed-chips",
    "mlPredictions": "/api/ml/predictions",
    "mlValidation": "/api/ml/validation",
    "parcelsExport": "/api/parcels/export",
    "similarFields": "/api/review/similar",
    "reviewChip": "/api/review/chip",
  }
  payload["basemap"] = {
    **DEMO_DATA["basemap"],
    "backendTileUrl": "/api/tiles/{epochId}/{z}/{y}/{x}.png",
    "backendOrigin": f"http://{host}",
  }
  return payload


def imagery_metadata(host: str) -> dict:
  payload = data_with_backend_urls(host)
  epochs = []
  for index, epoch in enumerate(payload["epochs"]):
    ident = epoch_id(epoch, index)
    epochs.append(
      {
        **epoch,
        "id": ident,
        "tileEndpoint": f"/api/tiles/{quote(ident)}/{{z}}/{{y}}/{{x}}.png",
      }
    )
  return {
    "basemap": payload["basemap"],
    "epochs": epochs,
    "notes": {
      "localTilePriority": "Tiles are stored under backend/tiles/<epoch-id>/<z>/<y>/<x>.png and served from disk.",
      "remoteFallback": "When no local tile exists, the backend downloads it from the configured Wayback source once, stores it, then serves the local file.",
      "mlUpdatePath": "Replace app/data.js or add file loaders for ML class, confidence, NDVI/EVI, stress, and SAM polygon outputs.",
    },
  }


def nisar_metadata() -> dict:
  return {
    "source": "NISAR SAR products via ASF/Earthdata, not a direct XYZ tile service",
    "demoRole": "Cloud/monsoon SAR fallback, flood/waterlogging signal, soil-moisture proxy, and temporal crop resilience feature input.",
    "rfpPositioning": {
      "supports": [
        "12.2.1 SAR fallback requirement",
        "12.2.6 crop health monitoring",
        "12.2.10 drought/dry-spell monitoring",
        "12.3 disaster and crop-loss monitoring",
      ],
      "doesNotReplace": "<=3 m optical imagery required for visual parcel/cadastral proof.",
    },
    "access": {
      "primary": "ASF Vertex and ASF Search Python package",
      "cloud": "NASA Earthdata Cloud / AWS S3",
      "auth": "NASA Earthdata Login required for download workflows.",
    },
    "productHandling": {
      "format": "HDF5 with CF/netCDF-compatible metadata structure",
      "qgisGdalHint": "Use .nc extension/workaround where GDAL needs netCDF-style spatial metadata recognition.",
      "tilePath": "Search/download product -> extract geocoded backscatter/coherence/soil-moisture layers -> normalize/render -> write backend/tiles/nisar-<date>/<z>/<y>/<x>.png.",
    },
    "candidateLayers": [
      "L-band backscatter",
      "S-band backscatter over India where available",
      "coherence/change layer",
      "soil-moisture product",
      "waterlogging/flood mask",
    ],
    "sources": [
      "https://science.nasa.gov/mission/nisar/data/",
      "https://nisar-docs.asf.alaska.edu/access-overview/",
      "https://nisar-docs.asf.alaska.edu/products-overview/",
      "https://nisar-docs.asf.alaska.edu/data-format/",
      "https://bhoonidhi.nrsc.gov.in/NISAR/",
    ],
  }


def load_ml_artifact(name: str) -> Optional[dict]:
  """Load a generated ML artifact, falling back to the committed seed copy."""
  for base in (GENERATED_DATA_DIR, SEED_DATA_DIR):
    path = base / name
    if path.is_file():
      try:
        payload = json.loads(path.read_text())
      except json.JSONDecodeError:
        continue
      payload.setdefault("meta", {})
      payload["meta"]["artifactPath"] = (
        "generated" if base == GENERATED_DATA_DIR else "seed"
      )
      return payload
  return None


def ml_predictions() -> dict:
  payload = load_ml_artifact("ml_predictions.json")
  if payload is None:
    return {
      "available": False,
      "note": "Run backend/scripts/ingest_sentinel2.py then run_ml_predictions.py.",
      "predictions": [],
    }
  payload["available"] = True
  return payload


def ml_validation() -> dict:
  payload = load_ml_artifact("ml_validation.json")
  if payload is None:
    return {"available": False, "note": "No validation artifact yet."}
  payload["available"] = True
  return payload


def parcels_export() -> dict:
  """Approved insured-parcel boundaries as GeoJSON for the ML aggregation step."""
  generated = GENERATED_DATA_DIR / "approved_parcels.geojson"
  if generated.is_file():
    try:
      return json.loads(generated.read_text())
    except json.JSONDecodeError:
      pass
  features = []
  for parcel in DEMO_DATA["parcels"]:
    geometry = parcel["geometry"]
    ring = geometry + [geometry[0]]
    features.append(
      {
        "type": "Feature",
        "id": parcel["id"],
        "properties": {
          "parcelId": parcel["id"],
          "village": parcel.get("village"),
          "block": parcel.get("village"),
          "areaHa": parcel.get("acreage"),
          "source": "curated-demo",
          "qcStatus": "demo-curated",
        },
        "geometry": {"type": "Polygon", "coordinates": [ring]},
      }
    )
  return {
    "type": "FeatureCollection",
    "name": "upahar_approved_parcels",
    "meta": {"featureCount": len(features), "source": "live-demo-fallback"},
    "features": features,
  }


def lgnd_configured() -> bool:
  return bool(os.environ.get(LGND_TOKEN_ENV))


def lgnd_status() -> dict:
  return {
    "configured": lgnd_configured(),
    "envVar": LGND_TOKEN_ENV,
    "baseUrl": LGND_API_BASE,
    "browserKeyExposure": "never",
    "supportedOperations": [
      "tenants",
      "collections",
      "indexes",
      "filter-by-geometry",
      "search-by-location",
      "search-changed-chips",
    ],
    "docs": "https://lgnd.ai/lgnd-docs",
  }


def lgnd_headers() -> dict:
  token = os.environ.get(LGND_TOKEN_ENV)
  if not token:
    raise RuntimeError(f"{LGND_TOKEN_ENV} is not configured")
  return {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
  }


def lgnd_request(method: str, path: str, payload: Optional[dict] = None, query: Optional[dict] = None) -> dict:
  query_string = ""
  if query:
    clean_query = {key: value for key, value in query.items() if value not in (None, "")}
    if clean_query:
      query_string = f"?{urlencode(clean_query)}"
  url = f"{LGND_API_BASE.rstrip('/')}/{path.lstrip('/')}{query_string}"
  body = json.dumps(payload).encode("utf-8") if payload is not None else None
  request = Request(url, data=body, method=method.upper(), headers=lgnd_headers())
  try:
    with urlopen(request, timeout=45) as response:
      response_body = response.read()
      if not response_body:
        return {"ok": True, "status": response.status, "data": None}
      try:
        data = json.loads(response_body.decode("utf-8"))
      except json.JSONDecodeError:
        data = response_body.decode("utf-8", errors="replace")
      return {"ok": True, "status": response.status, "data": data}
  except HTTPError as error:
    response_body = error.read()
    try:
      detail = json.loads(response_body.decode("utf-8")) if response_body else error.reason
    except json.JSONDecodeError:
      detail = response_body.decode("utf-8", errors="replace")
    return {"ok": False, "status": error.code, "error": detail}
  except URLError as error:
    return {"ok": False, "status": HTTPStatus.BAD_GATEWAY, "error": str(error.reason)}


LGND_DEFAULTS = None


def _collection_seed_point(collection: dict) -> tuple[float, float]:
  """A representative in-bounds lon/lat for a collection (centroid of vertices)."""
  def walk(node):
    if isinstance(node, (int, float)):
      return
    if len(node) == 2 and isinstance(node[0], (int, float)):
      yield node
      return
    for child in node:
      yield from walk(child)

  points = list(walk(collection.get("geometry", {}).get("coordinates", [])))
  if not points:
    return (2.3, 47.0)  # mainland France fallback
  lons = [point[0] for point in points]
  lats = [point[1] for point in points]
  return (sum(lons) / len(lons), sum(lats) / len(lats))


def lgnd_defaults() -> Optional[dict]:
  """Discover tenant, a Sentinel-2 collection, and its index once, server-side.

  Keeps tenant/collection/index plumbing out of the UI: the review tab only asks
  for similar fields. Prefers a Sentinel-2 collection (agricultural imagery).
  """
  global LGND_DEFAULTS
  if LGND_DEFAULTS is not None:
    return LGND_DEFAULTS
  if not lgnd_configured():
    return None
  tenants = lgnd_request("GET", "/tenants")
  if not tenants.get("ok"):
    return None
  tenant_list = tenants["data"].get("data", [])
  if not tenant_list:
    return None
  tenant_id = tenant_list[0]["id"]

  collections = lgnd_request("GET", f"/tenants/{tenant_id}/collections")
  collection_list = collections.get("data", {}).get("data", []) if collections.get("ok") else []
  ready = [item for item in collection_list if item.get("status") == "READY"] or collection_list
  if not ready:
    return None
  collection = next((item for item in ready if "sentinel" in item.get("name", "").lower()), ready[0])

  indexes = lgnd_request("GET", f"/tenants/{tenant_id}/collections/{collection['id']}/indexes")
  index_list = indexes.get("data", {}).get("data", []) if indexes.get("ok") else []
  ready_index = next((item for item in index_list if item.get("status") == "READY"), index_list[0] if index_list else None)
  if not ready_index:
    return None

  seed_lon, seed_lat = _collection_seed_point(collection)
  LGND_DEFAULTS = {
    "tenantId": tenant_id,
    "collectionId": collection["id"],
    "indexId": ready_index["id"],
    "collectionName": collection.get("name", ""),
    "seed": {"lon": round(seed_lon, 6), "lat": round(seed_lat, 6)},
  }
  return LGND_DEFAULTS


def similar_fields(lat: Optional[float] = None, lon: Optional[float] = None, limit: int = 9) -> dict:
  """Return visually similar field chips for a location, normalized for the UI."""
  config = lgnd_defaults()
  if config is None:
    return {"available": False, "results": [], "note": "Similar-field search is not configured."}

  if lat is None or lon is None:
    lat = config["seed"]["lat"]
    lon = config["seed"]["lon"]

  response = lgnd_request(
    "POST",
    f"/tenants/{config['tenantId']}/collections/{config['collectionId']}/search-by-location",
    {"indexId": config["indexId"], "latitude": lat, "longitude": lon, "limit": limit},
  )
  if not response.get("ok"):
    return {"available": False, "results": [], "note": "Similar-field search is temporarily unavailable."}

  results = []
  for item in response["data"].get("data", []):
    centroid = item.get("centroid", {}).get("coordinates")
    if not centroid:
      continue
    result_lon, result_lat = float(centroid[0]), float(centroid[1])
    results.append(
      {
        "id": item.get("chip_id"),
        "similarity": round(float(item.get("score", 0.0)) * 100),
        "date": (item.get("datetime") or "")[:10],
        "lon": round(result_lon, 6),
        "lat": round(result_lat, 6),
        "thumb": f"/api/review/chip?lon={result_lon}&lat={result_lat}",
      }
    )
  return {
    "available": True,
    "query": {"lat": round(lat, 6), "lon": round(lon, 6), "thumb": f"/api/review/chip?lon={lon}&lat={lat}"},
    "results": results,
  }


def remote_tile_url(epoch_ident: str, z: str, y: str, x: str) -> Optional[str]:
  for index, epoch in enumerate(DEMO_DATA["epochs"]):
    if epoch_id(epoch, index) == epoch_ident:
      return (
        DEMO_DATA["basemap"]["tileUrl"]
        .replace("{tileSet}", str(epoch["tileSet"]))
        .replace("{z}", z)
        .replace("{y}", y)
        .replace("{x}", x)
      )
  return None


def safe_path(base: Path, *parts: str) -> Optional[Path]:
  resolved = (base.joinpath(*parts)).resolve()
  try:
    resolved.relative_to(base.resolve())
  except ValueError:
    return None
  return resolved


class UpaharHandler(SimpleHTTPRequestHandler):
  server_version = "UpaharDemoBackend/0.1"

  def log_message(self, format: str, *args) -> None:
    print(f"{self.address_string()} - {format % args}")

  def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Cache-Control", "no-store")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    if self.command != "HEAD":
      self.wfile.write(body)

  def send_error_json(self, status: HTTPStatus, message: str) -> None:
    self.send_json({"error": message}, status)

  def send_png(self, image, cache: str = "no-store") -> None:
    body_io = BytesIO()
    image.save(body_io, format="PNG")
    body = body_io.getvalue()
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Type", "image/png")
    self.send_header("Cache-Control", cache)
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    if self.command != "HEAD":
      self.wfile.write(body)

  def do_GET(self) -> None:
    parsed = urlparse(self.path)
    path = unquote(parsed.path)

    if path == "/api/health":
      self.send_json({"ok": True, "service": "upahar-demo-backend", "runtime": "python"})
      return
    if path == "/api/demo-data":
      self.send_json(data_with_backend_urls(self.headers.get("Host", f"localhost:{PORT}")))
      return
    if path == "/api/imagery/metadata":
      self.send_json(imagery_metadata(self.headers.get("Host", f"localhost:{PORT}")))
      return
    if path == "/api/sar/nisar":
      self.send_json(nisar_metadata())
      return
    if path == "/api/ml/predictions":
      self.send_json(ml_predictions())
      return
    if path == "/api/ml/validation":
      self.send_json(ml_validation())
      return
    if path == "/api/parcels/export":
      self.send_json(parcels_export())
      return
    if path == "/api/lgnd/status":
      self.send_json(lgnd_status())
      return
    if path == "/api/lgnd/tenants":
      self.handle_lgnd_tenants()
      return
    if path == "/api/lgnd/collections":
      self.handle_lgnd_collections(parsed.query)
      return
    if path == "/api/lgnd/indexes":
      self.handle_lgnd_indexes(parsed.query)
      return
    if path == "/api/sam/chip":
      self.serve_sam_chip(parsed.query)
      return
    if path == "/api/review/similar":
      self.serve_similar_fields(parsed.query)
      return
    if path == "/api/review/chip":
      self.serve_review_chip(parsed.query)
      return
    if path == "/api/geojson/parcels":
      self.send_json(parcel_geojson())
      return
    if path == "/api/geojson/ground-truth":
      self.send_json(point_geojson("upahar_demo_ground_truth", DEMO_DATA["groundTruth"]))
      return
    if path == "/api/geojson/procurement-centers":
      self.send_json(point_geojson("upahar_demo_procurement_centers", DEMO_DATA["procurementCenters"]))
      return
    if path.startswith("/api/tiles/"):
      self.serve_tile(path)
      return

    self.serve_static(path)

  def do_HEAD(self) -> None:
    self.do_GET()

  def do_POST(self) -> None:
    parsed = urlparse(self.path)
    path = unquote(parsed.path)

    if path == "/api/sam/suggest":
      self.handle_sam_suggest()
      return
    if path == "/api/sam/auto":
      self.handle_sam_auto()
      return
    if path == "/api/lgnd/filter-by-geometry":
      self.handle_lgnd_filter_by_geometry()
      return
    if path == "/api/lgnd/search-by-location":
      self.handle_lgnd_search_by_location()
      return
    if path == "/api/lgnd/search-changed-chips":
      self.handle_lgnd_search_changed_chips()
      return

    self.send_error_json(HTTPStatus.NOT_FOUND, "Not found")

  def read_json_body(self) -> Optional[dict]:
    try:
      length = int(self.headers.get("Content-Length", "0"))
      body = self.rfile.read(length) if length > 0 else b"{}"
      payload = json.loads(body.decode("utf-8"))
      return payload if isinstance(payload, dict) else None
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
      return None

  def handle_sam_suggest(self) -> None:
    payload = self.read_json_body()
    if payload is None:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
      return

    parcel_id = str(payload.get("parcelId", ""))
    prompts = payload.get("prompts", [])
    epoch_ident = str(payload.get("epochId") or epoch_id(DEMO_DATA["epochs"][0], 0))
    center = payload.get("center", {})
    center_lon = center.get("lon") if isinstance(center, dict) else None
    center_lat = center.get("lat") if isinstance(center, dict) else None
    if not isinstance(prompts, list):
      self.send_error_json(HTTPStatus.BAD_REQUEST, "prompts must be an array")
      return

    result = sam_mask_suggestions(parcel_id, prompts, epoch_ident, center_lon, center_lat)
    if result is None:
      self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown parcel")
      return

    self.send_json(result)

  def handle_sam_auto(self) -> None:
    payload = self.read_json_body()
    if payload is None:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
      return

    parcel_id = str(payload.get("parcelId", ""))
    epoch_ident = str(payload.get("epochId") or epoch_id(DEMO_DATA["epochs"][0], 0))
    center = payload.get("center", {})
    center_lon = center.get("lon") if isinstance(center, dict) else None
    center_lat = center.get("lat") if isinstance(center, dict) else None

    result = sam_auto_suggestions(parcel_id, epoch_ident, center_lon, center_lat)
    if result is None:
      self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown parcel")
      return

    self.send_json(result)

  def require_lgnd_token(self) -> bool:
    if lgnd_configured():
      return True
    self.send_json(
      {
        "ok": False,
        "configured": False,
        "error": f"Set {LGND_TOKEN_ENV} in the backend environment before calling LGND.",
      },
      HTTPStatus.SERVICE_UNAVAILABLE,
    )
    return False

  def send_lgnd_result(self, result: dict) -> None:
    status = result.get("status", HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_GATEWAY)
    if isinstance(status, HTTPStatus):
      status = status.value
    status_code = HTTPStatus(status) if status in HTTPStatus._value2member_map_ else HTTPStatus.BAD_GATEWAY
    self.send_json(result, status_code)

  def handle_lgnd_tenants(self) -> None:
    if not self.require_lgnd_token():
      return
    self.send_lgnd_result(lgnd_request("GET", "/tenants"))

  def handle_lgnd_collections(self, query: str) -> None:
    if not self.require_lgnd_token():
      return
    tenant_id = parse_qs(query).get("tenantId", [""])[0]
    if not tenant_id:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "tenantId is required")
      return
    self.send_lgnd_result(lgnd_request("GET", f"/tenants/{quote(tenant_id)}/collections"))

  def handle_lgnd_indexes(self, query: str) -> None:
    if not self.require_lgnd_token():
      return
    params = parse_qs(query)
    tenant_id = params.get("tenantId", [""])[0]
    collection_id = params.get("collectionId", [""])[0]
    if not tenant_id or not collection_id:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "tenantId and collectionId are required")
      return
    self.send_lgnd_result(lgnd_request("GET", f"/tenants/{quote(tenant_id)}/collections/{quote(collection_id)}/indexes"))

  def handle_lgnd_filter_by_geometry(self) -> None:
    payload = self.read_json_body()
    if payload is None:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
      return
    if not self.require_lgnd_token():
      return
    tenant_id = str(payload.pop("tenantId", ""))
    collection_id = str(payload.pop("collectionId", ""))
    if not tenant_id or not collection_id:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "tenantId and collectionId are required")
      return
    if "geometry" not in payload:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "geometry is required")
      return
    self.send_lgnd_result(lgnd_request("POST", f"/tenants/{quote(tenant_id)}/collections/{quote(collection_id)}/filter-by-geometry", payload))

  def handle_lgnd_search_by_location(self) -> None:
    payload = self.read_json_body()
    if payload is None:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
      return
    if not self.require_lgnd_token():
      return
    tenant_id = str(payload.pop("tenantId", ""))
    collection_id = str(payload.pop("collectionId", ""))
    if not tenant_id or not collection_id:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "tenantId and collectionId are required")
      return
    if "latitude" not in payload or "longitude" not in payload:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "latitude and longitude are required")
      return
    self.send_lgnd_result(lgnd_request("POST", f"/tenants/{quote(tenant_id)}/collections/{quote(collection_id)}/search-by-location", payload))

  def handle_lgnd_search_changed_chips(self) -> None:
    payload = self.read_json_body()
    if payload is None:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
      return
    if not self.require_lgnd_token():
      return
    tenant_id = str(payload.pop("tenantId", ""))
    collection_id = str(payload.pop("collectionId", ""))
    if not tenant_id or not collection_id:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "tenantId and collectionId are required")
      return
    self.send_lgnd_result(lgnd_request("POST", f"/tenants/{quote(tenant_id)}/collections/{quote(collection_id)}/search-changed-chips", payload))

  def serve_sam_chip(self, query: str) -> None:
    params = parse_qs(query)
    parcel_id = params.get("parcelId", [""])[0]
    epoch_ident = params.get("epochId", [epoch_id(DEMO_DATA["epochs"][0], 0)])[0]
    center_lon = float(params["centerLon"][0]) if "centerLon" in params else None
    center_lat = float(params["centerLat"][0]) if "centerLat" in params else None
    parcel = resolve_chip_parcel(parcel_id, center_lon, center_lat)

    try:
      chip, _ = render_tile_chip(parcel, epoch_ident, center_lon, center_lat)
    except Exception as error:
      self.send_error_json(HTTPStatus.BAD_GATEWAY, f"Could not render imagery chip: {error}")
      return

    self.send_png(chip, cache="public, max-age=300")

  def serve_similar_fields(self, query: str) -> None:
    params = parse_qs(query)
    lat = float(params["lat"][0]) if "lat" in params else None
    lon = float(params["lon"][0]) if "lon" in params else None
    limit = int(params["limit"][0]) if "limit" in params else 9
    self.send_json(similar_fields(lat, lon, limit))

  def serve_review_chip(self, query: str) -> None:
    params = parse_qs(query)
    if "lon" not in params or "lat" not in params:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "lon and lat are required")
      return
    lon = float(params["lon"][0])
    lat = float(params["lat"][0])
    span = float(params["span"][0]) if "span" in params else 0.016
    epoch_ident = epoch_id(DEMO_DATA["epochs"][0], 0)
    try:
      chip, _ = render_chip_at(lon, lat, span, span * 0.5625, epoch_ident)
    except Exception as error:
      self.send_error_json(HTTPStatus.BAD_GATEWAY, f"Could not render chip: {error}")
      return
    self.send_png(chip, cache="public, max-age=600")

  def serve_tile(self, path: str) -> None:
    match = re.fullmatch(r"/api/tiles/([^/]+)/(\d+)/(\d+)/(\d+)\.(png|jpg|jpeg|webp)", path)
    if not match:
      self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid tile request")
      return

    epoch_ident, z, y, x, ext = match.groups()
    try:
      tile_path = ensure_local_tile(epoch_ident, z, y, x, ext)
      self.send_file(tile_path, cache="public, max-age=86400")
      return
    except RuntimeError as error:
      self.send_error_json(HTTPStatus.NOT_FOUND, str(error))
    except OSError as error:
      self.send_error_json(HTTPStatus.BAD_GATEWAY, f"Could not store tile: {error}")

  def serve_static(self, path: str) -> None:
    if path.startswith("/rfp/"):
      file_path = safe_path(RFP_DIR, path.removeprefix("/rfp/"))
    else:
      file_path = safe_path(APP_DIR, "index.html" if path == "/" else path.lstrip("/"))

    if not file_path or not file_path.is_file():
      self.send_error_json(HTTPStatus.NOT_FOUND, "Not found")
      return
    self.send_file(file_path, cache="no-store")

  def send_file(self, path: Path, cache: str) -> None:
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = path.read_bytes()
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Type", content_type)
    self.send_header("Cache-Control", cache)
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    if self.command != "HEAD":
      self.wfile.write(body)


def main() -> None:
  server = ThreadingHTTPServer(("127.0.0.1", PORT), UpaharHandler)
  print(f"Agri insurer demo backend listening on http://localhost:{PORT}")
  server.serve_forever()


if __name__ == "__main__":
  main()
