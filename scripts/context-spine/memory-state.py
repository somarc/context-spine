#!/usr/bin/env python3
import argparse
import datetime as dt
import html
import json
from pathlib import Path

from context_config import load_config, resolve_repo_path
from generated_artifact import (
    GeneratedArtifactSpec,
    publish_generated_artifacts,
    validate_json_artifact,
    validate_nonempty_text,
)
from memory_events import events_root, iter_event_paths, latest_events
from memory_records import iter_record_paths, latest_record, records_root
from run_state import finish_run, start_run


MACHINE_RECORD_CATEGORIES = (
    "sessions",
    "observations",
    "evidence",
    "promotions",
    "invalidations",
)


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def safe_mtime(path: Path) -> dt.datetime | None:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.UTC)
    except OSError:
        return None


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def latest_matching(directory: Path, pattern: str) -> Path | None:
    files = sorted(path for path in directory.glob(pattern) if path.is_file())
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def generated_surface(path: Path, repo_root: Path) -> dict:
    stamp = safe_mtime(path)
    age_days = None
    if stamp is not None:
        age_days = round((dt.datetime.now(dt.UTC) - stamp).total_seconds() / 86400, 2)
    return {
        "exists": path.exists(),
        "path": relative_repo_path(repo_root, path),
        "updated_at": stamp.isoformat() if stamp else None,
        "age_days": age_days,
        "status": freshness_status(path.exists(), age_days),
    }


def project_counts(repo_root: Path) -> dict:
    return {
        "adr_count": len(list((repo_root / "docs" / "adr").glob("*.md"))),
        "runbook_count": len(list((repo_root / "docs" / "runbooks").glob("*.md"))),
        "diagram_count": len(list((repo_root / ".agent" / "diagrams").glob("*.html"))),
        "evidence_pack_count": len(list((repo_root / "meta" / "context-spine" / "evidence-packs").rglob("*.md"))),
    }


def latest_session_markdown(memory_root: Path, repo_root: Path) -> dict | None:
    session_path = latest_matching(memory_root / "sessions", "*-session.md")
    if session_path is None:
        return None
    stamp = safe_mtime(session_path)
    age_days = None
    if stamp is not None:
        age_days = round((dt.datetime.now(dt.UTC) - stamp).total_seconds() / 86400, 2)
    return {
        "path": relative_repo_path(repo_root, session_path),
        "updated_at": stamp.isoformat() if stamp else None,
        "age_days": age_days,
        "title": session_path.name,
    }


def latest_baseline(memory_root: Path, repo_root: Path) -> dict | None:
    baseline = latest_matching(memory_root, "spine-notes-*.md")
    if baseline is None:
        return None
    stamp = safe_mtime(baseline)
    age_days = None
    if stamp is not None:
        age_days = round((dt.datetime.now(dt.UTC) - stamp).total_seconds() / 86400, 2)
    return {
        "path": relative_repo_path(repo_root, baseline),
        "updated_at": stamp.isoformat() if stamp else None,
        "age_days": age_days,
        "title": baseline.name,
    }


def record_category_state(memory_root: Path, repo_root: Path, category: str) -> dict:
    paths = iter_record_paths(memory_root, category)
    latest = latest_record(memory_root, category)
    payload = {
        "count": len(paths),
        "root": relative_repo_path(repo_root, records_root(memory_root) / category),
        "latest": None,
    }
    if latest is not None:
        latest_path, record = latest
        payload["latest"] = {
            "path": relative_repo_path(repo_root, latest_path),
            "record_id": record.get("record_id", ""),
            "recorded_at": record.get("recorded_at"),
            "summary": record.get("summary") or record.get("title") or record.get("job") or "",
        }
    return payload


