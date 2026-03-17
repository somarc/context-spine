#!/usr/bin/env python3
import datetime as dt
import importlib.util
import sys
from pathlib import Path
from typing import Any

from context_config import load_config, resolve_repo_path
from run_state import collect_git_snapshot
from runtime_manifest import runtime_version


QUERY_MODES = {
    "active-delivery",
    "recovery",
    "promotion",
    "maintenance",
}


def _load_peer_module(name: str, filename: str):
    path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


memory_state = _load_peer_module("memory_state_for_query_core", "memory-state.py")


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    config = load_config(repo_root)
    return resolve_repo_path(repo_root, str(config.get("memory_root", "meta/context-spine"))).resolve()


def latest_matching(directory: Path, pattern: str) -> Path | None:
    files = sorted(path for path in directory.glob(pattern) if path.is_file())
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def safe_mtime(path: Path) -> str | None:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.UTC).isoformat()
    except OSError:
        return None


def resolve_state_path(repo_root: Path, item: dict[str, Any] | None) -> Path | None:
    if not item:
        return None
    raw_path = str(item.get("path", "")).strip()
    if not raw_path:
        return None
    return (repo_root / raw_path).resolve()


def parse_section(path: Path, header: str) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    capture = False
    section: list[str] = []
    for line in lines:
        if capture and line.startswith("## "):
            break
        if line == header:
            capture = True
            continue
        if capture:
            section.append(line.rstrip())
    return section


