#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/runpod_sync.sh push
  scripts/runpod_sync.sh pull-results
  scripts/runpod_sync.sh pull-inspection
  scripts/runpod_sync.sh pull PATH_ON_REMOTE PATH_ON_LOCAL

Environment overrides, usually from .env:
  AI4AGRI_REMOTE_HOST          default: 213.173.107.6
  AI4AGRI_REMOTE_USER          default: root
  RUNPOD_SSH_PORT              default: 34365
  RUNPOD_SSH_KEY               default: ~/.ssh/id_ed25519
  AI4AGRI_REMOTE_PROJECT_DIR   default: /workspace/ai4agri

Examples:
  scripts/runpod_sync.sh push
  scripts/runpod_sync.sh pull-results
  scripts/runpod_sync.sh pull /workspace/ai4agri/results/subtask1/inspection ./results/subtask1/
USAGE
}

load_env() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi
}

require_rsync() {
  if ! command -v rsync >/dev/null 2>&1; then
    echo "rsync is required locally. On Apple Silicon macOS: brew install rsync" >&2
    exit 1
  fi
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 2
  fi

  load_env
  require_rsync

  local action="$1"
  local host="${AI4AGRI_REMOTE_HOST:-213.173.107.6}"
  local user="${AI4AGRI_REMOTE_USER:-root}"
  local port="${RUNPOD_SSH_PORT:-34365}"
  local key="${RUNPOD_SSH_KEY:-$HOME/.ssh/id_ed25519}"
  local remote_project="${AI4AGRI_REMOTE_PROJECT_DIR:-/workspace/ai4agri}"
  local ssh_cmd="ssh -p ${port} -i ${key}"
  local remote="${user}@${host}"

  case "$action" in
    push)
      rsync -rtv --no-owner --no-group --no-perms \
        --exclude .git \
        --exclude .DS_Store \
        --exclude .env \
        --exclude .venv \
        --exclude __pycache__ \
        --exclude data \
        --exclude results/subtask1/baseline \
        --exclude results/subtask1/features \
        --exclude results/subtask1/submissions \
        --exclude results/subtask2/baseline \
        --exclude results/subtask2/features \
        --exclude results/subtask2/manifest.csv \
        --exclude results/subtask2/submissions \
        -e "$ssh_cmd" \
        ./ "${remote}:${remote_project}/"
      ;;
    pull-results)
      mkdir -p results
      rsync -rtv --no-owner --no-group --no-perms \
        -e "$ssh_cmd" \
        "${remote}:${remote_project}/results/" ./results/
      ;;
    pull-inspection)
      mkdir -p results/subtask1 results/subtask2
      rsync -rtv --no-owner --no-group --no-perms \
        -e "$ssh_cmd" \
        "${remote}:${remote_project}/results/subtask1/inspection/" ./results/subtask1/inspection/ || true
      rsync -rtv --no-owner --no-group --no-perms \
        -e "$ssh_cmd" \
        "${remote}:${remote_project}/results/subtask2/inspection/" ./results/subtask2/inspection/ || true
      ;;
    pull)
      if [[ $# -ne 3 ]]; then
        usage
        exit 2
      fi
      mkdir -p "$3"
      rsync -rtv --no-owner --no-group --no-perms \
        -e "$ssh_cmd" \
        "${remote}:$2" "$3"
      ;;
    *)
      usage
      exit 2
      ;;
  esac
}

main "$@"
