#!/usr/bin/env python3
import datetime as dt
import json
import re
import subprocess
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


SHORTSTAT_PATTERN = re.compile(r"(?P<count>\d+)\s+(?P<label>files? changed|insertions?\(\+\)|deletions?\(-\))")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def _git_available(repo_root: Path) -> bool:
    return _run(["git", "rev-parse", "--show-toplevel"], repo_root).returncode == 0


def _git_value(repo_root: Path, cmd: list[str], fallback: str = "") -> str:
    result = _run(cmd, repo_root)
    if result.returncode != 0:
        return fallback
    return result.stdout.strip() or fallback


def _parse_shortstat(text: str) -> dict:
    payload = {
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0,
        "raw": text.strip(),
    }
    for match in SHORTSTAT_PATTERN.finditer(text):
        count = int(match.group("count"))
        label = match.group("label")
        if "files changed" in label or "file changed" in label:
            payload["files_changed"] = count
        elif "insertions" in label or "insertion" in label:
            payload["insertions"] = count
        elif "deletions" in label or "deletion" in label:
            payload["deletions"] = count
    return payload


def _git_shortstat(repo_root: Path, *args: str) -> dict:
    result = _run(["git", *args], repo_root)
    if result.returncode != 0:
        return {"files_changed": 0, "insertions": 0, "deletions": 0, "raw": ""}
    return _parse_shortstat(result.stdout)


def _git_status_counts(lines: list[str]) -> dict:
    staged = 0
    unstaged = 0
    untracked = 0
    sample: list[str] = []
    for line in lines:
        if len(line) < 3:
            continue
        if line.startswith("??"):
            untracked += 1
        else:
            if line[0] != " ":
                staged += 1
            if line[1] != " ":
                unstaged += 1
        sample.append(line[3:])
    return {
        "staged_count": staged,
        "unstaged_count": unstaged,
        "untracked_count": untracked,
        "changed_paths_sample": sample[:8],
    }


def collect_git_snapshot(repo_root: Path) -> dict:
    if not _git_available(repo_root):
        return {"available": False}

    status_result = _run(["git", "status", "--porcelain"], repo_root)
    lines = [line for line in status_result.stdout.splitlines() if line.strip()] if status_result.returncode == 0 else []
    counts = _git_status_counts(lines)
    return {
        "available": True,
        "branch": _git_value(repo_root, ["git", "rev-parse", "--abbrev-ref", "HEAD"], "unknown"),
        "head": _git_value(repo_root, ["git", "rev-parse", "HEAD"], ""),
        "head_short": _git_value(repo_root, ["git", "rev-parse", "--short", "HEAD"], ""),
        "dirty": bool(lines),
        "changed_path_count": len(lines),
        **counts,
        "diff_unstaged": _git_shortstat(repo_root, "diff", "--shortstat"),
        "diff_staged": _git_shortstat(repo_root, "diff", "--cached", "--shortstat"),
        "diff_vs_head": _git_shortstat(repo_root, "diff", "--shortstat", "HEAD"),
    }


def classify_command(command: str, args: dict | list | None = None) -> dict:
    lowered = command.lower().strip()
    family = "general"
    if any(token in lowered for token in ("verify", ":test")):
        family = "verification"
    elif any(token in lowered for token in ("doctor", "score")):
        family = "verification"
    elif any(token in lowered for token in ("upgrade", "rollout")):
        family = "maintenance"
    elif any(token in lowered for token in ("state", "hot-memory")):
        family = "generated-aid"
    elif any(token in lowered for token in ("session", "log", "refresh", "embed", "update")):
        family = "capture"

    signals = ["git", "diffs", "tool-events"]
    if any(token in lowered for token in ("verify", ":test", "pytest", "unittest")):
        signals.append("tests")

    return {
        "family": family,
        "signals": signals,
        "command": command,
        "has_args": bool(args),
    }


def _diff_count(before: dict | None, after: dict | None, key: str) -> int | None:
    if not before or not after:
        return None
    if key not in before or key not in after:
        return None
    return int(after.get(key, 0)) - int(before.get(key, 0))


def diff_git_snapshots(before: dict | None, after: dict | None) -> dict:
    if not before or not after or not before.get("available") or not after.get("available"):
        return {}
    return {
        "changed_path_delta": _diff_count(before, after, "changed_path_count"),
        "staged_delta": _diff_count(before, after, "staged_count"),
        "unstaged_delta": _diff_count(before, after, "unstaged_count"),
        "untracked_delta": _diff_count(before, after, "untracked_count"),
        "head_changed": before.get("head") != after.get("head"),
        "dirty_changed": before.get("dirty") != after.get("dirty"),
    }


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
        "automatic_capture": {
            "classification": classify_command(command, args),
            "git_start": collect_git_snapshot(repo_root),
            "git_finish": None,
            "git_delta": {},
        },
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
    repo_root = Path(str(handle.payload.get("repo_root", ".")))
    automatic_capture = dict(handle.payload.get("automatic_capture", {}))
    git_start = automatic_capture.get("git_start")
    git_finish = collect_git_snapshot(repo_root)

    handle.payload["status"] = status
    handle.payload["summary"] = summary
    handle.payload["finished_at"] = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    handle.payload["artifacts"] = _sanitize(artifacts or [])
    automatic_capture["git_finish"] = git_finish
    automatic_capture["git_delta"] = diff_git_snapshots(git_start, git_finish)
    handle.payload["automatic_capture"] = automatic_capture
    if extra:
        merged = dict(handle.payload.get("extra", {}))
        merged.update(_sanitize(extra))
        handle.payload["extra"] = merged
    handle.path.write_text(json.dumps(handle.payload, indent=2) + "\n", encoding="utf-8")
    return handle