def first_meaningful_line(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            return stripped[2:].strip()
        return stripped
    return ""


def extract_bullets(lines: list[str], *, limit: int = 5) -> list[str]:
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
        if len(bullets) >= limit:
            break
    return bullets


def parse_source_of_truth(note_path: Path, repo_root: Path) -> list[Path]:
    text = note_path.read_text(encoding="utf-8")
    if "---" not in text:
        return []
    _, rest = text.split("---", 1)
    if "---" not in rest:
        return []
    frontmatter, _ = rest.split("---", 1)

    paths: list[Path] = []
    capture = False
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped == "source_of_truth:":
            capture = True
            continue
        if capture:
            if not stripped:
                continue
            if not stripped.startswith("- "):
                break
            candidate = Path(stripped[2:].strip())
            resolved = candidate if candidate.is_absolute() else (repo_root / candidate)
            resolved = resolved.resolve()
            if resolved.exists():
                paths.append(resolved)
    return paths


def to_surface(
    repo_root: Path,
    *,
    path: Path,
    kind: str,
    title: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "title": title,
        "path": memory_state.relative_repo_path(repo_root, path),
        "updated_at": safe_mtime(path),
        "reason": reason,
    }


def _dedupe_surfaces(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        path = str(item.get("path", "")).strip()
        if not path or path in seen:
            continue
        seen.add(path)
        deduped.append(item)
    return deduped


def infer_flow_state(payload: dict[str, Any]) -> dict[str, str]:
    baseline = payload["layers"]["project"]["baseline"]
    session = payload["layers"]["session"]["latest_markdown"]

    if not baseline:
        return {
            "inferred": "fresh",
            "reason": "No baseline note is available yet.",
        }
    if not session:
        return {
            "inferred": "recovery",
            "reason": "Baseline exists, but there is no latest session markdown surface.",
        }
    if session.get("age_days", 0) is not None and session.get("age_days", 0) > 2:
        return {
            "inferred": "recovery",
            "reason": "Latest session markdown is stale enough that restart quality is degraded.",
        }
    return {
        "inferred": "active",
        "reason": "Baseline and latest session are present, so restart-quality context is available.",
    }


def build_authoritative_surfaces(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []

    baseline_path = resolve_state_path(repo_root, payload["layers"]["project"]["baseline"])
    if baseline_path is not None:
        surfaces.append(
            to_surface(
                repo_root,
                path=baseline_path,
                kind="baseline",
                title=baseline_path.name,
                reason="Primary durable project model.",
            )
        )

    session_path = resolve_state_path(repo_root, payload["layers"]["session"]["latest_markdown"])
    if session_path is not None:
        surfaces.append(
            to_surface(
                repo_root,
                path=session_path,
                kind="session",
                title=session_path.name,
                reason="Latest rolling session memory for current work.",
            )
        )

    remaining = max(0, limit - len(surfaces))
    if baseline_path is not None and remaining > 0:
        for source_path in parse_source_of_truth(baseline_path, repo_root)[:remaining]:
            surfaces.append(
                to_surface(
                    repo_root,
                    path=source_path,
                    kind="source-of-truth",
                    title=source_path.name,
                    reason="Referenced from the baseline note as source of truth.",
                )
            )

    return _dedupe_surfaces(surfaces)[:limit]


def build_source_hydration(
    repo_root: Path,
    memory_root: Path,
    payload: dict[str, Any],
    authoritative_surfaces: list[dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    hydration: list[dict[str, Any]] = []

    for preferred_kind in ("baseline", "session"):
        for item in authoritative_surfaces:
            if item.get("kind") == preferred_kind:
                hydration.append(item)
                break

    hot_memory_path = memory_root / "hot-memory-index.md"
    if hot_memory_path.exists():
        hydration.append(
            to_surface(
                repo_root,
                path=hot_memory_path,
                kind="generated-hot-memory",
                title=hot_memory_path.name,
                reason="Curated working set surface.",
            )
        )

    memory_state_path = memory_root / "memory-state.json"
    if memory_state_path.exists():
        hydration.append(
            to_surface(
                repo_root,
                path=memory_state_path,
                kind="generated-state",
                title=memory_state_path.name,
                reason="Machine-readable summary of current memory layers.",
            )
        )

    for run in payload["layers"]["machine"]["runs"]["recent"][:1]:
        run_path = resolve_state_path(repo_root, {"path": run.get("path", "")})
        if run_path is None:
            continue
        hydration.append(
            to_surface(
                repo_root,
                path=run_path,
                kind="run-record",
                title=run_path.name,
                reason=f"Recent runtime activity from {run.get('command', 'unknown command')}.",
            )
        )

    for event in payload["layers"]["machine"]["events"]["recent"][:1]:
        event_path = resolve_state_path(repo_root, {"path": event.get("path", "")})
        if event_path is None:
            continue
        hydration.append(
            to_surface(
                repo_root,
                path=event_path,
                kind="event-record",
                title=event_path.name,
                reason=f"Recent high-signal event of type {event.get('event_type', 'unknown')}.",
            )
        )

    source_of_truth_count = 0
    for item in authoritative_surfaces:
        if item.get("kind") != "source-of-truth":
            continue
        hydration.append(item)
        source_of_truth_count += 1
        if source_of_truth_count >= 2:
            break

    for item in authoritative_surfaces:
        hydration.append(item)

    return _dedupe_surfaces(hydration)[:limit]


def build_active_objective(
    repo_root: Path,
    payload: dict[str, Any],
    *,
    requested_objective: str,
) -> dict[str, Any]:
    if requested_objective.strip():
        return {
            "text": requested_objective.strip(),
            "source": {"kind": "input", "path": "", "section": ""},
        }

    session_path = resolve_state_path(repo_root, payload["layers"]["session"]["latest_markdown"])
    if session_path is not None:
        next_actions = extract_bullets(parse_section(session_path, "## Next Actions"), limit=1)
        if next_actions:
            return {
                "text": next_actions[0],
                "source": {
                    "kind": "session",
                    "path": memory_state.relative_repo_path(repo_root, session_path),
                    "section": "## Next Actions",
                },
            }

        summary_line = first_meaningful_line(parse_section(session_path, "## Summary"))
        if summary_line:
            return {
                "text": summary_line,
                "source": {
                    "kind": "session",
                    "path": memory_state.relative_repo_path(repo_root, session_path),
                    "section": "## Summary",
                },
            }

    baseline_path = resolve_state_path(repo_root, payload["layers"]["project"]["baseline"])
    if baseline_path is not None:
        current_state_line = first_meaningful_line(parse_section(baseline_path, "## Current State"))
        if current_state_line:
            return {
                "text": current_state_line,
                "source": {
                    "kind": "baseline",
                    "path": memory_state.relative_repo_path(repo_root, baseline_path),
                    "section": "## Current State",
                },
            }

    return {
        "text": "Recover the current objective from the latest session, recent runs, and baseline note.",
        "source": {"kind": "inference", "path": "", "section": ""},
    }


def build_next_actions(repo_root: Path, payload: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
    session_path = resolve_state_path(repo_root, payload["layers"]["session"]["latest_markdown"])
    actions: list[dict[str, Any]] = []
    if session_path is not None:
        for action in extract_bullets(parse_section(session_path, "## Next Actions"), limit=limit):
            actions.append(
                {
                    "text": action,
                    "source": {
                        "kind": "session",
                        "path": memory_state.relative_repo_path(repo_root, session_path),
                        "section": "## Next Actions",
                    },
                }
            )
    return actions


def build_stale_or_suspect_truths(
    repo_root: Path,
    memory_root: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    baseline = payload["layers"]["project"]["baseline"]
    session = payload["layers"]["session"]["latest_markdown"]
    generated = payload["layers"]["generated"]
    recent_runs = payload["layers"]["machine"]["runs"]["recent"]

    if not baseline:
        items.append(
            {
                "severity": "high",
                "label": "Missing baseline note",
                "detail": "Durable project truth is underconstrained without a baseline spine note.",
                "path": "",
            }
        )

    if not session:
        items.append(
            {
                "severity": "medium",
                "label": "Missing latest session",
                "detail": "No latest session markdown surface is available for current work continuity.",
                "path": "",
            }
        )
    elif session.get("age_days", 0) is not None and session.get("age_days", 0) > 2:
        items.append(
            {
                "severity": "medium",
                "label": "Stale latest session",
                "detail": f"Latest session markdown is {session['age_days']} day(s) old.",
                "path": str(session.get("path", "")),
            }
        )

    hot_memory = generated.get("hot_memory", {})
    if not hot_memory.get("exists", False):
        items.append(
            {
                "severity": "medium",
                "label": "Missing hot memory index",
                "detail": "Working-set hydration is weaker without a generated hot-memory index.",
                "path": memory_state.relative_repo_path(repo_root, memory_root / "hot-memory-index.md"),
            }
        )
    elif hot_memory.get("status") in {"aging", "stale"}:
        items.append(
            {
                "severity": "low",
                "label": "Hot memory index is not fresh",
                "detail": f"Hot memory status is {hot_memory.get('status')}.",
                "path": str(hot_memory.get("path", "")),
            }
        )

    verification_present = any(
        str(run.get("family", "")) == "verification" or "verify" in str(run.get("command", "")).lower()
        for run in recent_runs
    )
    if not verification_present:
        items.append(
            {
                "severity": "low",
                "label": "No recent verification run recorded",
                "detail": "Recent runtime activity does not include a verification-family run.",
                "path": "",
            }
        )

    return items


def build_metacognitive_check(
    payload: dict[str, Any],
    stale_or_suspect_truths: list[dict[str, Any]],
) -> dict[str, Any]:
    notes: list[str] = []
    baseline = payload["layers"]["project"]["baseline"]
    session = payload["layers"]["session"]["latest_markdown"]

    if baseline:
        notes.append("Baseline note is present.")
    else:
        notes.append("Baseline note is missing, so project truth is inferred more than preferred.")

    if session:
        notes.append("Latest session markdown is available for working continuity.")
    else:
        notes.append("Latest session markdown is missing, so active objective quality is reduced.")

    if not stale_or_suspect_truths:
        notes.append("No obvious freshness or drift warnings were detected in the sampled surfaces.")

    status = "grounded"
    high_count = sum(1 for item in stale_or_suspect_truths if item.get("severity") == "high")
    medium_count = sum(1 for item in stale_or_suspect_truths if item.get("severity") == "medium")
    if high_count > 0:
        status = "weak"
    elif medium_count > 0:
        status = "partial"

    return {
        "status": status,
        "notes": notes,
    }


def build_machine_context(payload: dict[str, Any], *, limit: int) -> dict[str, Any]:
    recent_runs = []
    for run in payload["layers"]["machine"]["runs"]["recent"][:limit]:
        recent_runs.append(
            {
                "path": run.get("path", ""),
                "command": run.get("command", ""),
                "status": run.get("status", ""),
                "summary": run.get("summary", ""),
                "started_at": run.get("started_at"),
                "finished_at": run.get("finished_at"),
                "family": run.get("family", ""),
                "signals": run.get("signals", []),
            }
        )

    recent_events = []
    for event in payload["layers"]["machine"]["events"]["recent"][:limit]:
        recent_events.append(
            {
                "path": event.get("path", ""),
                "event_type": event.get("event_type", ""),
                "summary": event.get("summary", ""),
                "recorded_at": event.get("recorded_at"),
                "source": event.get("source", ""),
                "status": event.get("status", ""),
            }
        )

    return {
        "recent_runs": recent_runs,
        "recent_events": recent_events,
    }


def build_query_payload(
    repo_root: Path,
    memory_root: Path,
    *,
    mode: str = "active-delivery",
    requested_objective: str = "",
    limit: int = 6,
    exclude_run_id: str = "",
) -> dict[str, Any]:
    normalized_mode = mode.strip().lower()
    if normalized_mode not in QUERY_MODES:
        raise ValueError(f"Unsupported query mode: {mode}")

    state_payload = memory_state.build_state(repo_root, memory_root, exclude_run_id=exclude_run_id)
    flow_state = infer_flow_state(state_payload)
    authoritative_surfaces = build_authoritative_surfaces(repo_root, state_payload, limit=limit)
    source_hydration = build_source_hydration(
        repo_root,
        memory_root,
        state_payload,
        authoritative_surfaces,
        limit=limit,
    )
    stale_or_suspect_truths = build_stale_or_suspect_truths(repo_root, memory_root, state_payload)
    next_actions = build_next_actions(repo_root, state_payload, limit=limit)
    active_objective = build_active_objective(
        repo_root,
        state_payload,
        requested_objective=requested_objective,
    )
    metacognitive_check = build_metacognitive_check(state_payload, stale_or_suspect_truths)
    machine_context = build_machine_context(state_payload, limit=min(limit, 3))

    return {
        "query_schema": "context-spine.query.v1",
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "runtime_version": runtime_version(repo_root),
        "repo_root": str(repo_root.resolve()),
        "memory_root": str(memory_root.resolve()),
        "mode": normalized_mode,
        "requested_objective": requested_objective.strip(),
        "git": collect_git_snapshot(repo_root),
        "flow_state": {
            "requested": normalized_mode,
            **flow_state,
        },
        "active_objective": active_objective,
        "authoritative_surfaces": authoritative_surfaces,
        "source_hydration": source_hydration,
        "working_set": source_hydration[:limit],
        "machine_context": machine_context,
        "stale_or_suspect_truths": stale_or_suspect_truths,
        "next_actions": next_actions,
        "critical_path": next_actions[:3],
        "metacognitive_check": metacognitive_check,
        "memory_state_export": state_payload.get("exports", {}),
    }


def build_rehydrate_payload(
    repo_root: Path,
    memory_root: Path,
    *,
    mode: str = "active-delivery",
    requested_objective: str = "",
    limit: int = 6,
    exclude_run_id: str = "",
) -> dict[str, Any]:
    query_payload = build_query_payload(
        repo_root,
        memory_root,
        mode=mode,
        requested_objective=requested_objective,
        limit=limit,
        exclude_run_id=exclude_run_id,
    )
    return {
        "rehydrate_schema": "context-spine.rehydrate.v1",
        "generated_at": query_payload["generated_at"],
        "runtime_version": query_payload["runtime_version"],
        "repo_root": query_payload["repo_root"],
        "memory_root": query_payload["memory_root"],
        "mode": query_payload["mode"],
        "requested_objective": query_payload["requested_objective"],
        "active_objective": query_payload["active_objective"],
        "authoritative_surfaces": query_payload["authoritative_surfaces"],
        "source_hydration": query_payload["source_hydration"],
        "working_set": query_payload["working_set"],
        "machine_context": query_payload["machine_context"],
        "flow_state": query_payload["flow_state"],
        "critical_path": query_payload["critical_path"],
        "stale_or_suspect_truths": query_payload["stale_or_suspect_truths"],
        "metacognitive_check": query_payload["metacognitive_check"],
        "next_actions": query_payload["next_actions"],
    }
