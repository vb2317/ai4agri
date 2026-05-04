#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${AI4AGRI_REMOTE_PROJECT_DIR:-/workspace/ai4agri}"

echo "== Host =="
hostname || true
date -u || true

echo
echo "== GPU =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader
else
  echo "nvidia-smi not found"
fi

echo
echo "== Disk =="
df -h /workspace "$PROJECT_DIR" 2>/dev/null || df -h

echo
echo "== Project Size =="
du -sh "$PROJECT_DIR" 2>/dev/null || true
du -sh "$PROJECT_DIR"/data "$PROJECT_DIR"/results 2>/dev/null || true

echo
echo "== Key Paths =="
find "$PROJECT_DIR" -maxdepth 2 -type d \
  \( -name data -o -name results -o -name scripts -o -name subtask1 -o -name subtask2 -o -name inspection -o -name submissions \) \
  -print 2>/dev/null | sort

echo
echo "== Python =="
if [[ -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  "$PROJECT_DIR/.venv/bin/python" - <<'PY'
import sys
print("python", sys.version.split()[0])
try:
    import torch
    print("torch", torch.__version__)
    print("cuda_available", torch.cuda.is_available())
except Exception as exc:
    print("torch_error", exc)
PY
else
  python3 --version || true
  echo ".venv not found at ${PROJECT_DIR}/.venv"
fi
