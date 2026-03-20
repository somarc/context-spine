#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


VERTEBRA_FILENAME = ".context-spine.json"
VERTEBRA_VERSION = 1
VALID_PROJECT_MODES = {"repo", "workspace", "linked-child"}
VALID_TRUTH_POLICIES = {"external", "hybrid", "embedded"}
DEFAULT_TRUTH_POLICY = "external"
DEFAULT_IGNORE_DIRS = {
    ".agent",
    ".git",
    ".qmd",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "docs",
    "meta",
    "node_modules",
    "venv",
}


@dataclass(frozen=True)
class VertebraLink:
    path: Path
    mode: str
    workspace_root: Path | None
    truth_policy: str
    project_id: str
    project_name: str
    error: str = ""


@dataclass(frozen=True)
class ChildRepo:
    path: Path
    relative_path: str
    install_state: str
    has_memory_root: bool
    has_scripts: bool
    has_baseline: bool
    baseline_note: Path | None
    latest_session: Path | None
    hot_memory: Path | None
    vertebra: VertebraLink | None = None


@dataclass(frozen=True)
class ProjectSpace:
    root: Path
    mode: str
    root_git: bool
    child_repos: list[ChildRepo]
    vertebra: VertebraLink | None = None


def local_config_path(path: Path) -> Path:
    return path / "meta" / "context-spine" / "context-spine.json"


def vertebra_path(path: Path) -> Path:
    return path / VERTEBRA_FILENAME


def has_git_marker(path: Path) -> bool:
    return (path / ".git").exists()


def git_available(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(path),
        capture_output=True,
        text=True,
        check=False,
    ).returncode == 0