def run_state(memory_root: Path, repo_root: Path, limit: int = 6, exclude_run_id: str = "") -> dict:
    run_root = memory_root / "runs"
    if not run_root.is_dir():
        return {"count": 0, "recent": []}

    items: list[tuple[float, dict]] = []
    for path in run_root.rglob("*.json"):
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if exclude_run_id and payload.get("run_id") == exclude_run_id:
            continue
        automatic_capture = payload.get("automatic_capture", {})
        classification = automatic_capture.get("classification", {})
        git_snapshot = automatic_capture.get("git_finish") or automatic_capture.get("git_start") or {}
        step_results = payload.get("extra", {}).get("steps", [])
        stamp = safe_mtime(path)
        items.append(
            (
                stamp.timestamp() if stamp is not None else 0,
                {
                    "path": relative_repo_path(repo_root, path),
                    "run_id": payload.get("run_id", ""),
                    "command": payload.get("command", ""),
                    "status": payload.get("status", "unknown"),
                    "started_at": payload.get("started_at"),
                    "finished_at": payload.get("finished_at"),
                    "summary": payload.get("summary", ""),
                    "artifact_count": len(payload.get("artifacts", [])),
                    "family": classification.get("family", ""),
                    "signals": classification.get("signals", []),
                    "git": {
                        "available": git_snapshot.get("available", False),
                        "branch": git_snapshot.get("branch", ""),
                        "head_short": git_snapshot.get("head_short", ""),
                        "dirty": git_snapshot.get("dirty", False),
                        "changed_path_count": git_snapshot.get("changed_path_count", 0),
                        "diff_vs_head": git_snapshot.get("diff_vs_head", {}),
                    },
                    "step_count": len(step_results),
                    "failed_step_count": sum(1 for step in step_results if step.get("status") != "success"),
                },
            )
        )

    items.sort(key=lambda item: item[0], reverse=True)
    return {"count": len(items), "recent": [payload for _, payload in items[:limit]]}


def event_state(memory_root: Path, repo_root: Path, limit: int = 6) -> dict:
    recent = []
    for path, payload in latest_events(memory_root, limit=limit):
        recent.append(
            {
                "path": relative_repo_path(repo_root, path),
                "event_id": payload.get("event_id", ""),
                "event_type": payload.get("event_type", ""),
                "recorded_at": payload.get("recorded_at"),
                "summary": payload.get("summary", ""),
                "source": payload.get("source", ""),
                "status": payload.get("status", ""),
                "run_id": payload.get("run_id", ""),
                "file_count": len(payload.get("files", [])),
                "ref_count": len(payload.get("refs", [])),
                "tags": payload.get("tags", []),
            }
        )
    return {
        "count": len(iter_event_paths(memory_root)),
        "root": relative_repo_path(repo_root, events_root(memory_root)),
        "recent": recent,
    }


def freshness_status(exists: bool, age_days: float | None) -> str:
    if not exists:
        return "missing"
    if age_days is None:
        return "unknown"
    if age_days <= 2:
        return "fresh"
    if age_days <= 7:
        return "aging"
    return "stale"


def summarize_generated_health(generated: dict[str, dict]) -> dict:
    values = list(generated.values())
    present = sum(1 for item in values if item["exists"])
    fresh = sum(1 for item in values if item["status"] == "fresh")
    aging = sum(1 for item in values if item["status"] == "aging")
    stale = sum(1 for item in values if item["status"] == "stale")
    missing = sum(1 for item in values if item["status"] == "missing")
    return {
        "present": present,
        "fresh": fresh,
        "aging": aging,
        "stale": stale,
        "missing": missing,
        "total": len(values),
    }


def build_state(
    repo_root: Path,
    memory_root: Path,
    *,
    json_path: Path | None = None,
    html_path: Path | None = None,
    exclude_run_id: str = "",
) -> dict:
    machine_records = {
        category: record_category_state(memory_root, repo_root, category)
        for category in MACHINE_RECORD_CATEGORIES
    }
    events = event_state(memory_root, repo_root)
    runs = run_state(memory_root, repo_root, exclude_run_id=exclude_run_id)
    generated = {
        "hot_memory": generated_surface(memory_root / "hot-memory-index.md", repo_root),
        "memory_scorecard": generated_surface(memory_root / "memory-scorecard.md", repo_root),
        "doctor_report": generated_surface(memory_root / "doctor-report.md", repo_root),
        "rollout_report": generated_surface(memory_root / "rollout-report.md", repo_root),
        "upgrade_report": generated_surface(memory_root / "upgrade-report.md", repo_root),
    }
    return {
        "state_schema": "context-spine.memory-state.v1",
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "repo_root": str(repo_root.resolve()),
        "memory_root": str(memory_root.resolve()),
        "exports": {
            "json": relative_repo_path(repo_root, (json_path or memory_root / "memory-state.json").resolve()),
            "html": relative_repo_path(repo_root, (html_path or memory_root / "memory-state.html").resolve()),
        },
        "layers": {
            "session": {
                "latest_markdown": latest_session_markdown(memory_root, repo_root),
                "records": machine_records["sessions"],
            },
            "project": {
                "baseline": latest_baseline(memory_root, repo_root),
                **project_counts(repo_root),
            },
            "machine": {
                "records": machine_records,
                "events": events,
                "runs": runs,
            },
            "generated": generated,
        },
        "summary": {
            "project_truth_surfaces": project_counts(repo_root),
            "machine_record_total": sum(item["count"] for item in machine_records.values()),
            "machine_event_total": events["count"],
            "machine_capture_total": sum(item["count"] for item in machine_records.values()) + events["count"],
            "run_total": runs["count"],
            "generated_health": summarize_generated_health(generated),
        },
    }


