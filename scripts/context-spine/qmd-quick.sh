#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MEM_ROOT="${CONTEXT_SPINE_ROOT:-$ROOT/meta/context-spine}"
COLLECTION="${CONTEXT_SPINE_COLLECTION:-context-spine-meta}"
QMD_QUERY="${CONTEXT_SPINE_QMD_QUERY:-priority todo decision action}"
QMD_QUERY_EXTRA="${CONTEXT_SPINE_QMD_QUERY_EXTRA:-evidence open questions source_of_truth}"
QMD_COLLECTIONS="${CONTEXT_SPINE_QMD_COLLECTIONS:-$COLLECTION}"
QMD_APPEND="${CONTEXT_SPINE_QMD_APPEND:-1}"
QMD_RETRIES="${CONTEXT_SPINE_QMD_RETRIES:-4}"
QMD_RETRY_SLEEP_SEC="${CONTEXT_SPINE_QMD_RETRY_SLEEP_SEC:-1}"
PACKAGE_JSON="$ROOT/package.json"

SESSIONS_DIR="$MEM_ROOT/sessions"
LATEST_SESSION=""
if [[ -d "$SESSIONS_DIR" ]]; then
  LATEST_SESSION="$(ls -1 "$SESSIONS_DIR"/*-session.md 2>/dev/null | sort | tail -n 1 || true)"
fi

if ! command -v qmd >/dev/null 2>&1; then
  echo "(qmd not found in PATH)"
  exit 0
fi

preferred_init_cmd() {
  if [[ -f "$PACKAGE_JSON" ]]; then
    echo "npm run context:init"
  else
    echo "bash ./scripts/context-spine/init-qmd.sh"
  fi
}

collection_exists() {
  local name="$1"
  qmd collection list | grep -Eq "^${name} \\(qmd://"
}

LOCAL_INDEX_DIR="$MEM_ROOT/.qmd"
LOCAL_INDEX_PATH="$LOCAL_INDEX_DIR/index.sqlite"
if [[ -z "${INDEX_PATH:-}" ]]; then
  mkdir -p "$LOCAL_INDEX_DIR"
  if [[ ! -f "$LOCAL_INDEX_PATH" ]]; then
    GLOBAL_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}"
    GLOBAL_INDEX_PATH="$GLOBAL_CACHE_DIR/qmd/index.sqlite"
    if [[ -f "$GLOBAL_INDEX_PATH" ]]; then
      for suffix in "" "-shm" "-wal"; do
        if [[ -f "$GLOBAL_INDEX_PATH$suffix" ]]; then
          cp "$GLOBAL_INDEX_PATH$suffix" "$LOCAL_INDEX_DIR/" 2>/dev/null || true
        fi
      done
    fi
  fi
  export INDEX_PATH="$LOCAL_INDEX_PATH"
fi

qmd_search_with_retry() {
  local query="$1"
  local collection="$2"
  local attempt=1
  local output=""
  local status=0
  while [[ "$attempt" -le "$QMD_RETRIES" ]]; do
    output="$(qmd search "$query" -c "$collection" -n 8 --files 2>&1)"
    status=$?
    if [[ "$status" -eq 0 ]]; then
      printf '%s\n' "$output"
      return 0
    fi
    if printf '%s' "$output" | grep -Eq "SQLITE_BUSY_RECOVERY|database is locked"; then
      echo "WARN: qmd index lock for collection '$collection' (attempt $attempt/$QMD_RETRIES)" >&2
      sleep $((QMD_RETRY_SLEEP_SEC * attempt))
      attempt=$((attempt + 1))
      continue
    fi
    if printf '%s' "$output" | grep -q "Collection not found"; then
      echo "HINT: run $(preferred_init_cmd) to register the collection." >&2
    fi
    printf '%s\n' "$output"
    return "$status"
  done
  printf '%s\n' "$output"
  return "$status"
}

append_block() {
  local session_file="$1"
  local block_file="$2"
  local tmp_file
  tmp_file="$(mktemp)"
  awk -v block_file="$block_file" '
    BEGIN { inserted=0 }
    {
      print $0
      if (!inserted && $0 ~ /^## QMD Triage/) {
        while ((getline line < block_file) > 0) {
          print line
        }
        close(block_file)
        inserted=1
      }
    }
    END {
      if (!inserted) {
        print ""
        print "## QMD Triage"
        while ((getline line < block_file) > 0) {
          print line
        }
        close(block_file)
      }
    }
  ' "$session_file" > "$tmp_file"
  mv "$tmp_file" "$session_file"
}

echo "===== QMD QUICK SEARCH ====="
IFS=',' read -r -a collections <<< "$QMD_COLLECTIONS"
missing_collection=0
for collection in "${collections[@]}"; do
  trimmed="$(echo "$collection" | sed 's/^ *//;s/ *$//')"
  if [[ -z "$trimmed" ]]; then
    continue
  fi
  if ! collection_exists "$trimmed"; then
    missing_collection=1
    break
  fi
done
if [[ "$missing_collection" -eq 1 ]]; then
  echo "INFO: missing QMD collection detected. Running $(preferred_init_cmd)"
  bash "$ROOT/scripts/context-spine/init-qmd.sh" >/dev/null || true
fi
session_has_qmd_link=0
if [[ -n "$LATEST_SESSION" && -f "$LATEST_SESSION" ]] && grep -q "qmd://" "$LATEST_SESSION"; then
  session_has_qmd_link=1
fi

for query in "$QMD_QUERY" "$QMD_QUERY_EXTRA"; do
  if [[ -z "$query" ]]; then
    continue
  fi
  echo "Query: $query"
  for collection in "${collections[@]}"; do
    trimmed="$(echo "$collection" | sed 's/^ *//;s/ *$//')"
    if [[ -z "$trimmed" ]]; then
      continue
    fi
    echo
    echo "Collection: $trimmed"
    search_output="$(qmd_search_with_retry "$query" "$trimmed" || true)"
    if [[ -n "$search_output" ]]; then
      printf '%s\n' "$search_output"
      if printf '%s' "$search_output" | grep -q "qmd://"; then
        session_has_qmd_link=1
      fi
    fi
    if [[ "$QMD_APPEND" != "0" && -n "$LATEST_SESSION" && -f "$LATEST_SESSION" ]]; then
      block_file="$(mktemp)"
      {
        echo ""
        echo "### QMD Quick Search - $(date +%F\ %T)"
        echo "- Query: $query"
        echo "- Collection: $trimmed"
        echo "- Results:"
        if [[ -n "$search_output" ]]; then
          printf '%s\n' "$search_output" | sed 's/^/  - /'
        else
          echo "  - (no results)"
        fi
      } > "$block_file"
      append_block "$LATEST_SESSION" "$block_file"
      rm -f "$block_file"
    fi
  done
  echo
done

if [[ "$QMD_APPEND" != "0" && -n "$LATEST_SESSION" && -f "$LATEST_SESSION" && "$session_has_qmd_link" -eq 0 ]]; then
  block_file="$(mktemp)"
  {
    echo ""
    echo "### QMD Link Guard - $(date +%F\ %T)"
    echo "- Required: add at least one concrete qmd:// hit to this session before close."
    echo "- Starter: qmd://$COLLECTION/"
  } > "$block_file"
  append_block "$LATEST_SESSION" "$block_file"
  rm -f "$block_file"
fi

echo "Tip: run retrieval before heavier repo-wide searches."
