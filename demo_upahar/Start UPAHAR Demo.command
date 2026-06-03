#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

URL="http://localhost:5173"

# Prefer the project venv (torch, segment_anything, rasterio, shapely) so the SAM
# backend runs real inference instead of the deterministic fallback.
VENV_PY="$ROOT/../.venv/bin/python"
if [ -x "$VENV_PY" ]; then
  PY="$VENV_PY"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
fi

if [ -n "$PY" ]; then
  echo "Starting UPAHAR demo at $URL"
  echo "Using Python: $PY"
  echo "Keep this window open while reviewing the app."
  echo "Press Control-C here to stop the demo server."
  open "$URL"
  "$PY" backend/server.py
else
  echo "Python 3 was not found. Opening the static preview instead."
  echo "The static preview is enough for visual review, but backend-only SAM/API features will be limited."
  open "$ROOT/app/index.html"
fi

