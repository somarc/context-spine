#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from context_config import default_config_path, load_config, resolve_repo_path
from run_state import finish_run, start_run
from runtime_manifest import default_manifest_path, load_runtime_manifest


@dataclass
class CheckResult:
    slug: str
    title: str
    status: str
    summary: str
    details: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)


PASS = "pass"
WARN = "warn"
FAIL = "fail"


def script_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_repo_root() -> Path:
    return script_root()


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )


def plural(value: int, noun: str) -> str:
    return f"{value} {noun}" + ("" if value == 1 else "s")


def fmt_age(days: int | None) -> str:
    if days is None:
        return "unknown age"
    if days < 0:
        return "future-dated"
    if days == 0:
        return "today"
    if days == 1:
        return "1 day old"
    return f"{days} days old"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return ""


def find_baseline(memory_root: Path, preferred_name: str = "spine-notes-context-spine.md") -> Path | None:
    preferred = memory_root / preferred_name
    if preferred.exists():
        return preferred
    candidates = sorted(memory_root.glob("spine-notes-*.md"))
    return candidates[0] if candidates else None


def parse_source_paths(baseline_text: str) -> list[str]:
    lines = baseline_text.splitlines()
    items: list[str] = []
    in_frontmatter = False
    in_sources = False

    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            if not in_frontmatter:
                in_sources = False
            continue
        if in_frontmatter:
            if line.startswith("source_of_truth:"):
                in_sources = True
                continue
            if in_sources:
                stripped = line.strip()
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip())
                    continue
                if stripped and not stripped.startswith("#"):
                    in_sources = False
        elif line.strip() == "## Sources":
            in_sources = True
            continue
        elif in_sources:
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
                continue
            if stripped.startswith("## "):
                in_sources = False
    return items


def resolve_source_path(entry: str, repo_root: Path) -> Path | None:
    if not entry or entry.startswith("qmd://") or "://" in entry:
        return None
    path = Path(entry).expanduser()
    if path.is_absolute():
        return path
    return repo_root / entry


def latest_session_file(memory_root: Path) -> Path | None:
    sessions_dir = memory_root / "sessions"
    if not sessions_dir.is_dir():
        return None
    files = sorted(sessions_dir.glob("*-session.md"))
    return files[-1] if files else None


def session_date_from_name(path: Path) -> dt.date | None:
    name = path.name[:10]
    try:
        return dt.date.fromisoformat(name)
    except ValueError:
        return None


def git_available(repo_root: Path) -> bool:
    return run(["git", "rev-parse", "--show-toplevel"], cwd=repo_root).returncode == 0


