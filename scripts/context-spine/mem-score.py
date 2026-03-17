#!/usr/bin/env python3
import argparse
import datetime as dt
import re
from pathlib import Path

from context_config import default_config_path, load_config, resolve_repo_path
from generated_artifact import GeneratedArtifactSpec, markdown_heading_validator, publish_generated_artifacts
from run_state import finish_run, start_run


QMD_PATTERN = re.compile(r"(qmd://|\bqmd\b)", re.IGNORECASE)
SESSION_LIKE = re.compile(r"(session|day)\.md$", re.IGNORECASE)
TIME_HEADER = re.compile(r"^## \d{2}:\d{2}:\d{2}")


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def iter_session_files(sessions_dir: Path):
    if not sessions_dir.is_dir():
        return []
    return sorted([path for path in sessions_dir.glob("*.md") if SESSION_LIKE.search(path.name)])


def first_qmd_line(lines):
    for index, line in enumerate(lines, start=1):
        if QMD_PATTERN.search(line):
            return index
    return None


def session_stats(sessions_dir: Path):
    files = iter_session_files(sessions_dir)
    total = len(files)
    with_qmd = 0
    early_qmd = 0
    qmd_mentions = 0
    qmd_links = 0
    first_qmd_ratios = []

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        total_lines = max(len(lines), 1)
        matches = list(QMD_PATTERN.finditer(text))
        if not matches:
            continue
        with_qmd += 1
        first_line = first_qmd_line(lines)
        if first_line is not None:
            ratio = first_line / total_lines
            first_qmd_ratios.append(ratio)
            if ratio <= 0.25:
                early_qmd += 1
        qmd_mentions += len(matches)
        qmd_links += sum(1 for match in matches if match.group(0).lower().startswith("qmd://"))

    return {
        "total": total,
        "with_qmd": with_qmd,
        "early_qmd": early_qmd,
        "qmd_mentions": qmd_mentions,
        "qmd_links": qmd_links,
        "first_qmd_ratios": first_qmd_ratios,
    }


def observation_stats(observations_dir: Path):
    if not observations_dir.is_dir():
        return {"entries": 0, "qmd_entries": 0}
    entries = 0
    qmd_entries = 0
    for path in sorted(observations_dir.glob("*.md")):
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        current = []
        seen_time_header = False
        for line in lines:
            if TIME_HEADER.match(line):
                seen_time_header = True
                if current:
                    entries += 1
                    if QMD_PATTERN.search("\n".join(current)):
                        qmd_entries += 1
                current = [line]
            elif seen_time_header:
                current.append(line)
        if current and seen_time_header:
            entries += 1
            if QMD_PATTERN.search("\n".join(current)):
                qmd_entries += 1
    return {"entries": entries, "qmd_entries": qmd_entries}


def hot_memory_age(hot_index: Path):
    if not hot_index.exists():
        return None
    mtime = dt.datetime.fromtimestamp(hot_index.stat().st_mtime)
    return (dt.datetime.now() - mtime).total_seconds() / 86400


def percentage(numerator, denominator):
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


def freshness_score(age_days):
    if age_days is None:
        return 0.0
    if age_days <= 1:
        return 100.0
    if age_days <= 3:
        return 80.0
    if age_days <= 7:
        return 60.0
    if age_days <= 14:
        return 40.0
    return 20.0


def hook_score(bootstrap: Path):
    return 100.0 if bootstrap.exists() else 0.0


def config_score(config_path: Path, config_error: str):
    if config_error:
        return 0.0
    return 100.0 if config_path.exists() else 0.0


def observation_density_score(entries, total_sessions):
    if total_sessions <= 0:
        return 0.0
    return min(entries, total_sessions) / total_sessions * 100.0


def weighted_score(coverage, early, observation_rate, observation_density, hooks, freshness, config):
    return round(
        coverage * 0.25 +
        early * 0.15 +
        observation_rate * 0.10 +
        observation_density * 0.15 +
        hooks * 0.10 +
        freshness * 0.20 +
        config * 0.05,
        1,
    )


def format_percent(value):
    return f"{value:.1f}%"


