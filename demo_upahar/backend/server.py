#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import mimetypes
import os
import re
from io import BytesIO
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import urlopen

ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
RFP_DIR = ROOT_DIR / "rfp"
TILE_DIR = ROOT_DIR / "backend" / "tiles"
MODEL_DIR = ROOT_DIR / "backend" / "models"
SAM_CHECKPOINT = MODEL_DIR / "sam_vit_b_01ec64.pth"
PORT = int(os.environ.get("PORT", "5173"))
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
  with urlopen(fallback, timeout=30) as response:
    body = response.read()
  tile_path.write_bytes(body)
  return tile_path


def render_tile_chip(parcel: dict, epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None):
  from PIL import Image

  zoom = int(DEMO_DATA["basemap"]["zoom"])
  tile_size = int(DEMO_DATA["basemap"]["tileSize"])
  chip_width = 640
  chip_height = 360
  min_lon, min_lat, max_lon, max_lat = polygon_bounds(parcel["geometry"])
  default_center_lon, default_center_lat = polygon_centroid(parcel["geometry"])
  chip_center_lon = center_lon if center_lon is not None else default_center_lon
  chip_center_lat = center_lat if center_lat is not None else default_center_lat
  span_lon = max((max_lon - min_lon) * 1.68, 0.006)
  span_lat = max((max_lat - min_lat) * 1.68, 0.0034)
  left = chip_center_lon - span_lon / 2
  right = chip_center_lon + span_lon / 2
  bottom = chip_center_lat - span_lat / 2
  top = chip_center_lat + span_lat / 2

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


def run_sam_on_tile_chip(parcel: dict, prompts: list[dict], epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> dict:
  import cv2
  import numpy as np

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
    contours, _ = cv2.findContours(mask.astype("uint8"), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
      continue
    contour = max(contours, key=cv2.contourArea)
    epsilon = max(2.0, 0.01 * cv2.arcLength(contour, True))
    approx = cv2.approxPolyDP(contour, epsilon, True)
    points = [[round(float(point[0][0]), 1), round(float(point[0][1]), 1)] for point in approx]
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


def sam_mask_suggestions(parcel_id: str, prompts: list[dict], epoch_ident: str, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> Optional[dict]:
  parcel = next((item for item in DEMO_DATA["parcels"] if item["id"] == parcel_id), None)
  if not parcel:
    return None

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
    if path == "/api/sam/chip":
      self.serve_sam_chip(parsed.query)
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

  def serve_sam_chip(self, query: str) -> None:
    params = parse_qs(query)
    parcel_id = params.get("parcelId", [""])[0]
    epoch_ident = params.get("epochId", [epoch_id(DEMO_DATA["epochs"][0], 0)])[0]
    center_lon = float(params["centerLon"][0]) if "centerLon" in params else None
    center_lat = float(params["centerLat"][0]) if "centerLat" in params else None
    parcel = next((item for item in DEMO_DATA["parcels"] if item["id"] == parcel_id), None)
    if parcel is None:
      self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown parcel")
      return

    try:
      chip, _ = render_tile_chip(parcel, epoch_ident, center_lon, center_lat)
    except Exception as error:
      self.send_error_json(HTTPStatus.BAD_GATEWAY, f"Could not render imagery chip: {error}")
      return

    self.send_png(chip, cache="public, max-age=300")

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
  print(f"UPAHAR demo backend listening on http://localhost:{PORT}")
  server.serve_forever()


if __name__ == "__main__":
  main()
