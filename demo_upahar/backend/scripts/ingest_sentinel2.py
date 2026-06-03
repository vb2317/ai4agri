#!/usr/bin/env python3
"""Sentinel-2 L2A ingestion for the MP agri-insurer demo (Next.md Section 5A, Tab 2).

This builds a per-parcel temporal artifact under
``backend/data/generated/sentinel2_parcels.json`` that the ML step
(``run_ml_predictions.py``) and the Sentinel-2 Intelligence tab consume.

Two modes:

* ``--mode demo`` (default): derive a deterministic temporal artifact from the
  existing demo parcels in ``app/data.js``. No network or credentials needed, so
  the downstream ML wiring can be exercised end to end before real imagery lands.
* ``--mode copernicus``: search Sentinel-2 L2A scenes through the Copernicus Data
  Space STAC API for the parcel AOI and season windows, pull the minimum band
  stack (B02/B03/B04/B08 + SCL, optional B05/B11), clip to each parcel, mask
  cloud/shadow with SCL, and compute NDVI/EVI/NDWI/NDRE/GCVI + seasonal summary
  features. This path needs Copernicus Data Space credentials (see notes below)
  and ``rasterio``; it is wired but expects VB to supply access + an AOI window.

The artifact schema is intentionally identical between modes so nothing
downstream needs to know which source produced it.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
GENERATED_DIR = BACKEND_DIR / "data" / "generated"
OUTPUT_PATH = GENERATED_DIR / "sentinel2_parcels.json"

# Reuse the canonical demo data + geometry helpers from the backend.
sys.path.insert(0, str(BACKEND_DIR))
from server import DEMO_DATA, polygon_bounds, polygon_centroid  # noqa: E402

# Copernicus Data Space STAC (used in --mode copernicus). Search is anonymous;
# asset download needs an OAuth token from the credentials below.
CDSE_STAC = "https://catalogue.dataspace.copernicus.eu/stac"
CDSE_TOKEN_URL = (
  "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
  "protocol/openid-connect/token"
)
S2_BANDS = ["B02", "B03", "B04", "B08"]
S2_OPTIONAL_BANDS = ["B05", "B11", "SCL"]
INDICES = ["ndvi", "evi", "ndwi", "ndre", "gcvi"]


def polygon_area_ha(points: list[list[float]]) -> float:
  """Approximate planar area in hectares for a small lon/lat polygon."""
  if len(points) < 3:
    return 0.0
  lat0 = sum(lat for _, lat in points) / len(points)
  m_per_deg_lat = 111320.0
  m_per_deg_lon = 111320.0 * math.cos(math.radians(lat0))
  area = 0.0
  for i in range(len(points)):
    lon1, lat1 = points[i]
    lon2, lat2 = points[(i + 1) % len(points)]
    area += (lon1 * m_per_deg_lon) * (lat2 * m_per_deg_lat)
    area -= (lon2 * m_per_deg_lon) * (lat1 * m_per_deg_lat)
  return round(abs(area) / 2.0 / 10000.0, 2)


def _seasonal_summary(series: list[dict]) -> dict:
  """Phenology + index summary features used by the ML step."""
  ndvi = [point["ndvi"] for point in series]
  dates = [point["date"] for point in series]
  peak_index = max(range(len(ndvi)), key=lambda i: ndvi[i])
  # Trapezoidal NDVI integral over evenly indexed epochs (unitless AUC proxy).
  auc = sum((ndvi[i] + ndvi[i + 1]) / 2 for i in range(len(ndvi) - 1))
  amplitude = max(ndvi) - min(ndvi)
  # Growing-season length proxy: epochs where NDVI exceeds the green-up midpoint.
  threshold = min(ndvi) + amplitude * 0.5
  active = [point["date"] for point in series if point["ndvi"] >= threshold]
  return {
    "ndviPeak": round(max(ndvi), 3),
    "ndviPeakDate": dates[peak_index],
    "ndviMin": round(min(ndvi), 3),
    "ndviAuc": round(auc, 3),
    "ndviAmplitude": round(amplitude, 3),
    "greenUpEpochs": len(active),
    "ndwiMin": round(min(point["ndwi"] for point in series), 3),
    "ndreMax": round(max(point["ndre"] for point in series), 3),
    "gcviMax": round(max(point["gcvi"] for point in series), 3),
    "lateSeasonDecline": round(max(ndvi) - ndvi[-1], 3),
  }


# --------------------------------------------------------------------------- #
# Demo mode: derive a temporal artifact from the existing curated parcels.
# --------------------------------------------------------------------------- #
def build_demo_series(parcel: dict, epochs: list[dict]) -> list[dict]:
  series = []
  states = parcel.get("epochStates") or []
  for index, epoch in enumerate(epochs):
    state = states[index] if index < len(states) else {}
    ndvi = float(state.get("ndvi", parcel["ndvi"][index] if index < len(parcel["ndvi"]) else 0.3))
    evi = float(state.get("evi", round(ndvi * 0.68, 3)))
    # Deterministic, index-consistent companions to NDVI/EVI for the demo.
    ndwi = round(0.42 - ndvi * 0.55, 3)            # wetter early, drier at canopy
    ndre = round(max(0.0, ndvi * 0.74 - 0.04), 3)  # red-edge tracks canopy N
    gcvi = round(max(0.0, ndvi * 6.2 - 0.6), 3)    # green chlorophyll vigor
    stress_score = float(state.get("stressScore", parcel.get("stressScore", 20)))
    # Cloud fraction proxy: monsoon mid-season is cloudier.
    cloud = round(min(38.0, 6.0 + index * 9.0 - (index == len(epochs) - 1) * 12.0), 1)
    series.append(
      {
        "date": epoch.get("date", str(index)),
        "label": epoch.get("label", f"epoch-{index}"),
        "cloudPct": max(2.0, cloud),
        "validPixelPct": round(100.0 - max(2.0, cloud), 1),
        "ndvi": round(ndvi, 3),
        "evi": round(evi, 3),
        "ndwi": ndwi,
        "ndre": ndre,
        "gcvi": gcvi,
        "stressScore": stress_score,
        "stateNote": state.get("stateNote", ""),
      }
    )
  return series


def build_demo_artifact() -> dict:
  epochs = DEMO_DATA["epochs"]
  parcels = []
  for parcel in DEMO_DATA["parcels"]:
    series = build_demo_series(parcel, epochs)
    parcels.append(
      {
        "id": parcel["id"],
        "village": parcel.get("village"),
        # Curated acreage is authoritative for the demo; the simplified polygon
        # under-measures. polygon_area_ha stays available for real cadastral input.
        "areaHa": parcel.get("acreage") or polygon_area_ha(parcel["geometry"]),
        "centroid": dict(zip(("lon", "lat"), polygon_centroid(parcel["geometry"]))),
        "weakLabel": parcel.get("crop"),
        "labelSource": "curated-demo (not field-verified)",
        "timeSeries": series,
        "summary": _seasonal_summary(series),
      }
    )
  return {
    "meta": {
      "source": "demo-synthetic",
      "note": (
        "Per-parcel temporal indices derived deterministically from curated demo "
        "parcels. Exercises the ML + UI pipeline before real Sentinel-2 ingestion."
      ),
      "aoi": DEMO_DATA["basemap"]["aoi"],
      "center": DEMO_DATA["basemap"]["center"],
      "season": "kharif-2025",
      "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "epochs": [
        {"label": epoch.get("label"), "date": epoch.get("date")} for epoch in epochs
      ],
      "bands": S2_BANDS,
      "indices": INDICES,
      "processingLevel": "L2A (target)",
    },
    "parcels": parcels,
  }


# --------------------------------------------------------------------------- #
# Copernicus mode: real STAC search + clip + index computation.
# --------------------------------------------------------------------------- #
def cdse_token() -> str:
  import os

  import requests

  user = os.environ.get("CDSE_USER")
  password = os.environ.get("CDSE_PASS")
  if not user or not password:
    raise RuntimeError(
      "Set CDSE_USER and CDSE_PASS (Copernicus Data Space login) for --mode copernicus."
    )
  response = requests.post(
    CDSE_TOKEN_URL,
    data={
      "client_id": "cdse-public",
      "grant_type": "password",
      "username": user,
      "password": password,
    },
    timeout=60,
  )
  response.raise_for_status()
  return response.json()["access_token"]


def search_scenes(bbox: list[float], date_range: str, max_cloud: float) -> list[dict]:
  import requests

  body = {
    "collections": ["SENTINEL-2"],
    "bbox": bbox,
    "datetime": date_range,
    "limit": 50,
    "query": {
      "productType": {"eq": "S2MSI2A"},
      "cloudCover": {"lte": max_cloud},
    },
  }
  response = requests.post(f"{CDSE_STAC}/search", json=body, timeout=90)
  response.raise_for_status()
  return response.json().get("features", [])


def build_copernicus_artifact(args: argparse.Namespace) -> dict:
  """Real ingestion path.

  Implemented against the Copernicus Data Space STAC + rasterio. It requires an
  AOI window (``--bbox``), a season date range, and CDSE credentials. The scene
  search runs anonymously; clipping/index math needs ``rasterio`` and a token to
  stream the band assets. VB owns the credentialed run; this keeps the code path
  honest rather than faking real imagery.
  """
  try:
    import rasterio  # noqa: F401
  except ImportError as error:  # pragma: no cover - depends on env
    raise RuntimeError("rasterio is required for --mode copernicus") from error

  if not args.bbox:
    raise RuntimeError(
      "Provide --bbox 'minLon minLat maxLon maxLat' for the MP pilot AOI."
    )
  bbox = [float(value) for value in args.bbox.split()]
  token = cdse_token()  # noqa: F841  (used by asset download once wired by VB)
  windows = args.windows.split(",") if args.windows else []
  if not windows:
    raise RuntimeError(
      "Provide --windows 'start/end,start/end,...' for early/mid/peak/late stages."
    )

  scenes_per_window = {window: search_scenes(bbox, window, args.max_cloud) for window in windows}
  found = {window: len(scenes) for window, scenes in scenes_per_window.items()}
  raise NotImplementedError(
    "Scene search wired (found per window: "
    f"{found}). Per-parcel asset clipping + index extraction is the remaining "
    "credentialed step for VB to run on the chosen AOI. See README 'Sentinel-2 "
    "ingestion'."
  )


def main() -> None:
  parser = argparse.ArgumentParser(description="Sentinel-2 ingestion for the agri-insurer demo")
  parser.add_argument("--mode", choices=["demo", "copernicus"], default="demo")
  parser.add_argument("--bbox", help="minLon minLat maxLon maxLat (copernicus mode)")
  parser.add_argument("--windows", help="comma-separated start/end date ranges (copernicus mode)")
  parser.add_argument("--max-cloud", type=float, default=35.0, dest="max_cloud")
  parser.add_argument("--out", type=Path, default=OUTPUT_PATH)
  args = parser.parse_args()

  if args.mode == "demo":
    artifact = build_demo_artifact()
  else:
    artifact = build_copernicus_artifact(args)

  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(artifact, indent=2))
  print(f"Wrote {len(artifact['parcels'])} parcels -> {args.out}")
  print(f"Source: {artifact['meta']['source']}")


if __name__ == "__main__":
  main()
