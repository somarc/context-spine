#!/usr/bin/env python3
import argparse
import datetime as dt
from pathlib import Path

from context_config import load_config, resolve_repo_path
from memory_records import write_record


def split_csv(value: str):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_frontmatter(path: Path, date_str: str, project: str):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        f"date: {date_str}\n"
        "type: context-spine-observations\n"
        f"project: {project}\n"
        "---\n\n"
    )
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Append a Context Spine observation.")
    parser.add_argument("--summary", required=True, help="Short summary of the observation")
    parser.add_argument("--type", default="observation", help="observation|decision|question|todo|summary")
    parser.add_argument("--project", default="", help="Project name")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--files", default="", help="Comma-separated file paths")
    parser.add_argument("--details", default="", help="Longer details")
    parser.add_argument("--truth", default="", help="verified|assumed|hypothesis")
    parser.add_argument("--evidence", default="", help="Comma-separated evidence")
    parser.add_argument("--constraints", default="", help="Comma-separated constraints")
    parser.add_argument("--assumptions", default="", help="Comma-separated assumptions")
    parser.add_argument("--action", default="", help="Next action")
    parser.add_argument("--qmd", default="", help="Comma-separated qmd links or queries")
    parser.add_argument("--session", default="", help="Session identifier or title")
    parser.add_argument("--date", default="", help="Override date in YYYY-MM-DD")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    now = dt.datetime.now()
    date_str = args.date or now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    repo_root = default_repo_root()
    config = load_config(repo_root)
    configured_root = resolve_repo_path(repo_root, str(config.get("memory_root", "meta/context-spine")))
    project_name = args.project or str(config.get("project", "project"))
    memory_root = (Path(args.root).expanduser() if args.root else configured_root).resolve()
    observations_file = memory_root / "observations" / f"{date_str}.md"
    ensure_frontmatter(observations_file, date_str, project_name)

    tags = split_csv(args.tags)
    files = split_csv(args.files)
    evidence = split_csv(args.evidence)
    constraints = split_csv(args.constraints)
    assumptions = split_csv(args.assumptions)
    qmd_items = split_csv(args.qmd)

    lines = [f"## {time_str}", f"- type: {args.type}", f"- summary: {args.summary}"]
    if args.session:
        lines.append(f"- session: {args.session}")
    if tags:
        lines.append(f"- tags: [{', '.join(tags)}]")
    if args.truth:
        lines.append(f"- truth: {args.truth}")
    if evidence:
        lines.append("- evidence:")
        lines.extend([f"  - {item}" for item in evidence])
    if constraints:
        lines.append("- constraints:")
        lines.extend([f"  - {item}" for item in constraints])
    if assumptions:
        lines.append("- assumptions:")
        lines.extend([f"  - {item}" for item in assumptions])
    if qmd_items:
        lines.append("- qmd:")
        lines.extend([f"  - {item}" for item in qmd_items])
    if args.action:
        lines.append(f"- action: {args.action}")
    if files:
        lines.append("- files:")
        lines.extend([f"  - {item}" for item in files])
    if args.details:
        lines.append("- details:")
        lines.append(f"  - {args.details}")

    with observations_file.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n\n")

    record_path = write_record(
        memory_root,
        "observations",
        {
            "layer": "observation",
            "project": project_name,
            "date": date_str,
            "time": time_str,
            "summary": args.summary,
            "entry_type": args.type,
            "markdown_path": str(observations_file),
            "tags": tags,
            "truth": args.truth,
            "evidence": evidence,
            "constraints": constraints,
            "assumptions": assumptions,
            "qmd": qmd_items,
            "files": files,
            "details": args.details,
            "action": args.action,
            "session": args.session,
        },
        record_id=f"observation-{date_str}-{time_str}",
        recorded_at=dt.datetime.now(dt.UTC).replace(microsecond=0),
    )

    print(f"Appended observation to {observations_file}")
    print(f"Observation record: {record_path}")


if __name__ == "__main__":
    main()
