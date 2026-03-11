#!/usr/bin/env python3
import argparse
import datetime as dt
import re
from pathlib import Path


QMD_PATTERN = re.compile(r"(qmd://|\bqmd\b)", re.IGNORECASE)
SESSION_LIKE = re.compile(r"(session|day)\.md$", re.IGNORECASE)
TIME_HEADER = re.compile(r"^## \d{2}:\d{2}:\d{2}")


def default_memory_root() -> Path:
    return Path(__file__).resolve().parents[2] / "meta" / "context-spine"


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


def weighted_score(coverage, early, observation_rate, hooks, freshness):
    return round(
        coverage * 0.35 +
        early * 0.20 +
        observation_rate * 0.20 +
        hooks * 0.10 +
        freshness * 0.15,
        1,
    )


def format_percent(value):
    return f"{value:.1f}%"


def main():
    parser = argparse.ArgumentParser(description="Score Context Spine memory quality.")
    parser.add_argument("--root", default="", help="Override memory root directory")
    parser.add_argument("--out", default="", help="Output scorecard path")
    args = parser.parse_args()

    memory_root = Path(args.root).expanduser() if args.root else default_memory_root()
    sessions = session_stats(memory_root / "sessions")
    observations = observation_stats(memory_root / "observations")
    hot_age = hot_memory_age(memory_root / "hot-memory-index.md")
    hooks = hook_score(Path(__file__).resolve().parent / "bootstrap.sh")

    coverage = percentage(sessions["with_qmd"], sessions["total"])
    early = percentage(sessions["early_qmd"], sessions["total"])
    observation_rate = percentage(observations["qmd_entries"], observations["entries"])
    freshness = freshness_score(hot_age)
    total = weighted_score(coverage, early, observation_rate, hooks, freshness)

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
        "",
        "## Hooks & Freshness",
        f"- Bootstrap script present: {'yes' if hooks > 0 else 'no'}",
    ]
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
    if hooks == 0:
        lines.append("- Add or restore the bootstrap hook.")
    if hot_age is None or hot_age > 3:
        lines.append("- Regenerate hot memory more frequently.")
    if lines[-1] == "## Recommendations":
        lines.append("- No major memory-quality gaps detected.")

    out_path = Path(args.out).expanduser() if args.out else memory_root / "memory-scorecard.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote scorecard to {out_path}")


if __name__ == "__main__":
    main()
