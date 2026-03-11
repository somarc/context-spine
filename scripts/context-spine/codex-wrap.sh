#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PREFLIGHT="${CONTEXT_SPINE_PREFLIGHT:-1}"

if [[ "$PREFLIGHT" != "0" && -x "$ROOT/scripts/context-spine/bootstrap.sh" ]]; then
  "$ROOT/scripts/context-spine/bootstrap.sh" || true
fi

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 -- <command> [args...]" >&2
  exit 1
fi

if [[ "$1" == "--" ]]; then
  shift
fi

exec "$@"
