#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from generated_artifact import (
    GeneratedArtifactSpec,
    markdown_heading_validator,
    publish_generated_artifacts,
    validate_json_artifact,
)
from project_space import detect_project_space
from run_state import finish_run, start_run
from runtime_manifest import runtime_version


@dataclass
class RepoStatus:
    repo: Path
    scope: str
    workspace_root: Path | None
    doctor_counts: dict[str, int]
    upgrade_mode: str
    project_mode: str
    scope_label: str
    nearest_workspace_root: str
    root_git: bool
    child_repo_count: int
    child_existing_count: int
    child_linked_count: int
    child_partial_count: int
    child_missing_count: int
    safe_missing: int
    safe_applied: int
    merge_missing: int
    merge_different: int


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def doctor_status(repo: Path, doctor_script: Path) -> dict:
    with tempfile.NamedTemporaryFile(prefix="context-spine-doctor-", suffix=".json", delete=False) as tmp:
        json_path = Path(tmp.name)
    try:
        result = subprocess.run(
            ["python3", str(doctor_script), "--repo-root", str(repo), "--json-out", str(json_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            return data.get("counts", {})
        if result.returncode != 0:
            return {"pass": 0, "warn": 0, "fail": 1}
        return {}
    finally:
        json_path.unlink(missing_ok=True)


def upgrade_status(repo: Path, upgrade_script: Path, apply_safe: bool) -> dict:
    with tempfile.NamedTemporaryFile(prefix="context-spine-upgrade-", suffix=".json", delete=False) as tmp:
        json_path = Path(tmp.name)
    cmd = ["python3", str(upgrade_script), "--target", str(repo), "--json-out", str(json_path)]
    if apply_safe:
        cmd.append("--apply-safe")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if json_path.exists():
            return json.loads(json_path.read_text(encoding="utf-8"))
        if result.returncode != 0:
            return {"mode": "error"}
        return {}
    finally:
        json_path.unlink(missing_ok=True)


def load_target_config(root: Path) -> dict:
    config_path = root / "meta" / "context-spine" / "context-spine.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def expand_targets(paths: list[Path]) -> list[tuple[Path, str, Path | None]]:
    expanded: list[tuple[Path, str, Path | None]] = []
    seen: set[str] = set()
    for target in paths:
        config = load_target_config(target)
        project_space = detect_project_space(target, config)
        root_key = str(target.resolve())
        if root_key not in seen:
            scope = "workspace-root" if project_space.mode == "workspace" else "repo-root"
            expanded.append((target.resolve(), scope, None))
            seen.add(root_key)
        if project_space.mode != "workspace":
            continue
        for child in project_space.child_repos:
            child_key = str(child.path.resolve())
            if child_key in seen:
                continue
            expanded.append((child.path.resolve(), "child-repo", target.resolve()))
            seen.add(child_key)
    return expanded


def severity(status: RepoStatus) -> tuple[int, int, int, int]:
    return (
        0 if status.doctor_counts.get("fail", 0) > 0 else 1,
        0 if status.upgrade_mode in {"missing", "error"} else 1 if status.upgrade_mode == "partial" else 2,
        -(status.merge_missing + status.merge_different),
        -(status.safe_missing),
    )


def recommendation(status: RepoStatus) -> str:
    if status.doctor_counts.get("fail", 0) > 0:
        return "Repair broken core surfaces before rollout."
    if status.upgrade_mode == "error":
        return "Upgrade evaluation failed; inspect the target directly before continuing rollout."
    if status.upgrade_mode == "linked-child":
        return "Linked child is intentionally light-touch; keep shared Context Spine truth in the parent workspace spine."
    if status.upgrade_mode == "missing":
        return "Install Context Spine first, then run doctor."
    if status.upgrade_mode == "partial":
        return "Apply safe additive surfaces and finish the partial install."
    if status.project_mode == "workspace" and (status.child_partial_count or status.child_missing_count):
        return "Parent workspace is healthy enough to read, but some child repos still need a vertebra or local spine. Prefer `context:upgrade -- --target <repo> --adopt-mode linked-child` when you want the light-touch path."
    if status.merge_missing or status.merge_different:
        return "Review merge-worthy files before calling the repo current."
    if status.safe_missing:
        return "Apply the remaining safe additive files."
    return "Repo looks current; keep it on the normal doctor/score loop."


def render_report(statuses: list[RepoStatus], *, run_id: str, runtime_version_text: str) -> str:
    lines = [
        "# Context Spine Rollout Report",
        "",
        f"- Run ID: {run_id}",
        f"- Runtime version: {runtime_version_text}",
        "## Summary",
        f"- Targets scanned: {len(statuses)}",
        "",
        "## Repo Status",
    ]
    for status in statuses:
        lines.extend(
            [
                "",
                f"### {status.repo}",
                f"- Scope: {status.scope}",
                f"- Project mode: {status.project_mode}",
                f"- Natural scope: {status.scope_label}",
                f"- Doctor: pass={status.doctor_counts.get('pass', 0)} warn={status.doctor_counts.get('warn', 0)} fail={status.doctor_counts.get('fail', 0)}",
                f"- Upgrade mode: {status.upgrade_mode}",
                f"- Root git: {'yes' if status.root_git else 'no'}",
                f"- Child repos: {status.child_repo_count}",
                f"- Child spines existing: {status.child_existing_count}",
                f"- Child spines linked: {status.child_linked_count}",
                f"- Child spines partial: {status.child_partial_count}",
                f"- Child spines missing: {status.child_missing_count}",
                f"- Safe additive gaps: {status.safe_missing}",
                f"- Safe additive applied: {status.safe_applied}",
                f"- Merge-review missing: {status.merge_missing}",
                f"- Merge-review diverged: {status.merge_different}",
                f"- Recommendation: {recommendation(status)}",
            ]
        )
        if status.workspace_root is not None:
            lines.append(f"- Workspace root: {status.workspace_root}")
        if status.nearest_workspace_root:
            lines.append(f"- Nearest parent workspace: {status.nearest_workspace_root}")
    return "\n".join(lines) + "\n"


def render_json(statuses: list[RepoStatus], *, run_id: str, runtime_version_text: str) -> str:
    payload = {
        "run_id": run_id,
        "runtime_version": runtime_version_text,
        "repos": [
            {
                "repo": str(status.repo),
                "scope": status.scope,
                "workspace_root": str(status.workspace_root) if status.workspace_root else None,
                "doctor_counts": status.doctor_counts,
                "upgrade_mode": status.upgrade_mode,
                "project_mode": status.project_mode,
                "scope_label": status.scope_label,
                "nearest_workspace_root": status.nearest_workspace_root or None,
                "root_git": status.root_git,
                "child_repo_count": status.child_repo_count,
                "child_existing_count": status.child_existing_count,
                "child_linked_count": status.child_linked_count,
                "child_partial_count": status.child_partial_count,
                "child_missing_count": status.child_missing_count,
                "safe_missing": status.safe_missing,
                "safe_applied": status.safe_applied,
                "merge_missing": status.merge_missing,
                "merge_different": status.merge_different,
                "recommendation": recommendation(status),
            }
            for status in statuses
        ]
    }
    return json.dumps(payload, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess Context Spine status across multiple local repos.")
    parser.add_argument("--repos", nargs="+", required=True, help="Repo paths to scan")
    parser.add_argument("--apply-safe", action="store_true", help="Apply safe additive upgrade files while scanning")
    parser.add_argument("--out", default="", help="Output markdown report path")
    parser.add_argument("--json-out", default="", help="Optional JSON report path")
    args = parser.parse_args()

    root = default_repo_root()
    doctor_script = root / "scripts" / "context-spine" / "doctor.py"
    upgrade_script = root / "scripts" / "context-spine" / "upgrade.py"
    memory_root = root / "meta" / "context-spine"
    runtime_version_text = runtime_version(root)
    run_handle = start_run(
        root,
        memory_root,
        "context:rollout",
        args=vars(args),
        extra={"runtime_version": runtime_version_text},
    )

    targets = expand_targets([Path(repo_arg).expanduser() for repo_arg in args.repos])
    statuses: list[RepoStatus] = []
    for repo, scope, workspace_root in targets:
        doctor_counts = doctor_status(repo, doctor_script)
        upgrade = upgrade_status(repo, upgrade_script, args.apply_safe)
        statuses.append(
            RepoStatus(
                repo=repo,
                scope=scope,
                workspace_root=workspace_root,
                doctor_counts=doctor_counts,
                upgrade_mode=upgrade.get("mode", "unknown"),
                project_mode=upgrade.get("project_mode", "repo"),
                scope_label=str(upgrade.get("scope_label", "")),
                nearest_workspace_root=str(upgrade.get("nearest_workspace_root", "")),
                root_git=bool(upgrade.get("root_git", False)),
                child_repo_count=int(upgrade.get("child_repo_count", 0)),
                child_existing_count=int(upgrade.get("child_existing_count", 0)),
                child_linked_count=int(upgrade.get("child_linked_count", 0)),
                child_partial_count=int(upgrade.get("child_partial_count", 0)),
                child_missing_count=int(upgrade.get("child_missing_count", 0)),
                safe_missing=len(upgrade.get("safe_missing", [])),
                safe_applied=len(upgrade.get("safe_applied", [])),
                merge_missing=len(upgrade.get("merge_missing", [])),
                merge_different=len(upgrade.get("merge_different", [])),
            )
        )

    statuses.sort(key=severity)

    out_path = Path(args.out).expanduser() if args.out else root / "meta" / "context-spine" / "rollout-report.md"
    artifact_specs = [
        GeneratedArtifactSpec(
            path=out_path,
            content=render_report(statuses, run_id=run_handle.run_id, runtime_version_text=runtime_version_text),
            validator=markdown_heading_validator("# Context Spine Rollout Report"),
        )
    ]
    if args.json_out:
        json_out_path = Path(args.json_out).expanduser()
        artifact_specs.append(
            GeneratedArtifactSpec(
                path=json_out_path,
                content=render_json(statuses, run_id=run_handle.run_id, runtime_version_text=runtime_version_text),
                validator=validate_json_artifact,
            )
        )

    try:
        published = publish_generated_artifacts(artifact_specs, run_id=run_handle.run_id)
    except Exception as exc:
        finish_run(
            run_handle,
            status="fail",
            summary=f"Failed to publish rollout artifact(s): {exc}",
            artifacts=[],
            extra={"publication_error": str(exc)},
        )
        print(f"Failed to publish rollout artifact(s): {exc}")
        return 1

    artifacts = [str(item.path) for item in published]

    finish_run(
        run_handle,
        status="success",
        summary=f"Rollout assessed {len(statuses)} target(s).",
        artifacts=artifacts,
        extra={
            "repo_count": len(statuses),
            "artifact_digests": {str(item.path): item.digest for item in published},
        },
    )
    print(f"Run ID: {run_handle.run_id}")
    print("===== CONTEXT SPINE ROLLOUT =====")
    for status in statuses:
        print(f"{status.repo}")
        print(
            f"  scope: {status.scope} project_mode={status.project_mode} "
            f"root_git={'yes' if status.root_git else 'no'} child_repos={status.child_repo_count}"
        )
        if status.child_repo_count:
            print(
                f"  child_spines: existing={status.child_existing_count} linked={status.child_linked_count} "
                f"partial={status.child_partial_count} missing={status.child_missing_count}"
            )
        if status.workspace_root is not None:
            print(f"  workspace_root: {status.workspace_root}")
        print(
            f"  doctor: pass={status.doctor_counts.get('pass', 0)} "
            f"warn={status.doctor_counts.get('warn', 0)} fail={status.doctor_counts.get('fail', 0)}"
        )
        print(
            f"  upgrade: mode={status.upgrade_mode} safe_missing={status.safe_missing} "
            f"safe_applied={status.safe_applied} merge_missing={status.merge_missing} "
            f"merge_different={status.merge_different}"
        )
        print(f"  next: {recommendation(status)}")
    print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
