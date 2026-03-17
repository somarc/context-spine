#!/usr/bin/env python3
import datetime as dt
import json
import re
import uuid
from pathlib import Path
from typing import Any


EVENT_TYPES = {
    "verification",
    "edit-burst",
    "retrieval",
    "decision",
    "invalidation",
    "context-shift",
}


def _sanitize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    return value


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "event"


def events_root(memory_root: Path) -> Path:
    return memory_root / "events"


def write_event(
    memory_root: Path,
    event_type: str,
    payload: dict[str, Any],
    *,
    event_id: str = "",
    recorded_at: dt.datetime | None = None,
) -> Path:
    normalized_type = event_type.strip().lower()
    if normalized_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")

    stamp = (recorded_at or dt.datetime.now(dt.UTC)).astimezone(dt.UTC).replace(microsecond=0)
    event_id = event_id or f"{_slug(normalized_type)}-{stamp.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    event_dir = events_root(memory_root) / stamp.strftime("%Y-%m-%d")
    event_dir.mkdir(parents=True, exist_ok=True)
    event_path = event_dir / f"{_slug(event_id)}.json"
    body = {
        "event_schema": "context-spine.memory-event.v1",
        "event_type": normalized_type,
        "event_id": event_id,
        "recorded_at": stamp.isoformat(),
        **_sanitize(payload),
    }
    event_path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return event_path


def iter_event_paths(memory_root: Path) -> list[Path]:
    root = events_root(memory_root)
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def load_event(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_events(memory_root: Path, *, limit: int = 6, event_types: set[str] | None = None) -> list[tuple[Path, dict[str, Any]]]:
    items: list[tuple[float, Path, dict[str, Any]]] = []
    for path in iter_event_paths(memory_root):
        payload = load_event(path)
        event_type = str(payload.get("event_type", "")).strip().lower()
        if event_types and event_type not in event_types:
            continue
        try:
            recorded = dt.datetime.fromisoformat(str(payload.get("recorded_at", ""))).timestamp()
        except ValueError:
            recorded = path.stat().st_mtime
        items.append((recorded, path, payload))
    items.sort(key=lambda item: item[0], reverse=True)
    return [(path, payload) for _, path, payload in items[:limit]]
