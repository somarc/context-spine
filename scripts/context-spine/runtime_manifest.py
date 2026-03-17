#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


IGNORED_NAMES = {".DS_Store", "__pycache__", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_manifest_path(repo_root: Path | None = None) -> Path:
    root = repo_root or default_repo_root()
    return root / "scripts" / "context-spine" / "runtime-manifest.json"


def load_runtime_manifest(repo_root: Path | None = None) -> dict:
    manifest_path = default_manifest_path(repo_root)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Runtime manifest must be a JSON object: {manifest_path}")
    return data


def runtime_version(repo_root: Path | None = None) -> str:
    try:
        return str(load_runtime_manifest(repo_root).get("runtime_version", "unknown"))
    except Exception:
        return "unknown"


def runtime_files(repo_root: Path | None = None) -> list[str]:
    return list(load_runtime_manifest(repo_root).get("runtime_files", []))


def safe_additive_files(repo_root: Path | None = None) -> list[str]:
    return list(load_runtime_manifest(repo_root).get("safe_additive_files", []))


def merge_review_files(repo_root: Path | None = None) -> list[str]:
    return list(load_runtime_manifest(repo_root).get("merge_review_files", []))


def configurable_files(repo_root: Path | None = None) -> list[str]:
    return list(load_runtime_manifest(repo_root).get("configurable_files", []))


def codex_skills(repo_root: Path | None = None) -> list[str]:
    return list(load_runtime_manifest(repo_root).get("codex_skills", []))


def _should_ignore(path: Path) -> bool:
    return path.name in IGNORED_NAMES or path.suffix in IGNORED_SUFFIXES


def iter_directory_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_NAMES for part in path.parts):
            continue
        if _should_ignore(path):
            continue
        files.append(path)
    return files


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in iter_directory_files(root):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