def latest_commit_date(repo_root: Path, memory_root: Path) -> dt.date | None:
    if not git_available(repo_root):
        return None
    memory_pathspec = relative_repo_path(repo_root, memory_root)
    result = run(
        [
            "git",
            "log",
            "-1",
            "--format=%cs",
            "--",
            ".",
            *([f":(exclude){memory_pathspec}/**"] if memory_pathspec else []),
            ":(exclude).agent/diagrams/**",
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    if not output:
        return None
    try:
        return dt.date.fromisoformat(output)
    except ValueError:
        return None


def dirty_worktree_paths(repo_root: Path, memory_root: Path) -> list[str]:
    if not git_available(repo_root):
        return []
    result = run(["git", "status", "--porcelain"], cwd=repo_root)
    if result.returncode != 0:
        return []
    return [line[3:] for line in result.stdout.splitlines() if len(line) > 3]


def placeholder_lines(text: str) -> list[str]:
    placeholders = []
    for index, line in enumerate(text.splitlines(), start=1):
        stripped = line.rstrip()
        if stripped in {"- ", "-"}:
            placeholders.append(f"line {index}: blank bullet")
    return placeholders


def file_age_days(path: Path) -> int | None:
    if not path.exists():
        return None
    mtime = dt.datetime.fromtimestamp(path.stat().st_mtime)
    return (dt.datetime.now() - mtime).days


def docs_markdown_files(docs_root: Path) -> list[Path]:
    return sorted(path for path in docs_root.rglob("*.md") if path.is_file())


def top_level_docs_files(docs_root: Path) -> list[Path]:
    return sorted(path for path in docs_root.glob("*.md") if path.is_file())


def roadmap_like_docs(paths: Iterable[Path]) -> list[Path]:
    keywords = ("roadmap", "phase-plan", "sprint", "implementation-gap", "implementation-gaps", "plan")
    matches: list[Path] = []
    for path in paths:
        name = path.name.lower()
        if any(keyword in name for keyword in keywords):
            matches.append(path)
    return matches


def check_config(repo_root: Path, memory_root: Path, config: dict, config_path: Path, config_error: str) -> CheckResult:
    if config_error:
        return CheckResult(
            slug="config",
            title="Context Spine config",
            status=FAIL,
            summary=f"Could not load `{config_path.relative_to(repo_root)}`.",
            details=[config_error],
            actions=["Fix the JSON syntax so every Context Spine runtime surface reads the same contract."],
        )

    preferred_file = str(config.get("baseline", {}).get("preferred_file", "")).strip()
    qmd_collection = str(config.get("collections", {}).get("meta", "")).strip()
    configured_memory_root = resolve_repo_path(repo_root, str(config.get("memory_root", default_memory_root(repo_root))))

    details = [
        f"Memory root: {configured_memory_root}",
        f"Preferred baseline: {preferred_file or '(default fallback only)'}",
    ]
    actions: list[str] = []

    if not config_path.exists():
        return CheckResult(
            slug="config",
            title="Context Spine config",
            status=WARN,
            summary="No explicit `context-spine.json` config is present.",
            details=details,
            actions=[
                "Add `meta/context-spine/context-spine.json` so bootstrap, doctor, scoring, and upgrade use the same explicit repo contract."
            ],
        )

    status = PASS
    summary = "Explicit Context Spine config is present."

    if configured_memory_root != memory_root.resolve():
        status = WARN
        details.append(f"Doctor memory root: {memory_root.resolve()}")
        actions.append("Align `--root` usage with `context-spine.json`, or update the config if the memory root moved.")
        summary = "The loaded config and requested memory root disagree."

    if not preferred_file:
        status = WARN
        actions.append("Set `baseline.preferred_file` in `context-spine.json` so upgrades and bootstrap share the same preferred baseline.")
        summary = "The config exists, but baseline preference is still implicit."

    if not qmd_collection:
        status = WARN
        actions.append("Set `collections.meta` in `context-spine.json` so QMD-aware scripts do not rely on fallback collection names.")
        summary = "The config exists, but the primary QMD collection is still implicit."
    else:
        details.append(f"Meta collection: {qmd_collection}")

    return CheckResult(
        slug="config",
        title="Context Spine config",
        status=status,
        summary=summary,
        details=details,
        actions=actions,
    )


def check_runtime_manifest(repo_root: Path) -> CheckResult:
    manifest_path = default_manifest_path(repo_root)
    if not manifest_path.exists():
        return CheckResult(
            slug="runtime-manifest",
            title="Runtime manifest",
            status=WARN,
            summary="No versioned runtime manifest is present.",
            actions=["Add `scripts/context-spine/runtime-manifest.json` or run the latest `context:upgrade` from the boilerplate source."],
        )

    try:
        manifest = load_runtime_manifest(repo_root)
    except Exception as exc:
        return CheckResult(
            slug="runtime-manifest",
            title="Runtime manifest",
            status=FAIL,
            summary=f"Could not load `{manifest_path.relative_to(repo_root)}`.",
            details=[str(exc)],
            actions=["Fix the runtime manifest so doctor, upgrade, and run-state surfaces can share one versioned contract."],
        )

    runtime_files = [str(item) for item in manifest.get("runtime_files", [])]
    missing_files = [path for path in runtime_files if not (repo_root / path).exists()]
    details = [
        f"Runtime version: {manifest.get('runtime_version', 'unknown')}",
        f"Runtime files declared: {len(runtime_files)}",
    ]
    if missing_files:
        return CheckResult(
            slug="runtime-manifest",
            title="Runtime manifest",
            status=WARN,
            summary="The runtime manifest is present, but some declared runtime files are missing.",
            details=details + [f"Missing: {path}" for path in missing_files],
            actions=["Run `context:upgrade` from the boilerplate source to restore missing runtime files."],
        )

    return CheckResult(
        slug="runtime-manifest",
        title="Runtime manifest",
        status=PASS,
        summary="Versioned runtime manifest is present and its declared runtime files resolve.",
        details=details,
    )


def check_baseline(repo_root: Path, memory_root: Path, preferred_name: str) -> CheckResult:
    baseline = find_baseline(memory_root, preferred_name=preferred_name)
    if not baseline:
        return CheckResult(
            slug="baseline",
            title="Baseline note",
            status=FAIL,
            summary="No baseline `spine-notes-*.md` note was found.",
            actions=["Create a baseline note before relying on Context Spine as the project entry point."],
        )

    baseline_text = read_text(baseline)
    source_entries = parse_source_paths(baseline_text)
    missing: list[str] = []
    resolved = 0
    for entry in source_entries:
        resolved_path = resolve_source_path(entry, repo_root)
        if resolved_path is None:
            continue
        resolved += 1
        if not resolved_path.exists():
            missing.append(entry)

    if missing:
        return CheckResult(
            slug="baseline",
            title="Baseline note",
            status=WARN,
            summary=f"{baseline.name} exists, but {plural(len(missing), 'source-of-truth path')} no longer resolve.",
            details=[f"Missing: {entry}" for entry in missing],
            actions=["Refresh `source_of_truth` and `Sources` paths so the baseline still points to live artifacts."],
        )

    summary = f"{baseline.name} is present."
    if resolved:
        summary += f" Verified {plural(resolved, 'local source path')}."
    return CheckResult(
        slug="baseline",
        title="Baseline note",
        status=PASS,
        summary=summary,
    )


def check_session(repo_root: Path, memory_root: Path) -> CheckResult:
    latest = latest_session_file(memory_root)
    if not latest:
        return CheckResult(
            slug="session",
            title="Latest session",
            status=WARN,
            summary="No `*-session.md` file was found.",
            actions=["Create a fresh session note before the next substantial work block."],
        )

    session_date = session_date_from_name(latest)
    commit_date = latest_commit_date(repo_root, memory_root)
    memory_root_rel = relative_repo_path(repo_root, memory_root)
    dirty_paths = [
        path for path in dirty_worktree_paths(repo_root, memory_root)
        if not (memory_root_rel and path.startswith(f"{memory_root_rel}/")) and not path.startswith(".agent/diagrams/")
    ]
    latest_text = read_text(latest)
    placeholders = placeholder_lines(latest_text)

    details: list[str] = [f"Latest session: {latest.name} ({fmt_age((dt.date.today() - session_date).days) if session_date else 'date not inferred'})"]
    actions: list[str] = []
    status = PASS
    summary = f"{latest.name} looks current."

    if commit_date and session_date and session_date < commit_date:
        status = WARN
        details.append(f"Latest non-memory commit date: {commit_date.isoformat()}")
        actions.append("Refresh the session note after code or doc changes land.")
        summary = "Code or docs changed after the latest session note."

    if dirty_paths:
        status = WARN if status == PASS else status
        details.append(f"Dirty worktree outside memory surfaces: {plural(len(dirty_paths), 'path')}")
        actions.append("Capture the current work-in-progress in a fresh or updated session note.")

    if placeholders:
        status = WARN if status == PASS else status
        details.extend(placeholders[:5])
        if len(placeholders) > 5:
            details.append(f"...and {len(placeholders) - 5} more placeholder lines")
        actions.append("Replace session template placeholders with concrete facts or remove unused sections.")
        if summary == f"{latest.name} looks current.":
            summary = "The latest session note exists but still contains placeholder content."

    return CheckResult(
        slug="session",
        title="Latest session",
        status=status,
        summary=summary,
        details=details,
        actions=actions,
    )


def check_generated(memory_root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []

    hot_index = memory_root / "hot-memory-index.md"
    hot_age = file_age_days(hot_index)
    if hot_age is None:
        results.append(
            CheckResult(
                slug="hot-memory",
                title="Hot memory index",
                status=WARN,
                summary="No hot-memory index is present.",
                actions=["Run `npm run context:bootstrap` or `python3 scripts/context-spine/hot-memory.py`."],
            )
        )
    elif hot_age > 7:
        results.append(
            CheckResult(
                slug="hot-memory",
                title="Hot memory index",
                status=WARN,
                summary=f"Hot memory is stale ({fmt_age(hot_age)}).",
                actions=["Regenerate hot memory so bootstrap points at current high-signal artifacts."],
            )
        )
    else:
        results.append(
            CheckResult(
                slug="hot-memory",
                title="Hot memory index",
                status=PASS,
                summary=f"Hot memory is present and {fmt_age(hot_age)}.",
            )
        )

    scorecard = memory_root / "memory-scorecard.md"
    score_age = file_age_days(scorecard)
    if score_age is None:
        results.append(
            CheckResult(
                slug="scorecard",
                title="Memory scorecard",
                status=WARN,
                summary="No memory scorecard is present.",
                actions=["Run `npm run context:score` after meaningful note or doc changes."],
            )
        )
    elif score_age > 14:
        results.append(
            CheckResult(
                slug="scorecard",
                title="Memory scorecard",
                status=WARN,
                summary=f"Memory scorecard is stale ({fmt_age(score_age)}).",
                actions=["Refresh the scorecard so retrieval health is visible."],
            )
        )
    else:
        results.append(
            CheckResult(
                slug="scorecard",
                title="Memory scorecard",
                status=PASS,
                summary=f"Memory scorecard is present and {fmt_age(score_age)}.",
            )
        )

    return results


def check_docs(repo_root: Path) -> CheckResult:
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return CheckResult(
            slug="docs-governance",
            title="Docs governance",
            status=PASS,
            summary="No docs directory is present, so doc-governance checks were skipped.",
        )

    details: list[str] = []
    actions: list[str] = []
    status = PASS

    docs_readme = docs_root / "README.md"
    if not docs_readme.exists():
        status = WARN
        details.append("Missing docs/README.md")
        actions.append("Add `docs/README.md` so people know what is canonical, archived, or draft.")

    archive_dir = docs_root / "archive"
    if not archive_dir.exists():
        status = WARN
        details.append("Missing docs/archive/")
        actions.append("Add `docs/archive/` for retired or superseded documentation.")

    drafts_dir = docs_root / "drafts"
    if not drafts_dir.exists():
        status = WARN
        details.append("Missing docs/drafts/")
        actions.append("Add `docs/drafts/` for work-in-progress material that should not read as canonical.")

    top_level = [path for path in top_level_docs_files(docs_root) if path.name != "README.md"]
    roadmap_candidates = roadmap_like_docs(top_level)
    if len(roadmap_candidates) > 1:
        status = WARN
        details.append(
            "Multiple roadmap-like docs at docs root: "
            + ", ".join(path.name for path in roadmap_candidates)
        )
        actions.append("Declare one active roadmap and move older planning docs into `docs/archive/`.")

    if status == PASS:
        total_docs = len(docs_markdown_files(docs_root))
        return CheckResult(
            slug="docs-governance",
            title="Docs governance",
            status=PASS,
            summary=f"Docs authority surfaces are in place across {plural(total_docs, 'Markdown file')}.",
        )

    return CheckResult(
        slug="docs-governance",
        title="Docs governance",
        status=status,
        summary="Docs exist, but the authority boundaries are not fully explicit.",
        details=details,
        actions=actions,
    )


def check_visuals(repo_root: Path) -> CheckResult:
    diagrams = repo_root / ".agent" / "diagrams"
    if not diagrams.is_dir():
        return CheckResult(
            slug="visual-surface",
            title="Visual explainer surface",
            status=WARN,
            summary="No `.agent/diagrams/` directory is present.",
            actions=["Add `.agent/diagrams/` so visual explainers have a stable home."],
        )

    visual_files = sorted(diagrams.glob("*.html"))
    if not visual_files:
        return CheckResult(
            slug="visual-surface",
            title="Visual explainer surface",
            status=WARN,
            summary="The diagrams directory exists, but it has no HTML explainers yet.",
            actions=["Add at least one HTML explainer for a subsystem or workflow that benefits from a visual reading path."],
        )

    return CheckResult(
        slug="visual-surface",
        title="Visual explainer surface",
        status=PASS,
        summary=f"Found {plural(len(visual_files), 'HTML explainer')} in `.agent/diagrams/`.",
    )


def summarize_status(results: list[CheckResult]) -> dict[str, int]:
    counts = {PASS: 0, WARN: 0, FAIL: 0}
    for result in results:
        counts[result.status] += 1
    return counts


def render_markdown(
    repo_root: Path,
    memory_root: Path,
    results: list[CheckResult],
    generated_at: dt.datetime,
    *,
    run_id: str,
    runtime_version: str,
) -> str:
    counts = summarize_status(results)
    lines = [
        "# Context Doctor Report",
        "",
        f"- Run ID: {run_id}",
        f"- Runtime version: {runtime_version}",
        f"- Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Repo root: {repo_root}",
        f"- Memory root: {memory_root}",
        "",
        "## Summary",
        f"- Pass: {counts[PASS]}",
        f"- Warn: {counts[WARN]}",
        f"- Fail: {counts[FAIL]}",
        "",
        "## Checks",
    ]

    icon = {PASS: "PASS", WARN: "WARN", FAIL: "FAIL"}
    for result in results:
        lines.extend(
            [
                "",
                f"### [{icon[result.status]}] {result.title}",
                result.summary,
            ]
        )
        if result.details:
            lines.append("")
            lines.append("Details:")
            lines.extend(f"- {detail}" for detail in result.details)
        if result.actions:
            lines.append("")
            lines.append("Actions:")
            lines.extend(f"- {action}" for action in result.actions)

    if counts[WARN] or counts[FAIL]:
        lines.extend(["", "## Next Actions"])
        emitted = set()
        for result in results:
            for action in result.actions:
                if action not in emitted:
                    emitted.add(action)
                    lines.append(f"- {action}")

    return "\n".join(lines) + "\n"


def render_terminal(results: list[CheckResult]) -> str:
    counts = summarize_status(results)
    lines = [
        "===== CONTEXT DOCTOR =====",
        f"pass={counts[PASS]} warn={counts[WARN]} fail={counts[FAIL]}",
        "",
    ]
    labels = {PASS: "PASS", WARN: "WARN", FAIL: "FAIL"}
    for result in results:
        lines.append(f"[{labels[result.status]}] {result.title}: {result.summary}")
        for detail in result.details:
            lines.append(f"  - {detail}")
        for action in result.actions[:2]:
            lines.append(f"  -> {action}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Context Spine hygiene and project-truth drift.")
    parser.add_argument("--repo-root", default="", help="Project root to inspect")
    parser.add_argument("--root", default="", help="Override memory root directory")
    parser.add_argument("--out", default="", help="Write markdown report to this path")
    parser.add_argument("--json-out", default="", help="Write machine-readable JSON report to this path")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as failures")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser() if args.repo_root else default_repo_root()
    config_path = default_config_path(repo_root)
    config_error = ""
    try:
        config = load_config(repo_root)
    except Exception as exc:
        config = {}
        config_error = str(exc)

    configured_memory_root = default_memory_root(repo_root)
    preferred_baseline = "spine-notes-context-spine.md"
    if not config_error and config:
        configured_memory_root = resolve_repo_path(repo_root, str(config.get("memory_root", configured_memory_root)))
        preferred_baseline = str(config.get("baseline", {}).get("preferred_file", preferred_baseline))

    memory_root = Path(args.root).expanduser() if args.root else configured_memory_root
    generated_at = dt.datetime.now()
    run_handle = start_run(
        repo_root,
        memory_root,
        "context:doctor",
        args=vars(args),
    )

    results = [
        check_config(repo_root, memory_root, config, config_path, config_error),
        check_runtime_manifest(repo_root),
        check_baseline(repo_root, memory_root, preferred_baseline),
        check_session(repo_root, memory_root),
        *check_generated(memory_root),
        check_docs(repo_root),
        check_visuals(repo_root),
    ]

    report = render_markdown(
        repo_root,
        memory_root,
        results,
        generated_at,
        run_id=run_handle.run_id,
        runtime_version=run_handle.payload["runtime_version"],
    )
    out_path = Path(args.out).expanduser() if args.out else memory_root / "doctor-report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    artifacts = [str(out_path)]
    if args.json_out:
        json_path = Path(args.json_out).expanduser()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {
                    "run_id": run_handle.run_id,
                    "runtime_version": run_handle.payload["runtime_version"],
                    "generated_at": generated_at.isoformat(),
                    "repo_root": str(repo_root),
                    "memory_root": str(memory_root),
                    "results": [result.__dict__ for result in results],
                    "counts": summarize_status(results),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        artifacts.append(str(json_path))

    counts = summarize_status(results)
    run_status = FAIL if counts[FAIL] > 0 else WARN if counts[WARN] > 0 else PASS
    finish_run(
        run_handle,
        status=run_status,
        summary=f"Doctor counts: pass={counts[PASS]} warn={counts[WARN]} fail={counts[FAIL]}",
        artifacts=artifacts,
        extra={"counts": counts},
    )
    sys.stdout.write(f"Run ID: {run_handle.run_id}\n")
    sys.stdout.write(render_terminal(results))
    sys.stdout.write(f"Report: {out_path}\n")

    if counts[FAIL] > 0:
        return 1
    if args.strict and counts[WARN] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
