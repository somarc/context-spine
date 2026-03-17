#!/usr/bin/env python3
import datetime as dt
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from runtime_manifest import runtime_version


def _sanitize(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    return value


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "run"


@dataclass
class RunHandle:
    run_id: str
    path: Path
    payload: dict


def start_run(
    repo_root: Path,
    memory_root: Path,
    command: str,
    *,
    args: dict | list | None = None,
    extra: dict | None = None,
) -> RunHandle:
    started_at = dt.datetime.now(dt.UTC).replace(microsecond=0)
    run_id = f"ctx-{_slug(command)}-{started_at.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    run_dir = memory_root / "runs" / started_at.strftime("%Y-%m-%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / f"{run_id}.json"
    payload = {
        "run_id": run_id,
        "command": command,
        "repo_root": str(repo_root),
        "memory_root": str(memory_root),
        "runtime_version": runtime_version(repo_root),
        "status": "running",
        "started_at": started_at.isoformat(),
        "finished_at": None,
        "summary": "",
        "artifacts": [],
        "args": _sanitize(args or {}),
        "extra": _sanitize(extra or {}),
    }
    run_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return RunHandle(run_id=run_id, path=run_path, payload=payload)


def finish_run(
    handle: RunHandle,
    *,
    status: str,
    summary: str,
    artifacts: list[str] | None = None,
    extra: dict | None = None,
) -> RunHandle:
    handle.payload["status"] = status
    handle.payload["summary"] = summary
    handle.payload["finished_at"] = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    handle.payload["artifacts"] = _sanitize(artifacts or [])
    if extra:
        merged = dict(handle.payload.get("extra", {}))
        merged.update(_sanitize(extra))
        handle.payload["extra"] = merged
    handle.path.write_text(json.dumps(handle.payload, indent=2) + "\n", encoding="utf-8")
    return handle
