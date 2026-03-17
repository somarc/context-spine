#!/usr/bin/env python3
import argparse
from pathlib import Path

from context_config import load_config, resolve_repo_path
from memory_events import EVENT_TYPES, write_event
from run_state import collect_git_snapshot


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a high-signal Context Spine event.")
    parser.add_argument("--type", required=True, choices=sorted(EVENT_TYPES), help="Event type")
    parser.add_argument("--summary", required=True, help="Short summary of what changed or was learned")
    parser.add_argument("--details", default="", help="Optional longer details")
    parser.add_argument("--source", default="codex", help="Who or what emitted the event")
    parser.add_argument("--source-command", default="", help="Optional command or workflow label")
    parser.add_argument("--status", default="", help="Optional status like success, fail, or updated")
    parser.add_argument("--files", default="", help="Comma-separated file paths touched or examined")
    parser.add_argument("--refs", default="", help="Comma-separated evidence or source references")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--session", default="", help="Related session identifier or title")
    parser.add_argument("--run-id", default="", help="Related Context Spine run id")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    repo_root = default_repo_root()
    config = load_config(repo_root)
    memory_root = (
        Path(args.root).expanduser()
        if args.root
        else resolve_repo_path(repo_root, str(config.get("memory_root", default_memory_root(repo_root))))
    ).resolve()

    event_path = write_event(
        memory_root,
        args.type,
        {
            "summary": args.summary,
            "details": args.details,
            "source": args.source,
            "source_command": args.source_command,
            "status": args.status,
            "files": split_csv(args.files),
            "refs": split_csv(args.refs),
            "tags": split_csv(args.tags),
            "session": args.session,
            "run_id": args.run_id,
            "git": collect_git_snapshot(repo_root),
        },
    )
    print(f"Event: {event_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
