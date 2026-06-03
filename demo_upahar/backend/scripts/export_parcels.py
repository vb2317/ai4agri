#!/usr/bin/env python3
"""Export approved parcel boundaries to GeoJSON (Next.md Section 5A, Tab 1).

The Parcel Creator publishes SAM-assisted boundaries that need to leave the
browser as a portfolio artifact. This writes a GeoJSON FeatureCollection with the
fields the parcel-level ML aggregation pipeline expects: parcel ID, village/block,
area, source, QC status, and timestamp.

Two inputs:

* default: the curated demo parcels from ``app/data.js`` (so there is always a
  valid export to feed the pipeline),
* ``--approved <file.json>``: a JSON array of approved parcels posted from the
  Parcel Creator tab (``id``, ``village``, ``acreage``, ``geometry``,
  ``annotation``), merged on top of the demo parcels.

The backend ``GET /api/parcels/export`` serves the same shape on demand.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
GENERATED_DIR = BACKEND_DIR / "data" / "generated"
OUTPUT_PATH = GENERATED_DIR / "approved_parcels.geojson"

sys.path.insert(0, str(BACKEND_DIR))
from server import DEMO_DATA  # noqa: E402


def parcel_feature(parcel: dict, qc_status: str, source: str) -> dict:
  geometry = parcel["geometry"]
  ring = geometry + [geometry[0]] if geometry and geometry[0] != geometry[-1] else geometry
  annotation = parcel.get("annotation", {})
  return {
    "type": "Feature",
    "id": parcel["id"],
    "properties": {
      "parcelId": parcel["id"],
      "village": parcel.get("village"),
      "block": parcel.get("block") or parcel.get("village"),
      "areaHa": parcel.get("acreage"),
      "source": source,
      "qcStatus": annotation.get("status", qc_status),
      "maskId": annotation.get("maskId"),
      "promptCount": annotation.get("promptCount"),
      "exportedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    },
    "geometry": {"type": "Polygon", "coordinates": [ring]},
  }


def build_collection(approved: list[dict] | None) -> dict:
  features = [
    parcel_feature(parcel, "demo-curated", "curated-demo")
    for parcel in DEMO_DATA["parcels"]
  ]
  if approved:
    features.extend(
      parcel_feature(parcel, "QC accepted", "sam-assisted + human QC")
      for parcel in approved
      if parcel.get("geometry")
    )
  return {
    "type": "FeatureCollection",
    "name": "upahar_approved_parcels",
    "meta": {
      "note": "Approved insured-parcel boundaries for the ML aggregation pipeline.",
      "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "featureCount": len(features),
    },
    "features": features,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description="Export approved parcel boundaries to GeoJSON")
  parser.add_argument("--approved", type=Path, help="JSON array of approved parcels from the Parcel Creator")
  parser.add_argument("--out", type=Path, default=OUTPUT_PATH)
  args = parser.parse_args()

  approved = None
  if args.approved and args.approved.is_file():
    approved = json.loads(args.approved.read_text())

  collection = build_collection(approved)
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(collection, indent=2))
  print(f"Wrote {collection['meta']['featureCount']} parcels -> {args.out}")


if __name__ == "__main__":
  main()