def escape_html(value: object) -> str:
    return html.escape(str(value))


def render_path_chip(path: str) -> str:
    return f'<span class="chip"><code>{escape_html(path)}</code></span>'


def render_optional_file(item: dict | None, empty_label: str) -> str:
    if not item:
        return f'<div class="surface surface-missing"><div class="surface-head"><strong>{escape_html(empty_label)}</strong><span class="badge badge-missing">missing</span></div><p>No artifact is available yet.</p></div>'
    age = "unknown age" if item.get("age_days") is None else f'{item["age_days"]} day(s) old'
    return (
        '<div class="surface">'
        f'<div class="surface-head"><strong>{escape_html(item.get("title", "artifact"))}</strong>'
        '<span class="badge badge-fresh">present</span></div>'
        f'<p>{escape_html(age)}</p>'
        f'{render_path_chip(str(item.get("path", "")))}'
        "</div>"
    )


def render_record_card(label: str, payload: dict) -> str:
    latest = payload.get("latest")
    latest_markup = "<p>No records captured yet.</p>"
    if latest:
        summary = latest.get("summary") or "No summary captured."
        latest_markup = (
            f'<p>Latest record: <strong>{escape_html(latest.get("record_id", ""))}</strong></p>'
            f'<p>{escape_html(summary)}</p>'
            f'{render_path_chip(str(latest.get("path", "")))}'
        )
    return (
        '<div class="surface">'
        f'<div class="surface-head"><strong>{escape_html(label)}</strong>'
        f'<span class="badge badge-neutral">{escape_html(payload.get("count", 0))} record(s)</span></div>'
        f'<p>Record root: <code>{escape_html(payload.get("root", ""))}</code></p>'
        f"{latest_markup}"
        "</div>"
    )


def render_generated_card(label: str, payload: dict) -> str:
    status = payload.get("status", "unknown")
    badge_class = {
        "fresh": "badge-fresh",
        "aging": "badge-aging",
        "stale": "badge-stale",
        "missing": "badge-missing",
    }.get(status, "badge-neutral")
    updated = payload.get("updated_at") or "not generated yet"
    age = "unknown age" if payload.get("age_days") is None else f'{payload["age_days"]} day(s) old'
    detail = age if payload.get("exists") else "Generate it when the surface matters."
    return (
        f'<div class="surface {"surface-missing" if status == "missing" else ""}">'
        f'<div class="surface-head"><strong>{escape_html(label)}</strong>'
        f'<span class="badge {badge_class}">{escape_html(status)}</span></div>'
        f'<p>{escape_html(detail)}</p>'
        f'<p class="meta-line">Updated: {escape_html(updated)}</p>'
        f'{render_path_chip(str(payload.get("path", "")))}'
        "</div>"
    )


def render_event_card(payload: dict) -> str:
    status = payload.get("status") or payload.get("event_type", "event")
    badge_class = {
        "success": "badge-fresh",
        "fail": "badge-stale",
        "verification": "badge-fresh",
        "promotion": "badge-fresh",
        "decision": "badge-neutral",
        "edit-burst": "badge-aging",
        "retrieval": "badge-neutral",
        "invalidation": "badge-stale",
        "context-shift": "badge-aging",
    }.get(status, "badge-neutral")
    meta_bits = [
        f"Source: {payload.get('source') or 'unknown'}",
        f"Files: {payload.get('file_count', 0)}",
        f"Refs: {payload.get('ref_count', 0)}",
    ]
    return (
        '<div class="surface">'
        f'<div class="surface-head"><strong>{escape_html(payload.get("event_type", "event"))}</strong>'
        f'<span class="badge {badge_class}">{escape_html(status)}</span></div>'
        f'<p>{escape_html(payload.get("summary", ""))}</p>'
        f'<p class="meta-line">{escape_html(" | ".join(meta_bits))}</p>'
        f'<p class="meta-line">Recorded: {escape_html(payload.get("recorded_at", ""))}</p>'
        f'{render_path_chip(str(payload.get("path", "")))}'
        "</div>"
    )