def read_vertebra_link(path: Path) -> VertebraLink | None:
    link_path = vertebra_path(path)
    if not link_path.exists():
        return None

    try:
        payload = json.loads(link_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return VertebraLink(
            path=link_path,
            mode="linked-child",
            workspace_root=None,
            truth_policy=DEFAULT_TRUTH_POLICY,
            project_id="",
            project_name=path.name,
            error=f"Invalid JSON: {exc}",
        )

    if not isinstance(payload, dict):
        return VertebraLink(
            path=link_path,
            mode="linked-child",
            workspace_root=None,
            truth_policy=DEFAULT_TRUTH_POLICY,
            project_id="",
            project_name=path.name,
            error="The vertebra file must be a JSON object.",
        )

    mode = str(payload.get("mode", "linked-child")).strip().lower() or "linked-child"
    if mode not in VALID_PROJECT_MODES:
        return VertebraLink(
            path=link_path,
            mode="linked-child",
            workspace_root=None,
            truth_policy=DEFAULT_TRUTH_POLICY,
            project_id=str(payload.get("project_id", "")),
            project_name=str(payload.get("project_name", path.name)),
            error=f"Unsupported mode `{mode}` in {VERTEBRA_FILENAME}.",
        )

    raw_workspace_root = str(payload.get("workspace_root", "")).strip()
    workspace_root = None
    error = ""
    if raw_workspace_root:
        candidate = Path(raw_workspace_root).expanduser()
        workspace_root = candidate if candidate.is_absolute() else (path / candidate).resolve()
    elif mode == "linked-child":
        error = "`workspace_root` is required for linked-child mode."

    truth_policy = str(payload.get("truth_policy", DEFAULT_TRUTH_POLICY)).strip().lower() or DEFAULT_TRUTH_POLICY
    if truth_policy not in VALID_TRUTH_POLICIES:
        error = error or f"Unsupported truth_policy `{truth_policy}` in {VERTEBRA_FILENAME}."
        truth_policy = DEFAULT_TRUTH_POLICY

    return VertebraLink(
        path=link_path,
        mode=mode,
        workspace_root=workspace_root,
        truth_policy=truth_policy,
        project_id=str(payload.get("project_id", "")).strip(),
        project_name=str(payload.get("project_name", path.name)).strip() or path.name,
        error=error,
    )


def install_state(path: Path) -> str:
    memory_root = path / "meta" / "context-spine"
    has_meta_contract = (memory_root / "context-spine.json").exists()
    has_scripts = (path / "scripts" / "context-spine").is_dir()
    has_baseline = any(memory_root.glob("spine-notes-*.md")) if memory_root.is_dir() else False
    has_sessions = (memory_root / "sessions").is_dir()
    has_meaningful_meta = has_meta_contract or has_baseline or has_sessions
    if has_meaningful_meta and has_scripts and has_baseline:
        return "existing"
    if read_vertebra_link(path) is not None:
        return "linked-child"
    if has_meaningful_meta or has_scripts:
        return "partial"
    return "missing"


def latest_baseline(path: Path) -> Path | None:
    memory_root = path / "meta" / "context-spine"
    if not memory_root.is_dir():
        return None
    candidates = sorted(memory_root.glob("spine-notes-*.md"))
    return candidates[-1] if candidates else None


def latest_session(path: Path) -> Path | None:
    sessions_dir = path / "meta" / "context-spine" / "sessions"
    if not sessions_dir.is_dir():
        return None
    candidates = sorted(sessions_dir.glob("*-session.md"))
    return candidates[-1] if candidates else None


def hot_memory_index(path: Path) -> Path | None:
    candidate = path / "meta" / "context-spine" / "hot-memory-index.md"
    return candidate if candidate.exists() else None


def load_local_config(path: Path) -> dict:
    config_path = local_config_path(path)
    if not config_path.exists():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def relative_to_root(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _child_repo(path: Path, root: Path) -> ChildRepo:
    baseline = latest_baseline(path)
    return ChildRepo(
        path=path.resolve(),
        relative_path=relative_to_root(root, path),
        install_state=install_state(path),
        has_memory_root=(path / "meta" / "context-spine").is_dir(),
        has_scripts=(path / "scripts" / "context-spine").is_dir(),
        has_baseline=baseline is not None,
        baseline_note=baseline,
        latest_session=latest_session(path),
        hot_memory=hot_memory_index(path),
        vertebra=read_vertebra_link(path),
    )


def _configured_child_paths(root: Path, project_space: dict) -> list[Path]:
    items = project_space.get("child_repos", [])
    paths: list[Path] = []
    if not isinstance(items, list):
        return paths
    for item in items:
        if not isinstance(item, str) or not item.strip():
            continue
        candidate = Path(item).expanduser()
        resolved = candidate if candidate.is_absolute() else (root / candidate).resolve()
        if resolved.exists() and resolved.is_dir():
            paths.append(resolved)
    return paths


def _scan_roots(root: Path, project_space: dict) -> list[Path]:
    configured = project_space.get("scan_roots", ["."])
    if not isinstance(configured, list) or not configured:
        configured = ["."]
    paths: list[Path] = []
    for item in configured:
        if not isinstance(item, str) or not item.strip():
            continue
        candidate = Path(item).expanduser()
        resolved = candidate if candidate.is_absolute() else (root / candidate).resolve()
        if resolved.exists() and resolved.is_dir():
            paths.append(resolved)
    return paths or [root]


def _is_child_repo_candidate(path: Path) -> bool:
    return has_git_marker(path) or read_vertebra_link(path) is not None


def _walk_for_child_repos(
    root: Path,
    scan_root: Path,
    *,
    current_depth: int,
    max_depth: int,
    ignore_dirs: set[str],
    discovered: dict[str, Path],
) -> None:
    try:
        entries = sorted(scan_root.iterdir(), key=lambda item: item.name)
    except OSError:
        return

    for entry in entries:
        if not entry.is_dir():
            continue
        if entry.name in ignore_dirs or entry.name.startswith("."):
            continue
        if entry.resolve() == root.resolve():
            continue
        if _is_child_repo_candidate(entry):
            discovered[str(entry.resolve())] = entry.resolve()
            continue
        if current_depth >= max_depth:
            continue
        _walk_for_child_repos(
            root,
            entry,
            current_depth=current_depth + 1,
            max_depth=max_depth,
            ignore_dirs=ignore_dirs,
            discovered=discovered,
        )


def discover_child_repo_roots(root: Path, config: dict) -> list[Path]:
    project_space = config.get("project_space", {}) if isinstance(config, dict) else {}
    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    configured_ignores = project_space.get("ignore_dirs", [])
    if isinstance(configured_ignores, list):
        ignore_dirs.update(str(item) for item in configured_ignores if str(item).strip())
    try:
        max_depth = int(project_space.get("scan_depth", 2))
    except (TypeError, ValueError):
        max_depth = 2
    if max_depth < 1:
        max_depth = 1

    discovered: dict[str, Path] = {}
    for path in _configured_child_paths(root, project_space):
        if path.resolve() != root.resolve() and _is_child_repo_candidate(path):
            discovered[str(path.resolve())] = path.resolve()

    for scan_root in _scan_roots(root, project_space):
        _walk_for_child_repos(
            root,
            scan_root,
            current_depth=1,
            max_depth=max_depth,
            ignore_dirs=ignore_dirs,
            discovered=discovered,
        )

    return [discovered[key] for key in sorted(discovered)]


def ancestor_workspace_roots(root: Path) -> list[Path]:
    resolved_root = root.resolve()
    ancestors: list[Path] = []
    for candidate in resolved_root.parents:
        if candidate == resolved_root:
            continue
        config_path = local_config_path(candidate)
        memory_root = candidate / "meta" / "context-spine"
        if not config_path.exists() and not memory_root.is_dir():
            continue
        project_space = detect_project_space(candidate, load_local_config(candidate))
        if project_space.mode == "workspace":
            ancestors.append(candidate.resolve())
    return ancestors


def nearest_workspace_root(root: Path) -> Path | None:
    ancestors = ancestor_workspace_roots(root)
    return ancestors[0] if ancestors else None


def scope_label(project_space: ProjectSpace) -> str:
    ancestors = ancestor_workspace_roots(project_space.root)
    if project_space.mode == "linked-child":
        return "repo vertebra"
    if project_space.mode == "workspace":
        return "meta spine" if not ancestors else "project spine"
    return "repo spine"


def detect_project_space(root: Path, config: dict) -> ProjectSpace:
    root = root.resolve()
    vertebra = read_vertebra_link(root)
    child_roots = discover_child_repo_roots(root, config)
    explicit_mode = ""
    has_local_config = (root / "meta" / "context-spine" / "context-spine.json").exists()
    if isinstance(config, dict):
        explicit_mode = str(config.get("project_space", {}).get("mode", "")).strip().lower()
        if not has_local_config and explicit_mode == "repo":
            explicit_mode = ""
    if not explicit_mode and vertebra is not None:
        explicit_mode = vertebra.mode

    root_git = has_git_marker(root) or git_available(root)
    if explicit_mode in VALID_PROJECT_MODES:
        mode = explicit_mode
    elif vertebra is not None:
        mode = "linked-child"
    elif child_roots and not root_git:
        mode = "workspace"
    else:
        mode = "repo"

    if mode == "linked-child":
        child_roots = []

    children = [_child_repo(path, root) for path in child_roots]
    return ProjectSpace(
        root=root,
        mode=mode,
        root_git=root_git,
        child_repos=children,
        vertebra=vertebra,
    )


def summarize_project_space(project_space: ProjectSpace) -> dict[str, int | str | bool]:
    existing = sum(1 for child in project_space.child_repos if child.install_state == "existing")
    linked = sum(1 for child in project_space.child_repos if child.install_state == "linked-child")
    partial = sum(1 for child in project_space.child_repos if child.install_state == "partial")
    missing = sum(1 for child in project_space.child_repos if child.install_state == "missing")
    workspace_ancestors = ancestor_workspace_roots(project_space.root)
    linked_workspace_root = project_space.vertebra.workspace_root if project_space.vertebra else None
    linked_workspace_ready = bool(
        linked_workspace_root
        and linked_workspace_root.exists()
        and (linked_workspace_root / "meta" / "context-spine").is_dir()
    )
    return {
        "mode": project_space.mode,
        "root_git": project_space.root_git,
        "child_repo_count": len(project_space.child_repos),
        "child_existing_count": existing,
        "child_linked_count": linked,
        "child_partial_count": partial,
        "child_missing_count": missing,
        "linked_workspace_ready": linked_workspace_ready,
        "scope_label": scope_label(project_space),
        "ancestor_workspace_count": len(workspace_ancestors),
        "nearest_workspace_root": str(workspace_ancestors[0]) if workspace_ancestors else "",
    }
