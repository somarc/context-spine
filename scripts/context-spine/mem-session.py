#!/usr/bin/env python3
import argparse
import datetime as dt
import subprocess
from pathlib import Path


def default_memory_root() -> Path:
    return Path(__file__).resolve().parents[2] / "meta" / "context-spine"


def git_value(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def git_dirty_summary(cwd: Path) -> str:
    result = subprocess.run(["git", "status", "--short"], cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return "unknown"
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return "clean"
    return f"{len(lines)} changed path(s)"


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
    repo_root = memory_root.parents[2] if memory_root.name == "context-spine" and memory_root.parent.name == "meta" else memory_root
    sessions_dir = memory_root / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    session_file = sessions_dir / f"{date_str}-session.md"
    if session_file.exists():
        raise SystemExit(f"Session file already exists: {session_file}")

    branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    commit = git_value(["git", "rev-parse", "--short", "HEAD"], repo_root)
    dirty = git_dirty_summary(repo_root)

    content = (
        "---\n"
        f"date: {date_str}\n"
        "type: context-spine-session\n"
        f"project: {args.project}\n"
        "tags: [context-spine, session]\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Session Context\n"
        f"- Branch: `{branch}`\n"
        f"- HEAD: `{commit}`\n"
        f"- Worktree: `{dirty}`\n\n"
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
        "## Verification\n"
        "- Last command that proved something important:\n"
        "  - \n\n"
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
