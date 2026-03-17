#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_config import load_config, resolve_repo_path
from memory_reconciliation import PROMOTION_STATUSES, normalize_refs, sanitize, write_reconciliation_trace
from run_state import finish_run, start_run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    config = load_config(repo_root)
    return resolve_repo_path(repo_root, str(config.get("memory_root", "meta/context-spine"))).resolve()


def record_promotion(
    repo_root: Path,
    memory_root: Path,
    *,
    summary: str,
    details: str = "",
    surface_kind: str = "durable-memory",
    files: str = "",
    refs: str = "",
    supersedes: str = "",
    tags: str = "",
    source: str = "codex",
    source_command: str = "context:promote",
    status: str = "promoted",
) -> dict:
    args = {
        "summary": summary,
        "details": details,
        "surface_kind": surface_kind,
        "files": files,
        "refs": refs,
        "supersedes": supersedes,
        "tags": tags,
        "source": source,
        "source_command": source_command,
        "status": status,
    }
    run_handle = start_run(repo_root, memory_root, "context:promote", args=args)

    try:
        superseded_refs = normalize_refs(repo_root, supersedes)
        trace = write_reconciliation_trace(
            repo_root,
            memory_root,
            run_handle,
            action="promote",
            summary=summary,
            details=details,
            source=source,
            source_command=source_command,
            status=status,
            files=files,
            refs=refs,
            tags=tags,
            extra={
                "surface_kind": surface_kind.strip() or "durable-memory",
                "supersedes": superseded_refs,
            },
        )
        finish_run(
            run_handle,
            status="success",
            summary=f"Recorded promotion for {len(trace['files'])} durable file(s).",
            artifacts=[trace["record_path"], trace["event_path"], *trace["files"]],
            extra={
                "record_id": trace["record_id"],
                "surface_kind": surface_kind.strip() or "durable-memory",
                "status": status,
                "supersedes": superseded_refs,
            },
        )
        return {
            "promotion_schema": "context-spine.promotion.v1",
            "run_id": run_handle.run_id,
            "run_path": run_handle.path,
            "surface_kind": surface_kind.strip() or "durable-memory",
            "status": status,
            "supersedes": superseded_refs,
            **trace,
        }
    except Exception as exc:
        finish_run(
            run_handle,
            status="failure",
            summary=f"Failed to record promotion: {exc}",
            extra={"surface_kind": surface_kind, "status": status},
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a durable promotion with explicit files, record, and event traces.")
    parser.add_argument("--summary", required=True, help="Short summary of what was promoted")
    parser.add_argument("--details", default="", help="Optional longer details")
    parser.add_argument("--kind", dest="surface_kind", default="durable-memory", help="Durable surface kind such as adr, runbook, or baseline")
    parser.add_argument("--files", required=True, help="Comma-separated repo file paths that were updated or created")
    parser.add_argument("--refs", default="", help="Comma-separated supporting evidence or source references")
    parser.add_argument("--supersedes", default="", help="Comma-separated refs or notes superseded by this promotion")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--source", default="codex", help="Who or what emitted the promotion")
    parser.add_argument("--source-command", default="context:promote", help="Workflow or command label")
    parser.add_argument("--status", default="promoted", choices=sorted(PROMOTION_STATUSES), help="Promotion status")
    parser.add_argument("--format", default="text", choices=["json", "text"], help="Output format")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    repo_root = default_repo_root()
    memory_root = (Path(args.root).expanduser() if args.root else default_memory_root(repo_root)).resolve()
    result = record_promotion(
        repo_root,
        memory_root,
        summary=args.summary,
        details=args.details,
        surface_kind=args.surface_kind,
        files=args.files,
        refs=args.refs,
        supersedes=args.supersedes,
        tags=args.tags,
        source=args.source,
        source_command=args.source_command,
        status=args.status,
    )

    if args.format == "json":
        print(json.dumps(sanitize(result), indent=2))
    else:
        print(f"Run ID: {result['run_id']}")
        print(f"Record: {result['record_path']}")
        print(f"Event: {result['event_path']}")
        print("Files:")
        for path in result["files"]:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
