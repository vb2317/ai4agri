#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${AI4AGRI_REMOTE_PROJECT_DIR:-/workspace/ai4agri}"
VENV_DIR="${AI4AGRI_VENV_DIR:-${PROJECT_DIR}/.venv}"

cd "$PROJECT_DIR"

if ! command -v rsync >/dev/null 2>&1; then
  apt-get update
  apt-get install -y rsync
fi

python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install git+https://github.com/MohammadElSakka/agripotential

python - <<'PY'
import sys
import torch

print("python", sys.version.split()[0])
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("cuda_device", torch.cuda.get_device_name(0))
PY

python scripts/validate_submission_zip.py --help >/dev/null
echo "RunPod bootstrap complete: ${PROJECT_DIR}"
