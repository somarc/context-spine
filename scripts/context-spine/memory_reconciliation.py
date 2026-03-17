#!/usr/bin/env python3
from pathlib import Path
from typing import Any

from memory_events import write_event
from memory_records import write_record
from run_state import collect_git_snapshot


ACTION_CONFIG = {
    "promote": {
        "category": "promotions",
        "event_type": "promotion",
        "default_status": "promoted",
    },
    "invalidate": {
        "category": "invalidations",
        "event_type": "invalidation",
        "default_status": "stale",
    },
}

PROMOTION_STATUSES = {
    "accepted",
    "promoted",
    "updated",
}

INVALIDATION_STATUSES = {
    "contradicted",
    "invalid",
    "stale",
    "superseded",
}


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        stripped = item.strip()
        if not stripped or stripped in seen:
            continue
        seen.add(stripped)
        deduped.append(stripped)
    return deduped


def sanitize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(item) for item in value]
    return value


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return _dedupe([item.strip() for item in value.split(",") if item.strip()])


def normalize_ref(repo_root: Path, value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return ""

    candidate = Path(stripped).expanduser()
    if candidate.is_absolute():
        if candidate.exists():
            return relative_repo_path(repo_root, candidate)
        return stripped

    repo_candidate = (repo_root / candidate).resolve()
    if repo_candidate.exists():
        return relative_repo_path(repo_root, repo_candidate)
    return stripped


def normalize_refs(repo_root: Path, value: str | list[str]) -> list[str]:
    items = split_csv(value) if isinstance(value, str) else _dedupe([str(item).strip() for item in value])
    return _dedupe([normalize_ref(repo_root, item) for item in items if str(item).strip()])


def resolve_repo_files(repo_root: Path, value: str | list[str], *, label: str = "files") -> list[str]:
    items = split_csv(value) if isinstance(value, str) else _dedupe([str(item).strip() for item in value])
    if not items:
        raise ValueError(f"{label} must include at least one repo file path.")

    normalized: list[str] = []
    repo_root = repo_root.resolve()
    for item in items:
        candidate = Path(item).expanduser()
        resolved = candidate.resolve() if candidate.is_absolute() else (repo_root / candidate).resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError as exc:
            raise ValueError(f"{label} must stay inside the repo: {item}") from exc
        if not resolved.exists():
            raise ValueError(f"{label} path does not exist: {item}")
        if not resolved.is_file():
            raise ValueError(f"{label} path must be a file: {item}")
        normalized.append(relative_repo_path(repo_root, resolved))
    return _dedupe(normalized)


def build_trace_payload(
    repo_root: Path,
    run_handle: Any,
    *,
    action: str,
    summary: str,
    details: str,
    source: str,
    source_command: str,
    status: str,
    files: list[str],
    refs: list[str],
    tags: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action not in ACTION_CONFIG:
        raise ValueError(f"Unsupported reconciliation action: {action}")

    payload = {
        "action": action,
        "summary": summary.strip(),
        "details": details.strip(),
        "source": source.strip() or "unknown",
        "source_command": source_command.strip() or f"context:{action}",
        "status": status.strip() or ACTION_CONFIG[action]["default_status"],
        "run_id": run_handle.run_id,
        "files": files,
        "refs": refs,
        "tags": tags,
        "git": collect_git_snapshot(repo_root),
    }
    if extra:
        payload.update(extra)
    return payload


def write_reconciliation_trace(
    repo_root: Path,
    memory_root: Path,
    run_handle: Any,
    *,
    action: str,
    summary: str,
    details: str = "",
    source: str = "codex",
    source_command: str = "",
    status: str = "",
    files: str | list[str],
    refs: str | list[str] = "",
    tags: str | list[str] = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action not in ACTION_CONFIG:
        raise ValueError(f"Unsupported reconciliation action: {action}")

    config = ACTION_CONFIG[action]
    normalized_files = resolve_repo_files(repo_root, files)
    normalized_refs = normalize_refs(repo_root, refs)
    normalized_tags = split_csv(tags) if isinstance(tags, str) else _dedupe([str(item).strip() for item in tags])
    record_id = f"{action}-{run_handle.run_id}"

    record_payload = build_trace_payload(
        repo_root,
        run_handle,
        action=action,
        summary=summary,
        details=details,
        source=source,
        source_command=source_command,
        status=status or config["default_status"],
        files=normalized_files,
        refs=normalized_refs,
        tags=normalized_tags,
        extra=extra,
    )
    record_path = write_record(
        memory_root,
        config["category"],
        record_payload,
        record_id=record_id,
    )

    event_refs = _dedupe(
        normalized_refs
        + [
            relative_repo_path(repo_root, record_path),
            relative_repo_path(repo_root, run_handle.path),
        ]
    )
    event_payload = {
        "summary": summary.strip(),
        "details": details.strip(),
        "source": source.strip() or "unknown",
        "source_command": source_command.strip() or f"context:{action}",
        "status": status.strip() or config["default_status"],
        "run_id": run_handle.run_id,
        "record_id": record_id,
        "files": normalized_files,
        "refs": event_refs,
        "tags": normalized_tags,
    }
    if extra:
        event_payload.update(extra)

    event_path = write_event(
        memory_root,
        config["event_type"],
        event_payload,
        event_id=f"{action}-{run_handle.run_id}",
    )

    return {
        "record_id": record_id,
        "record_path": record_path,
        "event_path": event_path,
        "files": normalized_files,
        "refs": normalized_refs,
        "tags": normalized_tags,
    }
