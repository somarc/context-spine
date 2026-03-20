#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_BOOTSTRAP=1
RUN_EMBED=0

usage() {
  cat <<'EOF'
Usage: setup.sh [--skip-bootstrap] [--with-embed] [--no-embed]

Fast first-time path for Context Spine:
  1. provision the project-scoped external vault
  2. wire repo-local QMD collections
  3. refresh lexical retrieval
  4. open the working set via bootstrap

Use `--with-embed` only when you want to attempt vector hydration explicitly.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-bootstrap)
      RUN_BOOTSTRAP=0
      shift
      ;;
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

echo "===== CONTEXT SETUP ====="
echo "Root: $ROOT"

echo "Durable notes: provisioning the project-scoped external vault"
bash "$ROOT/scripts/context-spine/init-vault.sh"

if command -v qmd >/dev/null 2>&1; then
  echo "Retrieval: configuring repo-local QMD collections and refreshing lexical search"
  if [[ "$RUN_EMBED" -eq 1 ]]; then
    bash "$ROOT/scripts/context-spine/refresh.sh" --with-embed
  else
    bash "$ROOT/scripts/context-spine/refresh.sh"
  fi
else
  echo "Retrieval: qmd not found; continuing without repo-local search"
  echo "Install qmd later, then rerun \`npm run context:setup\` or \`npm run context:refresh\`."
fi

if [[ "$RUN_BOOTSTRAP" -eq 1 ]]; then
  echo
  echo "Opening the working set..."
  bash "$ROOT/scripts/context-spine/bootstrap.sh"
fi
