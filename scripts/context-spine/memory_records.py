#!/usr/bin/env python3
import datetime as dt
import json
import re
import uuid
from pathlib import Path
from typing import Any


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
    return normalized or "record"


def records_root(memory_root: Path) -> Path:
    return memory_root / "records"


def write_record(
    memory_root: Path,
    category: str,
    payload: dict[str, Any],
    *,
    record_id: str = "",
    recorded_at: dt.datetime | None = None,
) -> Path:
    stamp = (recorded_at or dt.datetime.now(dt.UTC)).astimezone(dt.UTC).replace(microsecond=0)
    record_id = record_id or f"{category}-{stamp.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    record_dir = records_root(memory_root) / category / stamp.strftime("%Y-%m-%d")
    record_dir.mkdir(parents=True, exist_ok=True)
    record_path = record_dir / f"{_slug(record_id)}.json"
    body = {
        "record_schema": "context-spine.memory-record.v1",
        "category": category,
        "record_id": record_id,
        "recorded_at": stamp.isoformat(),
        **_sanitize(payload),
    }
    record_path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return record_path


def iter_record_paths(memory_root: Path, category: str) -> list[Path]:
    root = records_root(memory_root) / category
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def load_record(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_record(memory_root: Path, category: str) -> tuple[Path, dict[str, Any]] | None:
    paths = iter_record_paths(memory_root, category)
    if not paths:
        return None
    latest_path = max(paths, key=lambda path: path.stat().st_mtime)
    return latest_path, load_record(latest_path)
