#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_BASE="$ROOT/meta/context-spine/evidence-packs"

job=""
log_file=""
summary=""

usage() {
  cat <<EOF
Usage:
  $0 --job <name> --log <log-file> [--summary <text>]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --job)
      job="$2"
      shift 2
      ;;
    --log)
      log_file="$2"
      shift 2
      ;;
    --summary)
      summary="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

[[ -n "$job" && -n "$log_file" ]] || { usage; exit 1; }
[[ -f "$log_file" ]] || { echo "Missing log file: $log_file" >&2; exit 1; }

date_dir="$(date '+%Y-%m-%d')"
out_dir="$OUT_BASE/$date_dir"
mkdir -p "$out_dir"
out_file="$out_dir/${job}.md"

extract_last() {
  local key="$1"
  grep -Eo "${key}:.*" "$log_file" | tail -n 1 | sed "s/^${key}:[[:space:]]*//" || true
}

decision="$(extract_last DECISION)"
evidence="$(extract_last EVIDENCE)"
files="$(extract_last FILES)"
next_actions="$(extract_last NEXT_ACTIONS)"
written="$(extract_last FILE_WRITTEN)"

if [[ -z "$summary" ]]; then
  summary="$(tail -n 40 "$log_file" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | cut -c1-300)"
fi

[[ -n "$decision" ]] || decision="TBD - add DECISION: in delegated prompt output"
[[ -n "$evidence" ]] || evidence="TBD - add EVIDENCE: with commands or links"
[[ -n "$files" ]] || files="TBD - add FILES: with paths"
[[ -n "$next_actions" ]] || next_actions="TBD - add NEXT_ACTIONS: as concise actions"

cat > "$out_file" <<EOF
# Evidence Pack: $job

- timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')
- log: $log_file

## Summary
- $summary

## Decision
- $decision

## Evidence
- $evidence

## Files
- $files

## Next Actions
- $next_actions

## Output Artifact
- ${written:-<none>}
EOF

echo "EVIDENCE_PACK:$out_file"
