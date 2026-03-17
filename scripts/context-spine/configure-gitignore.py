#!/usr/bin/env python3
import argparse
from pathlib import Path

from context_config import load_config


BEGIN_TEMPLATE = "# >>> context-spine gitignore (mode: {mode}) >>>"
END_MARKER = "# <<< context-spine gitignore <<<"

RULES = {
    "tracked": [
        "meta/context-spine/.qmd/",
        "meta/context-spine/events/",
        "meta/context-spine/runs/",
        "meta/context-spine/records/",
        "meta/context-spine/hot-memory-index.md",
        "meta/context-spine/memory-state.json",
        "meta/context-spine/memory-state.html",
        "meta/context-spine/memory-scorecard.md",
        "meta/context-spine/doctor-report.md",
        "meta/context-spine/doctor-report.json",
        "meta/context-spine/upgrade-report.md",
        "meta/context-spine/upgrade-report.json",
        "meta/context-spine/rollout-report.md",
        "meta/context-spine/rollout-report.json",
    ],
    "local": [
        "meta/context-spine/",
    ],
}

DESCRIPTIONS = {
    "tracked": "Commit durable and rolling Context Spine memory; ignore only generated local aids.",
    "local": "Keep repo-local Context Spine memory out of git; promote shared truth into committed docs and code.",
}


def render_block(mode: str) -> str:
    lines = [
        BEGIN_TEMPLATE.format(mode=mode),
        f"# {DESCRIPTIONS[mode]}",
        *RULES[mode],
        END_MARKER,
    ]
    return "\n".join(lines) + "\n"


def replace_block(content: str, block: str) -> str:
    begin_index = content.find("# >>> context-spine gitignore ")
    if begin_index == -1:
        if content and not content.endswith("\n"):
            content += "\n"
        if content and not content.endswith("\n\n"):
            content += "\n"
        return content + block

    end_index = content.find(END_MARKER, begin_index)
    if end_index == -1:
        raise ValueError("Found Context Spine gitignore block start without end marker.")

    end_index += len(END_MARKER)
    if end_index < len(content) and content[end_index] == "\n":
        end_index += 1
    return content[:begin_index] + block + content[end_index:]


def remove_block(content: str) -> str:
    begin_index = content.find("# >>> context-spine gitignore ")
    if begin_index == -1:
        return content

    end_index = content.find(END_MARKER, begin_index)
    if end_index == -1:
        raise ValueError("Found Context Spine gitignore block start without end marker.")

    end_index += len(END_MARKER)
    if end_index < len(content) and content[end_index] == "\n":
        end_index += 1
    updated = content[:begin_index] + content[end_index:]
    return updated.rstrip() + ("\n" if updated.strip() else "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the Context Spine block inside .gitignore.")
    parser.add_argument("--repo-root", default="", help="Target repo root; defaults to this repo")
    parser.add_argument("--mode", choices=["tracked", "local", "none"], default="")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser() if args.repo_root else Path(__file__).resolve().parents[2]
    config = load_config(repo_root)
    mode = args.mode or str(config.get("gitignore_mode", "tracked"))
    gitignore = repo_root / ".gitignore"
    content = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""

    if mode == "none":
        updated = remove_block(content)
    else:
        updated = replace_block(content, render_block(mode))

    if updated:
        gitignore.write_text(updated, encoding="utf-8")
    elif gitignore.exists():
        gitignore.unlink()

    if mode == "none":
        print(f"Removed Context Spine gitignore block from {gitignore}")
    else:
        print(f"Configured Context Spine gitignore mode '{mode}' in {gitignore}")
        if mode == "local":
            print("If Context Spine files are already tracked, untrack them once with: git rm -r --cached meta/context-spine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
