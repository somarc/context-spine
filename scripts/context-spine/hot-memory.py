#!/usr/bin/env python3
import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path

from context_config import load_config, resolve_repo_path


@dataclass
class WorkingSetItem:
    title: str
    path: Path
    reason: str
    section: str
    timestamp: dt.datetime | None = None


GENERATED_NAMES = {
    "README.md",
    "hot-memory-index.md",
    "memory-scorecard.md",
    "doctor-report.md",
    "doctor-report.json",
    "upgrade-report.md",
    "upgrade-report.json",
    "rollout-report.md",
    "rollout-report.json",
}


def default_memory_root() -> Path:
    return (Path(__file__).resolve().parents[2] / "meta" / "context-spine").resolve()


def infer_collection_root(memory_root: Path) -> Path:
    if memory_root.name == "context-spine" and memory_root.parent.name == "meta":
        return memory_root.parent.resolve()
    return memory_root.resolve()


def infer_repo_root(memory_root: Path) -> Path:
    if not (memory_root.name == "context-spine" and memory_root.parent.name == "meta"):
        return memory_root.resolve()
    parents = memory_root.parents
    if len(parents) > 1:
        return parents[1].resolve()
    return memory_root.resolve()


def safe_mtime(path: Path) -> dt.datetime | None:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return None


def latest_file(paths: list[Path]) -> Path | None:
    ranked = [(safe_mtime(path), path) for path in paths]
    ranked = [(stamp, path) for stamp, path in ranked if stamp is not None]
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1]


def parse_source_of_truth(note_path: Path, repo_root: Path) -> list[Path]:
    text = note_path.read_text(encoding="utf-8")
    if "---" not in text:
        return []
    _, rest = text.split("---", 1)
    if "---" not in rest:
        return []
    frontmatter, _ = rest.split("---", 1)
    match = re.search(r"(?ms)^source_of_truth:\s*\n(?P<body>(?:^\s+- .*\n?)*)", frontmatter)
    if not match:
        return []

    paths: list[Path] = []
    for raw_line in match.group("body").splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("- "):
            continue
        candidate = Path(stripped[2:].strip())
        resolved = candidate if candidate.is_absolute() else (repo_root / candidate)
        resolved = resolved.resolve()
        if resolved.exists():
            paths.append(resolved)
    return paths


def add_item(items: list[WorkingSetItem], seen: set[Path], item: WorkingSetItem) -> None:
    if item.path in seen or not item.path.exists():
        return
    seen.add(item.path)
    items.append(item)


