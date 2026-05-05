#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/runpod_install_rsync.sh

Installs rsync on the active RunPod using plain SSH. Use this before
scripts/runpod_sync.sh when a fresh pod does not have rsync installed yet.
Connection details are read from .env.
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

require_env() {
  local name="$1"
  local value="$2"
  if [[ -z "$value" ]]; then
    echo "Missing $name. Run scripts/configure_runpod_env.sh or set it in .env." >&2
    exit 2
  fi
}

main() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi
  if [[ $# -ne 0 ]]; then
    usage >&2
    exit 2
  fi

  load_env

  local host="${AI4AGRI_REMOTE_HOST:-}"
  local user="${AI4AGRI_REMOTE_USER:-root}"
  local port="${RUNPOD_SSH_PORT:-}"
  local key="${RUNPOD_SSH_KEY:-$HOME/.ssh/id_ed25519}"

  require_env AI4AGRI_REMOTE_HOST "$host"
  require_env RUNPOD_SSH_PORT "$port"

  ssh -p "$port" -i "$key" "${user}@${host}" 'bash -s' <<'REMOTE'
set -euo pipefail

wait_for_apt_locks() {
  local attempts=60
  local locks=(
    /var/lib/apt/lists/lock
    /var/lib/dpkg/lock
    /var/lib/dpkg/lock-frontend
  )
  for ((attempt = 1; attempt <= attempts; attempt++)); do
    local busy=0
    for lock in "${locks[@]}"; do
      if command -v fuser >/dev/null 2>&1 && fuser "$lock" >/dev/null 2>&1; then
        busy=1
      fi
    done
    if [[ "$busy" -eq 0 ]]; then
      return 0
    fi
    echo "waiting for apt/dpkg lock (${attempt}/${attempts})..." >&2
    sleep 5
  done
  echo "apt/dpkg lock did not clear after $((attempts * 5)) seconds" >&2
  ps -ef | grep -E "apt-get|apt |dpkg" | grep -v grep >&2 || true
  return 1
}

if command -v rsync >/dev/null 2>&1; then
  rsync --version | head -1
  exit 0
fi

wait_for_apt_locks
if ! apt-get update; then
  echo "apt-get update failed; disabling unreachable deadsnakes PPA entries and retrying." >&2
  for source in /etc/apt/sources.list.d/*deadsnakes*.list; do
    if [[ -f "$source" ]]; then
      mv "$source" "${source}.disabled"
      echo "disabled $source" >&2
    fi
  done
  wait_for_apt_locks
  apt-get update
fi

wait_for_apt_locks
apt-get install -y rsync
REMOTE
}

main "$@"
