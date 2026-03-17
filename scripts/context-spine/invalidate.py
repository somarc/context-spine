#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_config import load_config, resolve_repo_path
from memory_reconciliation import INVALIDATION_STATUSES, normalize_ref, sanitize, write_reconciliation_trace
from run_state import finish_run, start_run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    config = load_config(repo_root)
    return resolve_repo_path(repo_root, str(config.get("memory_root", "meta/context-spine"))).resolve()


def record_invalidation(
    repo_root: Path,
    memory_root: Path,
    *,
    summary: str,
    subject: str,
    details: str = "",
    replacement: str = "",
    files: str = "",
    refs: str = "",
    tags: str = "",
    source: str = "codex",
    source_command: str = "context:invalidate",
    status: str = "stale",
) -> dict:
    args = {
        "summary": summary,
        "subject": subject,
        "details": details,
        "replacement": replacement,
        "files": files,
        "refs": refs,
        "tags": tags,
        "source": source,
        "source_command": source_command,
        "status": status,
    }
    run_handle = start_run(repo_root, memory_root, "context:invalidate", args=args)

    try:
        normalized_replacement = normalize_ref(repo_root, replacement)
        trace = write_reconciliation_trace(
            repo_root,
            memory_root,
            run_handle,
            action="invalidate",
            summary=summary,
            details=details,
            source=source,
            source_command=source_command,
            status=status,
            files=files,
            refs=refs,
            tags=tags,
            extra={
                "subject": subject.strip(),
                "replacement": normalized_replacement,
            },
        )
        finish_run(
            run_handle,
            status="success",
            summary=f"Recorded invalidation for {len(trace['files'])} durable file(s).",
            artifacts=[trace["record_path"], trace["event_path"], *trace["files"]],
            extra={
                "record_id": trace["record_id"],
                "subject": subject.strip(),
                "replacement": normalized_replacement,
                "status": status,
            },
        )
        return {
            "invalidation_schema": "context-spine.invalidation.v1",
            "run_id": run_handle.run_id,
            "run_path": run_handle.path,
            "subject": subject.strip(),
            "replacement": normalized_replacement,
            "status": status,
            **trace,
        }
    except Exception as exc:
        finish_run(
            run_handle,
            status="failure",
            summary=f"Failed to record invalidation: {exc}",
            extra={"subject": subject, "status": status},
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Record an explicit invalidation with durable file, record, and event traces.")
    parser.add_argument("--summary", required=True, help="Short summary of what became stale or invalid")
    parser.add_argument("--subject", required=True, help="The assumption, note, or surface being invalidated")
    parser.add_argument("--details", default="", help="Optional longer details")
    parser.add_argument("--replacement", default="", help="Optional replacement surface, note, or ref")
    parser.add_argument("--files", required=True, help="Comma-separated repo file paths updated to reflect the invalidation")
    parser.add_argument("--refs", default="", help="Comma-separated supporting evidence or source references")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--source", default="codex", help="Who or what emitted the invalidation")
    parser.add_argument("--source-command", default="context:invalidate", help="Workflow or command label")
    parser.add_argument("--status", default="stale", choices=sorted(INVALIDATION_STATUSES), help="Invalidation status")
    parser.add_argument("--format", default="text", choices=["json", "text"], help="Output format")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    repo_root = default_repo_root()
    memory_root = (Path(args.root).expanduser() if args.root else default_memory_root(repo_root)).resolve()
    result = record_invalidation(
        repo_root,
        memory_root,
        summary=args.summary,
        subject=args.subject,
        details=args.details,
        replacement=args.replacement,
        files=args.files,
        refs=args.refs,
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
