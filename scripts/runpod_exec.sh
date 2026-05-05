#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/runpod_exec.sh [--env-file PATH] 'COMMAND'
  scripts/runpod_exec.sh [--env-file PATH] --no-cd 'COMMAND'
  scripts/runpod_exec.sh 'COMMAND'
  scripts/runpod_exec.sh --no-cd 'COMMAND'

Runs a command on the current RunPod over SSH. By default the command starts in
AI4AGRI_REMOTE_PROJECT_DIR, which defaults to /workspace/ai4agri.

Examples:
  scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'
  scripts/runpod_exec.sh 'source .venv/bin/activate && python scripts/inspect_subtask1.py --splits train val test'
USAGE
}

load_env() {
  local env_file="${1:-.env}"
  if [[ -f "$env_file" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$env_file"
    set +a
  fi
}

quote_for_remote() {
  printf "%q" "$1"
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
  if [[ $# -lt 1 ]]; then
    usage
    exit 2
  fi
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi

  local use_cd=1
  local env_file=".env"
  if [[ "${1:-}" == "--env-file" ]]; then
    if [[ $# -lt 2 ]]; then
      usage
      exit 2
    fi
    env_file="$2"
    shift 2
  fi
  if [[ "${1:-}" == "--no-cd" ]]; then
    use_cd=0
    shift
  fi
  if [[ $# -ne 1 ]]; then
    usage
    exit 2
  fi

  load_env "$env_file"

  local host="${AI4AGRI_REMOTE_HOST:-}"
  local user="${AI4AGRI_REMOTE_USER:-root}"
  local port="${RUNPOD_SSH_PORT:-}"
  local key="${RUNPOD_SSH_KEY:-$HOME/.ssh/id_ed25519}"
  local remote_project="${AI4AGRI_REMOTE_PROJECT_DIR:-/workspace/ai4agri}"
  local command="$1"
  local remote_command

  require_env AI4AGRI_REMOTE_HOST "$host"
  require_env RUNPOD_SSH_PORT "$port"

  if [[ "$use_cd" -eq 1 ]]; then
    remote_command="cd $(quote_for_remote "$remote_project") && $command"
  else
    remote_command="$command"
  fi

  ssh -p "$port" -i "$key" "${user}@${host}" "$remote_command"
}

main "$@"
