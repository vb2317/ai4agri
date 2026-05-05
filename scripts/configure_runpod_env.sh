#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/configure_runpod_env.sh --host HOST --port PORT [options]

Writes or updates local .env with the active RunPod connection details.
Run this whenever VB starts a new pod or SSH port changes.

Options:
  --host HOST                 Public SSH host or IP, required.
  --port PORT                 Public SSH port, required.
  --user USER                 SSH user, default: root.
  --key PATH                  SSH private key, default: ~/.ssh/id_ed25519.
  --project-dir PATH          Remote project dir, default: /workspace/ai4agri.
  --remote-data-dir PATH      Remote data dir, default: PROJECT_DIR/data.
  --remote-results-dir PATH   Remote results dir, default: PROJECT_DIR/results.
  --jupyter-url URL           Optional JupyterLab URL for notes.
  --pod-id ID                 Optional RunPod pod id for notes.
  --pod-name NAME             Optional human-friendly note.
  --test                      Test SSH after updating .env.

Example:
  scripts/configure_runpod_env.sh \
    --host 213.173.107.6 \
    --port 34365 \
    --pod-id vit08hc86csllk \
    --jupyter-url https://example-8888.proxy.runpod.net/lab
USAGE
}

quote_value() {
  local value="$1"
  printf "'%s'" "${value//\'/\'\\\'\'}"
}

upsert_env() {
  local key="$1"
  local value="$2"
  local file="$3"
  local quoted
  quoted="$(quote_value "$value")"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    awk -v key="$key" -v value="${key}=${quoted}" 'BEGIN{done=0} $0 ~ "^" key "=" {$0=value; done=1} {print} END{if(!done) print value}' "$file" > "${file}.tmp"
    mv "${file}.tmp" "$file"
  else
    printf "%s=%s\n" "$key" "$quoted" >> "$file"
  fi
}

main() {
  local host=""
  local port=""
  local user="root"
  local key="$HOME/.ssh/id_ed25519"
  local project_dir="/workspace/ai4agri"
  local data_dir=""
  local results_dir=""
  local jupyter_url=""
  local pod_id=""
  local pod_name=""
  local test_connection=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --host) host="$2"; shift 2 ;;
      --port) port="$2"; shift 2 ;;
      --user) user="$2"; shift 2 ;;
      --key) key="$2"; shift 2 ;;
      --project-dir) project_dir="$2"; shift 2 ;;
      --remote-data-dir|--data-dir) data_dir="$2"; shift 2 ;;
      --remote-results-dir|--results-dir) results_dir="$2"; shift 2 ;;
      --jupyter-url) jupyter_url="$2"; shift 2 ;;
      --pod-id) pod_id="$2"; shift 2 ;;
      --pod-name) pod_name="$2"; shift 2 ;;
      --test) test_connection=1; shift ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
  done

  if [[ -z "$host" || -z "$port" ]]; then
    usage >&2
    exit 2
  fi

  data_dir="${data_dir:-${project_dir}/data}"
  results_dir="${results_dir:-${project_dir}/results}"

  if [[ ! -f .env ]]; then
    cp .env.example .env
  fi

  upsert_env AI4AGRI_REMOTE_HOST "$host" .env
  upsert_env AI4AGRI_REMOTE_USER "$user" .env
  upsert_env RUNPOD_SSH_PORT "$port" .env
  upsert_env RUNPOD_SSH_KEY "$key" .env
  upsert_env AI4AGRI_REMOTE_PROJECT_DIR "$project_dir" .env
  upsert_env AI4AGRI_REMOTE_DATA_DIR "$data_dir" .env
  upsert_env AI4AGRI_REMOTE_RESULTS_DIR "$results_dir" .env
  upsert_env RUNPOD_JUPYTER_URL "$jupyter_url" .env
  upsert_env RUNPOD_POD_ID "$pod_id" .env
  upsert_env RUNPOD_POD_NAME "$pod_name" .env

  echo "Updated .env for RunPod host ${host}:${port}"
  echo "Test with: scripts/runpod_exec.sh 'bash scripts/runpod_status.sh'"
  if [[ "$test_connection" -eq 1 ]]; then
    scripts/runpod_exec.sh --no-cd 'hostname && pwd'
  fi
}

main "$@"
