#!/usr/bin/env python3
import argparse
import datetime as dt
from pathlib import Path


def default_memory_root() -> Path:
    return Path(__file__).resolve().parents[2] / "meta" / "context-spine"


def main():
    parser = argparse.ArgumentParser(description="Create a Context Spine session summary template.")
    parser.add_argument("--date", default="", help="Override date in YYYY-MM-DD")
    parser.add_argument("--project", default="project", help="Project name")
    parser.add_argument("--title", default="", help="Custom title")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    now = dt.datetime.now()
    date_str = args.date or now.strftime("%Y-%m-%d")
    title = args.title or f"{date_str} - Session Summary"

    memory_root = Path(args.root).expanduser() if args.root else default_memory_root()
    sessions_dir = memory_root / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    session_file = sessions_dir / f"{date_str}-session.md"
    if session_file.exists():
        raise SystemExit(f"Session file already exists: {session_file}")

    content = (
        "---\n"
        f"date: {date_str}\n"
        "type: context-spine-session\n"
        f"project: {args.project}\n"
        "tags: [context-spine, session]\n"
        "---\n\n"
        f"# {title}\n\n"
        "## QMD Triage\n"
        "- Required: add at least one `qmd://` link during the first retrieval pass.\n"
        "- Queries:\n"
        "  - \n"
        "- Top hits (qmd://...):\n"
        "  - \n"
        "- Notes:\n\n"
        "## Summary\n"
        "- \n\n"
        "## Current State\n"
        "- \n\n"
        "## Evidence\n"
        "- \n\n"
        "## Decisions\n"
        "- \n\n"
        "## Constraints / First Principles\n"
        "- \n\n"
        "## Files Touched\n"
        "- \n\n"
        "## Open Questions\n"
        "- \n\n"
        "## Next Actions\n"
        "- \n"
    )
    session_file.write_text(content, encoding="utf-8")
    print(f"Created session template at {session_file}")


if __name__ == "__main__":
    main()
