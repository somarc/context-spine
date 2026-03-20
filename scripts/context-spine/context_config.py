#!/usr/bin/env python3
import json
import shlex
from copy import deepcopy
from pathlib import Path

from project_space import detect_project_space, summarize_project_space


DEFAULT_CONFIG = {
    "project": "context-spine",
    "memory_root": "meta/context-spine",
    "baseline": {
        "preferred_file": "spine-notes-context-spine.md",
    },
    "collections": {
        "meta": "context-spine-meta",
        "docs": "project-docs",
        "skills": "project-skills",
        "vault": "project-vault",
        "vault_root": "",
    },
    "qmd": {
        "collections": "context-spine-meta,project-docs,project-skills",
        "append_to_session": True,
        "queries": {
            "bootstrap": "spine notes baseline bootstrap memory",
            "primary": "priority todo decision action",
            "extra": "evidence open questions source_of_truth hydration flow cognition metacognition",
            "skills": "hydration flow metacognition backflow source hydration flow state",
        },
        "retries": 4,
        "retry_sleep_sec": 1,
    },
    "gitignore_mode": "tracked",
    "project_space": {
        "mode": "repo",
        "child_repos": [],
        "scan_roots": ["."],
        "scan_depth": 2,
        "ignore_dirs": [],
    },
}


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config_path(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine" / "context-spine.json"


def deep_merge(base: dict, override: dict) -> dict:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(repo_root: Path | None = None) -> dict:
    root = repo_root or default_repo_root()
    config = deepcopy(DEFAULT_CONFIG)
    config_path = default_config_path(root)
    if config_path.exists():
        override = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(override, dict):
            raise ValueError(f"Context Spine config must be a JSON object: {config_path}")
        config = deep_merge(config, override)
    return config


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def shell_variables(repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or default_repo_root()
    config = load_config(root)
    memory_root = resolve_repo_path(root, str(config["memory_root"]))
    collections = config.get("collections", {})
    qmd = config.get("qmd", {})
    queries = qmd.get("queries", {})
    project_space = detect_project_space(root, config)
    project_space_summary = summarize_project_space(project_space)

    return {
        "CONFIG_CONTEXT_SPINE_PROJECT": str(config.get("project", "")),
        "CONFIG_CONTEXT_SPINE_ROOT": str(memory_root),
        "CONFIG_CONTEXT_SPINE_BASELINE_PREFERRED": str(config.get("baseline", {}).get("preferred_file", "")),
        "CONFIG_CONTEXT_SPINE_COLLECTION": str(collections.get("meta", "")),
        "CONFIG_CONTEXT_SPINE_DOCS_COLLECTION": str(collections.get("docs", "")),
        "CONFIG_CONTEXT_SPINE_SKILLS_COLLECTION": str(collections.get("skills", "")),
        "CONFIG_CONTEXT_SPINE_VAULT_COLLECTION": str(collections.get("vault", "")),
        "CONFIG_CONTEXT_SPINE_VAULT_ROOT": str(collections.get("vault_root", "")),
        "CONFIG_CONTEXT_SPINE_QMD_COLLECTIONS": str(qmd.get("collections", "")),
        "CONFIG_CONTEXT_SPINE_QMD_APPEND": "1" if qmd.get("append_to_session", True) else "0",
        "CONFIG_CONTEXT_SPINE_QMD_QUERY_BOOTSTRAP": str(queries.get("bootstrap", "")),
        "CONFIG_CONTEXT_SPINE_QMD_QUERY": str(queries.get("primary", "")),
        "CONFIG_CONTEXT_SPINE_QMD_QUERY_EXTRA": str(queries.get("extra", "")),
        "CONFIG_CONTEXT_SPINE_QMD_QUERY_SKILLS": str(queries.get("skills", "")),
        "CONFIG_CONTEXT_SPINE_QMD_RETRIES": str(qmd.get("retries", 4)),
        "CONFIG_CONTEXT_SPINE_QMD_RETRY_SLEEP_SEC": str(qmd.get("retry_sleep_sec", 1)),
        "CONFIG_CONTEXT_SPINE_GITIGNORE_MODE": str(config.get("gitignore_mode", "")),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_MODE": str(project_space_summary.get("mode", "repo")),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_ROOT_GIT": "1" if project_space_summary.get("root_git") else "0",
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_REPO_COUNT": str(project_space_summary.get("child_repo_count", 0)),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_EXISTING_COUNT": str(project_space_summary.get("child_existing_count", 0)),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_LINKED_COUNT": str(project_space_summary.get("child_linked_count", 0)),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_PARTIAL_COUNT": str(project_space_summary.get("child_partial_count", 0)),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_MISSING_COUNT": str(project_space_summary.get("child_missing_count", 0)),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_SCOPE_LABEL": str(project_space_summary.get("scope_label", "")),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_ANCESTOR_WORKSPACE_COUNT": str(project_space_summary.get("ancestor_workspace_count", 0)),
        "CONFIG_CONTEXT_SPINE_PROJECT_SPACE_NEAREST_WORKSPACE_ROOT": str(project_space_summary.get("nearest_workspace_root", "")),
    }


def render_shell_variables(repo_root: Path | None = None) -> str:
    values = shell_variables(repo_root)
    return "\n".join(f"{name}={shlex.quote(value)}" for name, value in values.items()) + "\n"