def render_run_card(payload: dict) -> str:
    status = payload.get("status", "unknown")
    badge_class = {
        "success": "badge-fresh",
        "warn": "badge-aging",
        "fail": "badge-stale",
        "running": "badge-neutral",
    }.get(status, "badge-neutral")
    summary = payload.get("summary") or "No summary recorded."
    git = payload.get("git", {})
    git_line = ""
    if git.get("available"):
        dirty_label = "dirty" if git.get("dirty") else "clean"
        git_line = (
            f'<p class="meta-line">Git: {escape_html(git.get("branch", "unknown"))} @ '
            f'{escape_html(git.get("head_short", ""))} | {escape_html(dirty_label)} '
            f'({escape_html(git.get("changed_path_count", 0))} path(s))</p>'
        )
    diff = git.get("diff_vs_head", {}) if isinstance(git, dict) else {}
    diff_line = ""
    if diff and diff.get("raw"):
        diff_line = f'<p class="meta-line">Diff vs HEAD: {escape_html(diff.get("raw", ""))}</p>'
    signals = payload.get("signals", [])
    signal_line = ""
    if payload.get("family") or signals:
        signal_line = (
            f'<p class="meta-line">Family: {escape_html(payload.get("family", "general"))} | '
            f'Signals: {escape_html(", ".join(signals) if signals else "none")}</p>'
        )
    step_line = ""
    if payload.get("step_count", 0):
        step_line = (
            f'<p class="meta-line">Steps: {escape_html(payload.get("step_count", 0))} | '
            f'Failures: {escape_html(payload.get("failed_step_count", 0))}</p>'
        )
    return (
        '<div class="surface">'
        f'<div class="surface-head"><strong>{escape_html(payload.get("command", "run"))}</strong>'
        f'<span class="badge {badge_class}">{escape_html(status)}</span></div>'
        f'<p>{escape_html(summary)}</p>'
        f"{signal_line}"
        f"{git_line}"
        f"{diff_line}"
        f"{step_line}"
        f'<p class="meta-line">Artifacts: {escape_html(payload.get("artifact_count", 0))} | Started: {escape_html(payload.get("started_at", ""))}</p>'
        f'{render_path_chip(str(payload.get("path", "")))}'
        "</div>"
    )


