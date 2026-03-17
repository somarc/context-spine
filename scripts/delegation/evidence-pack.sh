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

export CONTEXT_SPINE_ROOT="$ROOT"
export CONTEXT_SPINE_MEMORY_ROOT="$ROOT/meta/context-spine"
export CONTEXT_SPINE_EVIDENCE_JOB="$job"
export CONTEXT_SPINE_EVIDENCE_SUMMARY="$summary"
export CONTEXT_SPINE_EVIDENCE_LOG="$log_file"
export CONTEXT_SPINE_EVIDENCE_MD="$out_file"
export CONTEXT_SPINE_EVIDENCE_DECISION="$decision"
export CONTEXT_SPINE_EVIDENCE_EVIDENCE="$evidence"
export CONTEXT_SPINE_EVIDENCE_FILES="$files"
export CONTEXT_SPINE_EVIDENCE_NEXT="$next_actions"
export CONTEXT_SPINE_EVIDENCE_OUTPUT="${written:-<none>}"
record_path="$(python3 - <<'PY'
import datetime as dt
import os
import sys
from pathlib import Path

root = Path(os.environ["CONTEXT_SPINE_ROOT"])
sys.path.insert(0, str(root / "scripts" / "context-spine"))

from memory_records import write_record  # noqa: E402

memory_root = Path(os.environ["CONTEXT_SPINE_MEMORY_ROOT"])
path = write_record(
    memory_root,
    "evidence",
    {
        "layer": "evidence",
        "job": os.environ["CONTEXT_SPINE_EVIDENCE_JOB"],
        "summary": os.environ["CONTEXT_SPINE_EVIDENCE_SUMMARY"],
        "log_path": os.environ["CONTEXT_SPINE_EVIDENCE_LOG"],
        "markdown_path": os.environ["CONTEXT_SPINE_EVIDENCE_MD"],
        "decision": os.environ["CONTEXT_SPINE_EVIDENCE_DECISION"],
        "evidence": os.environ["CONTEXT_SPINE_EVIDENCE_EVIDENCE"],
        "files": os.environ["CONTEXT_SPINE_EVIDENCE_FILES"],
        "next_actions": os.environ["CONTEXT_SPINE_EVIDENCE_NEXT"],
        "output_artifact": os.environ["CONTEXT_SPINE_EVIDENCE_OUTPUT"],
    },
    record_id=f"evidence-{os.environ['CONTEXT_SPINE_EVIDENCE_JOB']}",
    recorded_at=dt.datetime.now(dt.UTC).replace(microsecond=0),
)
print(path)
PY
)"

echo "EVIDENCE_PACK:$out_file"
echo "EVIDENCE_RECORD:$record_path"
