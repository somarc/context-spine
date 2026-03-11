#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="${CONTEXT_SPINE_SKILL_SOURCE:-$ROOT/.pi/skills/context-spine}"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="${CONTEXT_SPINE_SKILL_TARGET:-$CODEX_HOME_DIR/skills/context-spine}"
VALIDATOR="${CONTEXT_SPINE_SKILL_VALIDATOR:-$ROOT/scripts/context-spine/validate-codex-skill.py}"
VALIDATE_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --validate-only)
      VALIDATE_ONLY=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Skill source not found: $SOURCE_DIR" >&2
  exit 1
fi

if [[ -f "$VALIDATOR" ]]; then
  python3 "$VALIDATOR" "$SOURCE_DIR"
else
  echo "Validator not found at $VALIDATOR; skipping source validation."
fi

if [[ "$VALIDATE_ONLY" -eq 1 ]]; then
  echo "Validated skill source: $SOURCE_DIR"
  exit 0
fi

mkdir -p "$(dirname "$TARGET_DIR")"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "$SOURCE_DIR/" "$TARGET_DIR/"
else
  rm -rf "$TARGET_DIR"
  mkdir -p "$(dirname "$TARGET_DIR")"
  cp -R "$SOURCE_DIR" "$TARGET_DIR"
fi

if [[ -f "$VALIDATOR" ]]; then
  python3 "$VALIDATOR" "$TARGET_DIR"
fi

echo "Installed Codex skill to $TARGET_DIR"
