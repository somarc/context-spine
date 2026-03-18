#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_EMBED=0

usage() {
  cat <<'EOF'
Usage: refresh.sh [--with-embed] [--no-embed]

Refresh QMD retrieval for repo-local Context Spine surfaces.
By default this runs lexical refresh only (`qmd update`).
Use `--with-embed` when you want to attempt vector hydration explicitly.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-embed)
      RUN_EMBED=1
      shift
      ;;
    --no-embed)
      RUN_EMBED=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "$RUN_EMBED" -eq 1 ]]; then
  bash "$ROOT/scripts/context-spine/qmd-refresh.sh" --embed
else
  bash "$ROOT/scripts/context-spine/qmd-refresh.sh"
fi
