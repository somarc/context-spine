#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="${CONTEXT_SPINE_SKILL_SOURCE:-}"
SKILLS_ROOT="${CONTEXT_SPINE_SKILLS_SOURCE:-$ROOT/.pi/skills}"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET_ROOT="${CONTEXT_SPINE_SKILLS_TARGET:-$CODEX_HOME_DIR/skills}"
TARGET_DIR_OVERRIDE="${CONTEXT_SPINE_SKILL_TARGET:-}"
VALIDATOR="${CONTEXT_SPINE_SKILL_VALIDATOR:-$ROOT/scripts/context-spine/validate-codex-skill.py}"
VALIDATE_ONLY=0
VERIFY_INSTALLED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --validate-only)
      VALIDATE_ONLY=1
      shift
      ;;
    --verify-installed)
      VERIFY_INSTALLED=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

collect_skill_dirs() {
  if [[ -n "$SOURCE_DIR" ]]; then
    if [[ ! -d "$SOURCE_DIR" || ! -f "$SOURCE_DIR/SKILL.md" ]]; then
      echo "Skill source not found or invalid: $SOURCE_DIR" >&2
      exit 1
    fi
    printf '%s\n' "$SOURCE_DIR"
    return
  fi

  if [[ ! -d "$SKILLS_ROOT" ]]; then
    echo "Skills root not found: $SKILLS_ROOT" >&2
    exit 1
  fi

  while IFS= read -r dir; do
    [[ -f "$dir/SKILL.md" ]] || continue
    printf '%s\n' "$dir"
  done < <(find "$SKILLS_ROOT" -mindepth 1 -maxdepth 1 -type d | sort)
}

validate_skill_dir() {
  local skill_dir="$1"
  [[ -f "$VALIDATOR" ]] || { echo "Validator not found at $VALIDATOR" >&2; exit 1; }
  python3 "$VALIDATOR" "$skill_dir"
}

compare_skill_dirs() {
  local source_dir="$1"
  local target_dir="$2"
  [[ -f "$VALIDATOR" ]] || { echo "Validator not found at $VALIDATOR" >&2; exit 1; }
  python3 "$VALIDATOR" --compare "$source_dir" "$target_dir"
}

sync_skill_dir() {
  local source_dir="$1"
  local target_dir="$2"

  mkdir -p "$(dirname "$target_dir")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$source_dir/" "$target_dir/"
  else
    rm -rf "$target_dir"
    mkdir -p "$(dirname "$target_dir")"
    cp -R "$source_dir" "$target_dir"
  fi
}

mapfile -t SKILL_DIRS < <(collect_skill_dirs)

if [[ "${#SKILL_DIRS[@]}" -eq 0 ]]; then
  echo "No skill directories found under $SKILLS_ROOT" >&2
  exit 1
fi

if [[ -n "$TARGET_DIR_OVERRIDE" && "${#SKILL_DIRS[@]}" -ne 1 ]]; then
  echo "CONTEXT_SPINE_SKILL_TARGET can only be used when syncing a single skill." >&2
  exit 1
fi

for skill_dir in "${SKILL_DIRS[@]}"; do
  validate_skill_dir "$skill_dir"
done

if [[ "$VALIDATE_ONLY" -eq 1 ]]; then
  echo "Validated skill sources:"
  for skill_dir in "${SKILL_DIRS[@]}"; do
    echo " - $skill_dir"
  done
  exit 0
fi

if [[ "$VERIFY_INSTALLED" -eq 1 ]]; then
  echo "Verifying installed Codex skills:"
  for skill_dir in "${SKILL_DIRS[@]}"; do
    skill_name="$(basename "$skill_dir")"
    if [[ -n "$TARGET_DIR_OVERRIDE" ]]; then
      target_dir="$TARGET_DIR_OVERRIDE"
    else
      target_dir="$TARGET_ROOT/$skill_name"
    fi
    if [[ ! -d "$target_dir" ]]; then
      echo "Installed skill not found: $target_dir" >&2
      exit 1
    fi
    compare_skill_dirs "$skill_dir" "$target_dir"
  done
  exit 0
fi

mkdir -p "$TARGET_ROOT"
declare -a INSTALLED_TARGETS=()

for skill_dir in "${SKILL_DIRS[@]}"; do
  skill_name="$(basename "$skill_dir")"
  if [[ -n "$TARGET_DIR_OVERRIDE" ]]; then
    target_dir="$TARGET_DIR_OVERRIDE"
  else
    target_dir="$TARGET_ROOT/$skill_name"
  fi

  sync_skill_dir "$skill_dir" "$target_dir"
  validate_skill_dir "$target_dir"
  compare_skill_dirs "$skill_dir" "$target_dir"
  INSTALLED_TARGETS+=("$target_dir")
done

echo "Installed Codex skills:"
for target_dir in "${INSTALLED_TARGETS[@]}"; do
  echo " - $target_dir"
done