def build_working_set(memory_root: Path, repo_root: Path, days: int) -> list[WorkingSetItem]:
    cutoff = dt.datetime.now() - dt.timedelta(days=days)
    items: list[WorkingSetItem] = []
    seen: set[Path] = set()

    baseline_candidates = sorted(memory_root.glob("spine-notes-*.md"))
    baseline_note = latest_file(baseline_candidates)
    if baseline_note is not None:
        add_item(
            items,
            seen,
            WorkingSetItem(
                title="Current baseline note",
                path=baseline_note,
                reason="The baseline is the highest-signal durable model of the repo.",
                section="Start Here",
                timestamp=safe_mtime(baseline_note),
            ),
        )

    latest_session = latest_file(sorted((memory_root / "sessions").glob("*.md")))
    if latest_session is not None:
        add_item(
            items,
            seen,
            WorkingSetItem(
                title="Latest session note",
                path=latest_session,
                reason="The latest session is the fastest way to recover active work and current intent.",
                section="Start Here",
                timestamp=safe_mtime(latest_session),
            ),
        )

    if baseline_note is not None:
        for path in parse_source_of_truth(baseline_note, repo_root)[:8]:
            add_item(
                items,
                seen,
                WorkingSetItem(
                    title=path.name,
                    path=path,
                    reason="Referenced in the baseline note as source of truth.",
                    section="Source Of Truth",
                    timestamp=safe_mtime(path),
                ),
            )

    candidate_docs = [
        repo_root / "docs" / "runbooks" / "session-start.md",
        repo_root / "docs" / "runbooks" / "doctor.md",
        repo_root / "docs" / "runbooks" / "upgrade-existing-project.md",
        repo_root / "docs" / "runbooks" / "multi-repo-rollout.md",
        repo_root / "docs" / "runbooks" / "pi-extension-points.md",
    ]
    for path in candidate_docs:
        if path.exists():
            add_item(
                items,
                seen,
                WorkingSetItem(
                    title=path.name,
                    path=path,
                    reason="Canonical runbook for the current operating loop.",
                    section="Canonical Docs",
                    timestamp=safe_mtime(path),
                ),
            )

    recent_memory: list[WorkingSetItem] = []
    for path in memory_root.rglob("*.md"):
        if path.name in GENERATED_NAMES:
            continue
        stamp = safe_mtime(path)
        if stamp is None or stamp < cutoff:
            continue
        recent_memory.append(
            WorkingSetItem(
                title=path.name,
                path=path,
                reason="Recently changed memory surface.",
                section="Recent Memory",
                timestamp=stamp,
            )
        )
    recent_memory.sort(key=lambda item: item.timestamp or dt.datetime.min, reverse=True)
    for item in recent_memory[:8]:
        add_item(items, seen, item)

    evidence_dir = repo_root / "docs" / "evidence"
    if evidence_dir.exists():
        evidence_files = sorted(evidence_dir.glob("*.md"))
        latest_evidence = latest_file(evidence_files)
        if latest_evidence is not None:
            add_item(
                items,
                seen,
                WorkingSetItem(
                    title=latest_evidence.name,
                    path=latest_evidence,
                    reason="Most recent evidence artifact.",
                    section="Latest Evidence",
                    timestamp=safe_mtime(latest_evidence),
                ),
            )

    diagram_dir = repo_root / ".agent" / "diagrams"
    if diagram_dir.exists():
        diagrams = sorted(diagram_dir.glob("*.html"))
        ranked_diagrams = [(safe_mtime(path), path) for path in diagrams]
        ranked_diagrams = [(stamp, path) for stamp, path in ranked_diagrams if stamp is not None]
        ranked_diagrams.sort(key=lambda item: item[0], reverse=True)
        for stamp, path in ranked_diagrams[:4]:
            add_item(
                items,
                seen,
                WorkingSetItem(
                    title=path.name,
                    path=path,
                    reason="Current visual explainer surface.",
                    section="Visual Explainers",
                    timestamp=stamp,
                ),
            )

    return items


def render_link(path: Path, repo_root: Path, collection_root: Path, collection_name: str) -> str:
    try:
        rel_repo = path.relative_to(repo_root).as_posix()
    except ValueError:
        return f"`{path}`"
    try:
        rel_collection = path.relative_to(collection_root).as_posix()
    except ValueError:
        rel_collection = ""

    if collection_name and rel_collection:
        return f"`qmd://{collection_name}/{rel_collection}` ({rel_repo})"
    return f"`{rel_repo}`"


def main():
    parser = argparse.ArgumentParser(description="Generate a working-set-focused hot-memory index.")
    parser.add_argument("--days", type=int, default=7, help="Lookback window for recent memory")
    parser.add_argument("--collection", default="", help="QMD collection name for links")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    repo_root_default = Path(__file__).resolve().parents[2]
    config = load_config(repo_root_default)
    configured_root = resolve_repo_path(repo_root_default, str(config.get("memory_root", default_memory_root())))
    collection_name = args.collection or str(config.get("collections", {}).get("meta", "context-spine-meta"))
    memory_root = (Path(args.root).expanduser() if args.root else configured_root).resolve()
    collection_root = infer_collection_root(memory_root)
    repo_root = infer_repo_root(memory_root)

    items = build_working_set(memory_root, repo_root, args.days)
    sections = [
        "Start Here",
        "Source Of Truth",
        "Canonical Docs",
        "Recent Memory",
        "Latest Evidence",
        "Visual Explainers",
    ]

    lines = [
        "# Hot Memory Index",
        "",
        f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Mode: working set, not raw recency",
        f"Recent-memory window: last {args.days} days",
        "",
        "This file is meant to answer: what should an agent or maintainer open first right now?",
        "",
    ]

    if not items:
        lines.append("- No working-set items found.")
    else:
        for section in sections:
            section_items = [item for item in items if item.section == section]
            if not section_items:
                continue
            lines.extend([f"## {section}", ""])
            for item in section_items:
                stamp = item.timestamp.strftime("%Y-%m-%d %H:%M") if item.timestamp else "unknown"
                link = render_link(item.path, repo_root, collection_root, collection_name)
                lines.append(f"- **{item.title}** · {stamp}")
                lines.append(f"  - why: {item.reason}")
                lines.append(f"  - open: {link}")
            lines.append("")

    out_file = memory_root / "hot-memory-index.md"
    out_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
