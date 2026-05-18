#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

URL="http://localhost:5173"

if command -v python3 >/dev/null 2>&1; then
  echo "Starting UPAHAR demo at $URL"
  echo "Keep this window open while reviewing the app."
  echo "Press Control-C here to stop the demo server."
  open "$URL"
  python3 backend/server.py
else
  echo "Python 3 was not found. Opening the static preview instead."
  echo "The static preview is enough for visual review, but backend-only SAM/API features will be limited."
  open "$ROOT/app/index.html"
fi

