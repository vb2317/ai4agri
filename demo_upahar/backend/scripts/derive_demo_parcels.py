#!/usr/bin/env python3
"""Derive realistic demo field boundaries from the AOI imagery via SAM.

The hand-authored demo parcels were crude hexagons that did not match the fields
under them. This runs SAM automatic mask generation over a wide chip at the AOI,
keeps field-sized, well-separated polygons, and prints them as lon/lat geometry +
area so they can replace the `geometry`/`acreage` of the parcels in app/data.js.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
from server import (  # noqa: E402
  DEMO_DATA,
  SAM_CHECKPOINT,
  _mask_to_polygon,
  epoch_id,
  render_chip_at,
)

CENTER_LON = float(DEMO_DATA["basemap"]["center"]["lon"])
CENTER_LAT = float(DEMO_DATA["basemap"]["center"]["lat"])
# Keep fields inside the map's framed extent (~1.4 km) so all parcels read clearly.
SPAN_LON = 0.013
SPAN_LAT = SPAN_LON * 0.5625


def polygon_area_ha(points: list[list[float]]) -> float:
  if len(points) < 3:
    return 0.0
  lat0 = sum(p[1] for p in points) / len(points)
  m_lat = 111320.0
  m_lon = 111320.0 * math.cos(math.radians(lat0))
  area = 0.0
  for i in range(len(points)):
    lon1, lat1 = points[i]
    lon2, lat2 = points[(i + 1) % len(points)]
    area += (lon1 * m_lon) * (lat2 * m_lat) - (lon2 * m_lon) * (lat1 * m_lat)
  return abs(area) / 2.0 / 10000.0


def centroid(points: list[list[float]]) -> tuple[float, float]:
  return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def main() -> None:
  import numpy as np
  from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

  # Denser sampling than the live endpoint, to find enough distinct fields to
  # cover every demo parcel (one-off offline derivation, so latency is fine).
  sam = sam_model_registry["vit_b"](checkpoint=str(SAM_CHECKPOINT))
  sam.to(device="cpu")
  generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=26,
    pred_iou_thresh=0.8,
    stability_score_thresh=0.85,
    min_mask_region_area=500,
  )
  epoch_ident = epoch_id(DEMO_DATA["epochs"][0], 0)
  chip, bounds = render_chip_at(CENTER_LON, CENTER_LAT, SPAN_LON, SPAN_LAT, epoch_ident)
  image = np.array(chip)
  raw = generator.generate(image)

  chip_area = float(image.shape[0] * image.shape[1])
  candidates = []
  for item in raw:
    fraction = float(item.get("area", 0)) / chip_area
    if fraction < 0.006 or fraction > 0.4:  # field-sized: not slivers, not the whole chip
      continue
    points, geometry = _mask_to_polygon(item["segmentation"], bounds)
    if not points or len(geometry) > 14:
      continue
    candidates.append({"geometry": geometry, "area": polygon_area_ha(geometry), "score": float(item.get("predicted_iou", 0))})

  # Prefer convincing field-sized polygons, then spread them out so parcels do not overlap.
  candidates.sort(key=lambda c: c["score"], reverse=True)
  chosen: list[dict] = []
  min_sep = SPAN_LON * 0.09
  for candidate in candidates:
    cx, cy = centroid(candidate["geometry"])
    if all(math.dist((cx, cy), centroid(c["geometry"])) > min_sep for c in chosen):
      chosen.append(candidate)
    if len(chosen) >= len(DEMO_DATA["parcels"]):
      break

  print(f"Found {len(candidates)} field candidates; selected {len(chosen)} for {len(DEMO_DATA['parcels'])} parcels.\n")
  out = []
  for parcel, candidate in zip(DEMO_DATA["parcels"], chosen):
    geometry = [[round(lon, 7), round(lat, 7)] for lon, lat in candidate["geometry"]]
    out.append({"id": parcel["id"], "acreage": round(candidate["area"], 1), "geometry": geometry})
    print(f"{parcel['id']}: {len(geometry)} pts, {candidate['area']:.1f} ha")
  Path("/tmp/derived_parcels.json").write_text(json.dumps(out, indent=2))
  print("\nWrote /tmp/derived_parcels.json")


if __name__ == "__main__":
  main()