def render_memory_state_html(payload: dict) -> str:
    project = payload["layers"]["project"]
    session = payload["layers"]["session"]
    machine = payload["layers"]["machine"]["records"]
    events = payload["layers"]["machine"]["events"]
    runs = payload["layers"]["machine"]["runs"]
    generated = payload["layers"]["generated"]
    summary = payload["summary"]
    generated_health = summary["generated_health"]

    session_markdown = render_optional_file(session.get("latest_markdown"), "Latest session markdown")
    baseline = render_optional_file(project.get("baseline"), "Baseline note")
    machine_total = summary["machine_capture_total"]
    event_cards = "".join(render_event_card(item) for item in events["recent"]) or (
        '<div class="surface surface-missing"><div class="surface-head"><strong>Recent events</strong><span class="badge badge-missing">missing</span></div><p>No high-signal events have been captured yet.</p></div>'
    )
    generated_cards = "".join(
        render_generated_card(label.replace("_", " ").title(), item)
        for label, item in generated.items()
    )
    record_cards = "".join(
        render_record_card(label.title(), payload)
        for label, payload in machine.items()
    )
    run_cards = "".join(render_run_card(item) for item in runs["recent"]) or (
        '<div class="surface surface-missing"><div class="surface-head"><strong>Recent runs</strong><span class="badge badge-missing">missing</span></div><p>No run history is available yet.</p></div>'
    )
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Context Spine Memory State</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {{
        --bg: #eef4f6;
        --surface: rgba(255, 255, 255, 0.9);
        --surface-strong: rgba(255, 255, 255, 0.98);
        --text: #102530;
        --text-dim: #49636f;
        --border: rgba(16, 37, 48, 0.12);
        --teal: #0f766e;
        --teal-soft: rgba(15, 118, 110, 0.12);
        --amber: #b45309;
        --amber-soft: rgba(180, 83, 9, 0.12);
        --rose: #be123c;
        --rose-soft: rgba(190, 18, 60, 0.11);
        --slate: #1d4ed8;
        --slate-soft: rgba(29, 78, 216, 0.1);
        --shadow: 0 24px 60px rgba(16, 37, 48, 0.12);
        --grid: rgba(16, 37, 48, 0.06);
      }}

      * {{ box-sizing: border-box; }}

      body {{
        margin: 0;
        color: var(--text);
        font-family: "IBM Plex Sans", system-ui, sans-serif;
        background:
          radial-gradient(circle at top left, rgba(15, 118, 110, 0.12), transparent 24%),
          radial-gradient(circle at top right, rgba(180, 83, 9, 0.1), transparent 28%),
          linear-gradient(var(--grid) 1px, transparent 1px),
          linear-gradient(90deg, var(--grid) 1px, transparent 1px),
          linear-gradient(180deg, #f8fbfc 0%, var(--bg) 100%);
        background-size: auto, auto, 24px 24px, 24px 24px, auto;
      }}

      main {{
        width: min(1280px, calc(100vw - 40px));
        margin: 20px auto 64px;
      }}

      .hero,
      .panel {{
        border: 1px solid var(--border);
        border-radius: 28px;
        background: var(--surface);
        box-shadow: var(--shadow);
        backdrop-filter: blur(12px);
      }}

      .hero {{
        padding: 32px;
        margin-bottom: 22px;
      }}

      .eyebrow,
      .kpi-label,
      .chip,
      code {{
        font-family: "IBM Plex Mono", monospace;
      }}

      .eyebrow {{
        font-size: 12px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--teal);
      }}

      h1,
      h2,
      h3,
      p {{
        margin: 0;
      }}

      h1 {{
        font-size: clamp(2.8rem, 6vw, 4.8rem);
        line-height: 0.92;
        max-width: 10ch;
      }}

      h2 {{
        font-size: 1.45rem;
        line-height: 1.2;
      }}

      h3 {{
        font-size: 1rem;
        line-height: 1.3;
      }}

      p {{
        color: var(--text-dim);
        line-height: 1.65;
      }}

      .lede {{
        margin-top: 16px;
        max-width: 72ch;
        font-size: 1.06rem;
      }}

      .hero-grid,
      .kpi-grid,
      .layer-grid,
      .surface-grid {{
        display: grid;
        gap: 18px;
      }}

      .hero-grid {{
        grid-template-columns: 1.2fr 0.8fr;
        align-items: start;
      }}

      .kpi-grid {{
        grid-template-columns: repeat(4, minmax(0, 1fr));
        margin-top: 22px;
      }}

      .layer-grid {{
        grid-template-columns: 1fr 1fr;
      }}

      .surface-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .panel {{
        padding: 24px;
        margin-top: 22px;
      }}

      .section-head {{
        display: grid;
        gap: 8px;
        margin-bottom: 18px;
      }}

      .kpi,
      .layer,
      .surface,
      .callout {{
        border: 1px solid var(--border);
        border-radius: 24px;
        background: var(--surface-strong);
        padding: 18px;
      }}

      .kpi strong {{
        display: block;
        font-size: 2rem;
        line-height: 1;
      }}

      .kpi-label {{
        display: block;
        margin-bottom: 10px;
        color: var(--text-dim);
        font-size: 12px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
      }}

      .kpi.project {{ background: linear-gradient(180deg, var(--slate-soft), rgba(255,255,255,0.95)); }}
      .kpi.session {{ background: linear-gradient(180deg, var(--amber-soft), rgba(255,255,255,0.95)); }}
      .kpi.machine {{ background: linear-gradient(180deg, var(--teal-soft), rgba(255,255,255,0.95)); }}
      .kpi.generated {{ background: linear-gradient(180deg, var(--rose-soft), rgba(255,255,255,0.95)); }}

      .layer {{
        min-height: 240px;
      }}

      .layer.project {{ background: linear-gradient(180deg, rgba(29, 78, 216, 0.08), rgba(255,255,255,0.96)); }}
      .layer.machine {{ background: linear-gradient(180deg, rgba(15, 118, 110, 0.08), rgba(255,255,255,0.96)); }}

      .surface {{
        display: grid;
        gap: 10px;
      }}

      .surface-missing {{
        opacity: 0.76;
        border-style: dashed;
      }}

      .surface-head {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
      }}

      .badge,
      .chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        font-size: 0.78rem;
      }}

      .badge-fresh {{ background: var(--teal-soft); color: var(--teal); }}
      .badge-aging {{ background: var(--amber-soft); color: var(--amber); }}
      .badge-stale {{ background: var(--rose-soft); color: var(--rose); }}
      .badge-missing {{ background: rgba(16, 37, 48, 0.08); color: var(--text-dim); }}
      .badge-neutral {{ background: rgba(29, 78, 216, 0.08); color: var(--slate); }}

      .chip {{
        width: fit-content;
        background: rgba(255, 255, 255, 0.7);
      }}

      code {{
        font-size: 0.86em;
      }}

      .meta-line {{
        font-size: 0.94rem;
      }}

      ul {{
        margin: 12px 0 0;
        padding-left: 18px;
      }}

      li {{
        color: var(--text-dim);
        line-height: 1.6;
      }}

      li + li {{
        margin-top: 6px;
      }}

      @media (max-width: 980px) {{
        .hero-grid,
        .kpi-grid,
        .layer-grid,
        .surface-grid {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div class="hero-grid">
          <div>
            <div class="eyebrow">Context Spine Visual Memory State</div>
            <h1>Layered memory, explained.</h1>
            <p class="lede">
              This generated view turns the current memory state into a readable surface for people:
              what project truth exists, what session state is active, what machine records have been captured,
              and how fresh the generated aids are.
            </p>
          </div>
          <div class="callout">
            <h2>Exports</h2>
            <ul>
              <li>JSON state: <code>{escape_html(payload["exports"]["json"])}</code></li>
              <li>HTML view: <code>{escape_html(payload["exports"]["html"])}</code></li>
              <li>Generated at: <code>{escape_html(payload["generated_at"])}</code></li>
              <li>Repo root: <code>{escape_html(payload["repo_root"])}</code></li>
            </ul>
          </div>
        </div>

        <div class="kpi-grid">
          <div class="kpi project">
            <span class="kpi-label">Project Truth</span>
            <strong>{escape_html(project["adr_count"] + project["runbook_count"] + project["diagram_count"])}</strong>
            <p>ADRs, runbooks, and diagrams anchored to the repo.</p>
          </div>
          <div class="kpi session">
            <span class="kpi-label">Session State</span>
            <strong>{escape_html(session["records"]["count"])}</strong>
            <p>Session records captured, with the latest markdown session shown below.</p>
          </div>
          <div class="kpi machine">
            <span class="kpi-label">Machine Capture</span>
            <strong>{escape_html(machine_total)}</strong>
            <p>Structured records and events, with {escape_html(summary["run_total"])} captured run(s).</p>
          </div>
          <div class="kpi generated">
            <span class="kpi-label">Generated Aids</span>
            <strong>{escape_html(generated_health["present"])}/{escape_html(generated_health["total"])}</strong>
            <p>{escape_html(generated_health["fresh"])} fresh, {escape_html(generated_health["aging"])} aging, {escape_html(generated_health["stale"])} stale.</p>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div class="eyebrow">Layer Map</div>
          <h2>Human truth and machine memory stay separate on purpose.</h2>
          <p>The project truth layer remains inspectable in files, while the machine layer stays structured and queryable.</p>
        </div>
        <div class="layer-grid">
          <div class="layer project">
            <h3>Project Truth</h3>
            <ul>
              <li>Baseline note: {escape_html(project["baseline"]["title"] if project["baseline"] else "missing")}</li>
              <li>{escape_html(project["adr_count"])} ADR(s)</li>
              <li>{escape_html(project["runbook_count"])} runbook(s)</li>
              <li>{escape_html(project["diagram_count"])} diagram(s)</li>
              <li>{escape_html(project["evidence_pack_count"])} evidence pack(s)</li>
            </ul>
          </div>
          <div class="layer machine">
            <h3>Machine Layer</h3>
            <ul>
              <li>{escape_html(machine["sessions"]["count"])} session record(s)</li>
              <li>{escape_html(machine["observations"]["count"])} observation record(s)</li>
              <li>{escape_html(machine["evidence"]["count"])} evidence record(s)</li>
              <li>{escape_html(machine["promotions"]["count"])} promotion record(s)</li>
              <li>{escape_html(machine["invalidations"]["count"])} invalidation record(s)</li>
              <li>{escape_html(events["count"])} high-signal event(s)</li>
              <li>Generated aids summarized with freshness status</li>
              <li>Designed for query and visual explanation, not for durable truth by itself</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div class="eyebrow">Key Surfaces</div>
          <h2>Open these first when you need to re-anchor quickly.</h2>
        </div>
        <div class="surface-grid">
          {baseline}
          {session_markdown}
        </div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div class="eyebrow">Machine Records</div>
          <h2>Structured capture for Codex and other runtime consumers.</h2>
          <p>These records are the first machine-usable layer next to markdown and durable notes.</p>
        </div>
        <div class="surface-grid">
          {record_cards}
        </div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div class="eyebrow">High-Signal Events</div>
          <h2>Sparse work events capture what mattered without becoming a log tail.</h2>
          <p>Use explicit event capture for meaningful edit bursts, retrieval passes, decisions, invalidations, or context shifts.</p>
        </div>
        <div class="surface-grid">
          {event_cards}
        </div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div class="eyebrow">Recent Runtime Activity</div>
          <h2>Automatic command capture shows what maintenance actually happened.</h2>
          <p>The state layer now surfaces recent run history so verification and maintenance stop living only in terminal scrollback.</p>
        </div>
        <div class="surface-grid">
          {run_cards}
        </div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div class="eyebrow">Generated Aids</div>
          <h2>Freshness status for the current helper surfaces.</h2>
          <p>Generated aids can be regenerated safely. They help reading and recovery, but they do not replace durable truth.</p>
        </div>
        <div class="surface-grid">
          {generated_cards}
        </div>
      </section>
    </main>
  </body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the current layered Context Spine memory state.")
    parser.add_argument("--root", default="", help="Override memory root directory")
    parser.add_argument("--out", default="", help="Output path for machine-readable state JSON")
    parser.add_argument("--html-out", default="", help="Output path for visual state HTML")
    args = parser.parse_args()

    repo_root = default_repo_root()
    config = load_config(repo_root)
    memory_root = (
        Path(args.root).expanduser()
        if args.root
        else resolve_repo_path(repo_root, str(config.get("memory_root", default_memory_root(repo_root))))
    ).resolve()
    out_path = (Path(args.out).expanduser() if args.out else memory_root / "memory-state.json").resolve()
    html_path = (Path(args.html_out).expanduser() if args.html_out else memory_root / "memory-state.html").resolve()

    run_handle = start_run(
        repo_root,
        memory_root,
        "context:state",
        args=vars(args),
    )
    payload = build_state(
        repo_root,
        memory_root,
        json_path=out_path,
        html_path=html_path,
        exclude_run_id=run_handle.run_id,
    )
    content = json.dumps(payload, indent=2) + "\n"
    html_content = render_memory_state_html(payload)
    try:
        published = publish_generated_artifacts(
            [
                GeneratedArtifactSpec(
                    path=out_path,
                    content=content,
                    validator=validate_json_artifact,
                ),
                GeneratedArtifactSpec(
                    path=html_path,
                    content=html_content,
                    validator=validate_nonempty_text,
                ),
            ],
            run_id=run_handle.run_id,
        )
    except Exception as exc:
        finish_run(
            run_handle,
            status="fail",
            summary=f"Failed to publish memory state: {exc}",
            artifacts=[],
            extra={"publication_error": str(exc)},
        )
        print(f"Failed to publish memory state: {exc}")
        return 1

    finish_run(
        run_handle,
        status="success",
        summary="Exported layered memory state.",
        artifacts=[str(item.path) for item in published],
        extra={"artifact_digests": {str(item.path): item.digest for item in published}},
    )
    print(f"Run ID: {run_handle.run_id}")
    print(f"Wrote memory state to {out_path}")
    print(f"Wrote visual memory state to {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