def main():
    parser = argparse.ArgumentParser(description="Score Context Spine memory quality.")
    parser.add_argument("--root", default="", help="Override memory root directory")
    parser.add_argument("--out", default="", help="Output scorecard path")
    args = parser.parse_args()

    repo_root = default_repo_root()
    config_path = default_config_path(repo_root)
    config_error = ""
    try:
        config = load_config(repo_root)
    except Exception as exc:
        config = {}
        config_error = str(exc)

    configured_memory_root = default_memory_root(repo_root)
    if not config_error and config:
        configured_memory_root = resolve_repo_path(repo_root, str(config.get("memory_root", configured_memory_root)))

    memory_root = (Path(args.root).expanduser() if args.root else configured_memory_root).resolve()
    run_handle = start_run(
        repo_root,
        memory_root,
        "context:score",
        args=vars(args),
    )
    sessions = session_stats(memory_root / "sessions")
    observations = observation_stats(memory_root / "observations")
    hot_age = hot_memory_age(memory_root / "hot-memory-index.md")
    hooks = hook_score(Path(__file__).resolve().parent / "bootstrap.sh")

    coverage = percentage(sessions["with_qmd"], sessions["total"])
    early = percentage(sessions["early_qmd"], sessions["total"])
    observation_rate = percentage(observations["qmd_entries"], observations["entries"])
    observation_density = observation_density_score(observations["entries"], sessions["total"])
    freshness = freshness_score(hot_age)
    explicit_config = config_score(config_path, config_error)
    total = weighted_score(coverage, early, observation_rate, observation_density, hooks, freshness, explicit_config)

    avg_first_qmd = None
    if sessions["first_qmd_ratios"]:
        avg_first_qmd = sum(sessions["first_qmd_ratios"]) / len(sessions["first_qmd_ratios"])

    lines = [
        "# Memory Scorecard",
        "",
        f"- Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Memory root: {memory_root}",
        "",
        "## Overall Score",
        f"- MQS: {total}/100",
        "",
        "## Operating Contract",
        f"- Explicit config present: {'yes' if explicit_config > 0 else 'no'}",
    ]
    if config_error:
        lines.append(f"- Config load error: {config_error}")
    else:
        lines.append(f"- Config file: {config_path}")
    lines.extend([
        "",
        "## QMD Usage (Sessions)",
        f"- Session files scanned: {sessions['total']}",
        f"- Sessions with QMD mentions: {sessions['with_qmd']} ({format_percent(coverage)})",
        f"- Sessions with early QMD: {sessions['early_qmd']} ({format_percent(early)})",
        f"- QMD mentions in sessions: {sessions['qmd_mentions']}",
        f"- QMD links in sessions: {sessions['qmd_links']}",
        "",
        "## QMD Usage (Observations)",
        f"- Observation entries: {observations['entries']}",
        f"- Entries with QMD mentions: {observations['qmd_entries']} ({format_percent(observation_rate)})",
        f"- Observation density vs sessions: {format_percent(observation_density)}",
        "",
        "## Hooks & Freshness",
        f"- Bootstrap script present: {'yes' if hooks > 0 else 'no'}",
    ])
    if avg_first_qmd is not None:
        lines.append(f"- Avg first QMD position: {format_percent(avg_first_qmd * 100)} of file")
    if hot_age is None:
        lines.append("- Hot memory index: missing")
    else:
        lines.append(f"- Hot memory index age: {hot_age:.1f} days")
    lines.extend([
        "",
        "## Recommendations",
    ])
    if coverage < 80:
        lines.append("- Add QMD hits to session summaries earlier.")
    if early < 70:
        lines.append("- Run retrieval preflight before heavier repo-wide searches.")
    if observation_rate < 50:
        lines.append("- Link more observations to concrete qmd queries or qmd:// references.")
    if observation_density < 70:
        lines.append("- Capture more than one-off observations so session history and observation history stay coupled.")
    if hooks == 0:
        lines.append("- Add or restore the bootstrap hook.")
    if hot_age is None or hot_age > 3:
        lines.append("- Regenerate hot memory more frequently.")
    if explicit_config == 0:
        if config_error:
            lines.append("- Fix `meta/context-spine/context-spine.json` so the runtime contract is explicit and loadable.")
        else:
            lines.append("- Add `meta/context-spine/context-spine.json` so repo policy is explicit instead of inferred.")
    if lines[-1] == "## Recommendations":
        lines.append("- No major memory-quality gaps detected.")

    out_path = (Path(args.out).expanduser() if args.out else memory_root / "memory-scorecard.md").resolve()
    try:
        published = publish_generated_artifacts(
            [
                GeneratedArtifactSpec(
                    path=out_path,
                    content="\n".join(lines) + "\n",
                    validator=markdown_heading_validator("# Memory Scorecard"),
                )
            ],
            run_id=run_handle.run_id,
        )
    except Exception as exc:
        finish_run(
            run_handle,
            status="fail",
            summary=f"Failed to publish memory scorecard: {exc}",
            artifacts=[],
            extra={"publication_error": str(exc)},
        )
        print(f"Failed to publish memory scorecard: {exc}")
        return 1

    finish_run(
        run_handle,
        status="success",
        summary=f"Generated memory scorecard with MQS {total}/100.",
        artifacts=[str(item.path) for item in published],
        extra={
            "mqs": total,
            "artifact_digests": {str(item.path): item.digest for item in published},
        },
    )
    print(f"Run ID: {run_handle.run_id}")
    print(f"Wrote scorecard to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
