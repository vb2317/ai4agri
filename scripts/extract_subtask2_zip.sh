#!/usr/bin/env bash
set -euo pipefail

DOWNLOAD_DIR="${1:-data/subtask2/downloads}"
EXTRACT_DIR="${2:-data/subtask2}"

if ! command -v unzip >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y unzip
  else
    echo "unzip is required. Install it, then rerun this script." >&2
    exit 1
  fi
fi

zip_path="$(find "$DOWNLOAD_DIR" -maxdepth 1 -type f -name '*.zip' | sort | head -n 1)"
if [[ -z "$zip_path" ]]; then
  echo "No ZIP found in ${DOWNLOAD_DIR}" >&2
  exit 1
fi

mkdir -p "$EXTRACT_DIR"
unzip -n "$zip_path" -d "$EXTRACT_DIR"
echo "Extracted ${zip_path} under ${EXTRACT_DIR}"
