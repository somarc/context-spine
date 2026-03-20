#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from generated_artifact import (
    GeneratedArtifactSpec,
    markdown_heading_validator,
    publish_generated_artifacts,
    validate_json_artifact,
)
from project_space import (
    DEFAULT_TRUTH_POLICY,
    VALID_TRUTH_POLICIES,
    VERTEBRA_FILENAME,
    VERTEBRA_VERSION,
    detect_project_space,
    install_state as shared_install_state,
    nearest_workspace_root,
    summarize_project_space,
)
from run_state import finish_run, start_run
from runtime_manifest import configurable_files, load_runtime_manifest, merge_review_files, runtime_files, safe_additive_files

PREFERRED_BASELINE_FILE = "meta/context-spine/spine-notes-context-spine.md"
GITIGNORE_BEGIN = "# >>> context-spine gitignore "
GITIGNORE_END = "# <<< context-spine gitignore <<<"


@dataclass
class UpgradeResult:
    repo_root: Path
    source_root: Path
    mode: str
    project_mode: str
    scope_label: str = ""
    runtime_version: str = ""
    root_git: bool = False
    child_repo_count: int = 0
    child_existing_count: int = 0
    child_linked_count: int = 0
    child_partial_count: int = 0
    child_missing_count: int = 0
    nearest_workspace_root: str = ""
    linked_workspace_root: str = ""
    truth_policy: str = ""
    safe_missing: list[str] = field(default_factory=list)
    safe_applied: list[str] = field(default_factory=list)
    merge_missing: list[str] = field(default_factory=list)
    merge_different: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    gitignore_mode: str = ""
    gitignore_applied: bool = False


def project_space_scope_line(result: UpgradeResult) -> str:
    return result.scope_label or "repo spine"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_install_state(repo_root: Path) -> str:
    return shared_install_state(repo_root)


def detect_mode(repo_root: Path) -> str:
    return detect_install_state(repo_root)


def slugify_project_id(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "project"


def workspace_root_reference(target_root: Path, workspace_root: Path) -> str:
    try:
        return os.path.relpath(workspace_root.resolve(), start=target_root.resolve())
    except ValueError:
        return str(workspace_root.resolve())


def linked_child_payload(
    target_root: Path,
    workspace_root: Path,
    *,
    project_id: str,
    project_name: str,
    truth_policy: str,
) -> dict[str, object]:
    resolved_target = target_root.resolve()
    resolved_workspace = workspace_root.resolve()
    resolved_project_name = project_name.strip() or resolved_target.name
    resolved_project_id = project_id.strip() or slugify_project_id(resolved_project_name)
    return {
        "version": VERTEBRA_VERSION,
        "mode": "linked-child",
        "workspace_root": workspace_root_reference(resolved_target, resolved_workspace),
        "project_id": resolved_project_id,
        "project_name": resolved_project_name,
        "truth_policy": truth_policy,
    }


def adopt_linked_child(
    target_root: Path,
    *,
    workspace_root: Path,
    project_id: str,
    project_name: str,
    truth_policy: str,
) -> tuple[bool, str]:
    if not target_root.exists() or not target_root.is_dir():
        return False, f"Target root does not exist: {target_root}"
    if not workspace_root.exists() or not workspace_root.is_dir():
        return False, f"Workspace root does not exist: {workspace_root}"

    current_state = detect_install_state(target_root)
    if current_state in {"existing", "partial"}:
        return (
            False,
            "Target already has repo-local Context Spine surfaces; keep embedded-repo mode or remove local surfaces before adopting linked-child.",
        )

    contract_path = target_root / VERTEBRA_FILENAME
    content = json.dumps(
        linked_child_payload(
            target_root,
            workspace_root,
            project_id=project_id,
            project_name=project_name,
            truth_policy=truth_policy,
        ),
        indent=2,
    ) + "\n"
    if contract_path.exists():
        existing = contract_path.read_text(encoding="utf-8")
        if existing == content:
            return False, f"Existing `{VERTEBRA_FILENAME}` already matches the requested linked-child contract."
        return False, f"Existing `{VERTEBRA_FILENAME}` differs; review it manually instead of overwriting it."

    contract_path.write_text(content, encoding="utf-8")
    return True, f"Wrote linked-child vertebra contract to `{contract_path}`."


def file_exists_and_same(target: Path, source: Path) -> bool:
    return target.exists() and source.exists() and sha256(target) == sha256(source)


def safe_copy(source_root: Path, target_root: Path, relative_path: str) -> bool:
    source = source_root / relative_path
    target = target_root / relative_path
    if not source.exists() or target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def git_available(repo_root: Path) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    ).returncode == 0


def dirty_paths(repo_root: Path) -> list[str]:
    if not git_available(repo_root):
        return []
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line[3:] for line in result.stdout.splitlines() if len(line) > 3]


def baseline_notes(repo_root: Path) -> list[Path]:
    memory_root = repo_root / "meta" / "context-spine"
    if not memory_root.is_dir():
        return []
    return sorted(memory_root.glob("spine-notes-*.md"))


def tracked_paths(repo_root: Path, pathspec: str) -> list[str]:
    if not git_available(repo_root):
        return []
    result = subprocess.run(
        ["git", "ls-files", pathspec],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def detect_gitignore_mode(repo_root: Path) -> str:
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        return ""
    for line in gitignore.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith(GITIGNORE_BEGIN) and line.endswith(">>>"):
            return line[len(GITIGNORE_BEGIN): -3].strip("() ").replace("mode: ", "", 1).strip()
    return ""


def apply_gitignore_mode(source_root: Path, target_root: Path, mode: str) -> tuple[bool, str]:
    script = source_root / "scripts" / "context-spine" / "configure-gitignore.py"
    if not script.exists():
        return False, f"Missing configure-gitignore.py in source repo: {script}"
    result = subprocess.run(
        ["python3", str(script), "--repo-root", str(target_root), "--mode", mode],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False, result.stderr.strip() or result.stdout.strip() or f"configure-gitignore failed for mode {mode}"
    return True, result.stdout.strip()


def evaluate(
    target_root: Path,
    source_root: Path,
    apply_safe: bool,
    gitignore_mode: str,
    *,
    adopt_mode: str = "",
    workspace_root_arg: str = "",
    project_id: str = "",
    project_name: str = "",
    truth_policy: str = DEFAULT_TRUTH_POLICY,
) -> UpgradeResult:
    manifest = load_runtime_manifest(source_root)
    adoption_note = ""
    if adopt_mode == "linked-child":
        workspace_root = Path(workspace_root_arg).expanduser() if workspace_root_arg else nearest_workspace_root(target_root)
        if workspace_root is None:
            adoption_note = (
                "Adopt mode `linked-child` could not find a parent workspace spine automatically. "
                "Pass `--workspace-root` explicitly or initialize a workspace spine in an ancestor folder."
            )
        else:
            adopted, adoption_note = adopt_linked_child(
                target_root,
                workspace_root=workspace_root,
                project_id=project_id,
                project_name=project_name,
                truth_policy=truth_policy,
            )
            if not workspace_root_arg:
                adoption_note = f"Auto-discovered parent workspace spine `{workspace_root}`. {adoption_note}"
            if adopted and not apply_safe:
                adoption_note = f"{adoption_note} No repo-local spine files were scaffolded."
    config_path = target_root / "meta" / "context-spine" / "context-spine.json"
    config: dict = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            config = {}
    project_space = detect_project_space(target_root, config)
    project_space_summary = summarize_project_space(project_space)
    result = UpgradeResult(
        repo_root=target_root,
        source_root=source_root,
        mode=detect_install_state(target_root),
        project_mode=str(project_space_summary["mode"]),
        scope_label=str(project_space_summary["scope_label"]),
        runtime_version=str(manifest.get("runtime_version", "unknown")),
        root_git=bool(project_space_summary["root_git"]),
        child_repo_count=int(project_space_summary["child_repo_count"]),
        child_existing_count=int(project_space_summary["child_existing_count"]),
        child_linked_count=int(project_space_summary["child_linked_count"]),
        child_partial_count=int(project_space_summary["child_partial_count"]),
        child_missing_count=int(project_space_summary["child_missing_count"]),
        nearest_workspace_root=str(project_space_summary["nearest_workspace_root"]),
        linked_workspace_root=(
            str(project_space.vertebra.workspace_root)
            if project_space.vertebra and project_space.vertebra.workspace_root is not None
            else ""
        ),
        truth_policy=project_space.vertebra.truth_policy if project_space.vertebra else "",
    )
    result.gitignore_mode = gitignore_mode
    if adoption_note:
        result.notes.append(adoption_note)

    if result.mode == "linked-child":
        if project_space.vertebra is None:
            result.notes.append("Linked-child mode was inferred, but no vertebra file could be read.")
        elif project_space.vertebra.error:
            result.notes.append(project_space.vertebra.error)
        else:
            result.notes.append(
                f"Linked child points to workspace root `{result.linked_workspace_root}` with truth_policy `{result.truth_policy}`."
            )
            linked_memory_root = project_space.vertebra.workspace_root / "meta" / "context-spine" if project_space.vertebra.workspace_root else None
            if linked_memory_root is not None and not linked_memory_root.is_dir():
                result.notes.append(
                    "The linked workspace root exists, but it does not have `meta/context-spine/` yet."
                )
        if dirty := dirty_paths(target_root):
            result.notes.append(f"Target repo currently has {len(dirty)} dirty worktree paths.")
        return result

    for relative_path in runtime_files(source_root):
        source = source_root / relative_path
        target = target_root / relative_path
        if not source.exists():
            result.notes.append(f"Boilerplate source missing: {relative_path}")
            continue
        if not target.exists():
            result.safe_missing.append(relative_path)
            if apply_safe and safe_copy(source_root, target_root, relative_path):
                result.safe_applied.append(relative_path)
            continue
        if not file_exists_and_same(target, source):
            result.merge_different.append(relative_path)

    for relative_path in safe_additive_files(source_root):
        source = source_root / relative_path
        target = target_root / relative_path
        if not source.exists():
            result.notes.append(f"Boilerplate source missing: {relative_path}")
            continue
        if target.exists():
            continue
        result.safe_missing.append(relative_path)
        if apply_safe and safe_copy(source_root, target_root, relative_path):
            result.safe_applied.append(relative_path)

    for relative_path in configurable_files(source_root):
        source = source_root / relative_path
        target = target_root / relative_path
        if not source.exists():
            result.notes.append(f"Boilerplate source missing: {relative_path}")
            continue
        if target.exists() and not file_exists_and_same(target, source):
            result.merge_different.append(relative_path)

    for relative_path in merge_review_files(source_root):
        source = source_root / relative_path
        target = target_root / relative_path
        if not source.exists():
            result.notes.append(f"Boilerplate source missing: {relative_path}")
            continue
        if not target.exists():
            result.merge_missing.append(relative_path)
        elif not file_exists_and_same(target, source):
            result.merge_different.append(relative_path)

    preferred_baseline = target_root / PREFERRED_BASELINE_FILE
    current_baselines = baseline_notes(target_root)
    if preferred_baseline.exists():
        source = source_root / PREFERRED_BASELINE_FILE
        if source.exists() and not file_exists_and_same(preferred_baseline, source):
            result.merge_different.append(PREFERRED_BASELINE_FILE)
    elif current_baselines:
        result.notes.append(
            "Custom baseline note detected; keep the existing `spine-notes-*.md` file instead of renaming it."
        )
    else:
        result.merge_missing.append(PREFERRED_BASELINE_FILE)

    if (target_root / "docs").is_dir() and not (target_root / "docs" / "README.md").exists():
        result.notes.append("Target repo has docs but no docs/README.md authority map.")

    if result.project_mode == "workspace":
        result.notes.append(
            "Workspace topology: "
            f"root_git={'yes' if result.root_git else 'no'} "
            f"child_repos={result.child_repo_count} "
            f"existing={result.child_existing_count} "
            f"linked={result.child_linked_count} "
            f"partial={result.child_partial_count} "
            f"missing={result.child_missing_count}"
        )
        if result.child_repo_count == 0:
            result.notes.append(
                "Workspace mode is configured or inferred, but no child git repos were detected. Review `project_space.child_repos` and scan settings."
            )

    current_gitignore_mode = detect_gitignore_mode(target_root)
    if gitignore_mode:
        applied, message = apply_gitignore_mode(source_root, target_root, gitignore_mode)
        result.gitignore_applied = applied
        result.notes.append(message)
        if gitignore_mode == "local" and tracked_paths(target_root, "meta/context-spine"):
            result.notes.append("Local mode does not untrack existing files; run `git rm -r --cached meta/context-spine` once if needed.")
    elif current_gitignore_mode:
        result.notes.append(f"Managed Context Spine gitignore mode is already set to `{current_gitignore_mode}`.")
    else:
        result.notes.append("Use `--gitignore-mode tracked|local` to manage the Context Spine block in `.gitignore`.")

    if dirty := dirty_paths(target_root):
        result.notes.append(f"Target repo currently has {len(dirty)} dirty worktree paths.")
    return result


def render_report(result: UpgradeResult, generated_at: dt.datetime, run_id: str) -> str:
    lines = [
        "# Context Spine Upgrade Report",
        "",
        f"- Run ID: {run_id}",
        f"- Runtime version: {result.runtime_version}",
        f"- Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Target repo: {result.repo_root}",
        f"- Boilerplate source: {result.source_root}",
        f"- Install state: {result.mode}",
        f"- Project mode: {result.project_mode}",
        f"- Scope: {project_space_scope_line(result)}",
        "",
        "## Summary",
        f"- Safe additive files missing: {len(result.safe_missing)}",
        f"- Safe additive files applied: {len(result.safe_applied)}",
        f"- Merge-review files missing: {len(result.merge_missing)}",
        f"- Merge-review files different: {len(result.merge_different)}",
        f"- Gitignore mode requested: {result.gitignore_mode or 'none'}",
        f"- Gitignore updated: {'yes' if result.gitignore_applied else 'no'}",
        "",
        "## Project Space",
        f"- Scope label: {result.scope_label}",
        f"- Root git: {'yes' if result.root_git else 'no'}",
        f"- Child repos: {result.child_repo_count}",
        f"- Child spines existing: {result.child_existing_count}",
        f"- Child spines linked: {result.child_linked_count}",
        f"- Child spines partial: {result.child_partial_count}",
        f"- Child spines missing: {result.child_missing_count}",
        f"- Nearest parent workspace: {result.nearest_workspace_root or 'n/a'}",
        f"- Linked workspace root: {result.linked_workspace_root or 'n/a'}",
        f"- Truth policy: {result.truth_policy or 'n/a'}",
        "",
        "## Safe Additive Files",
    ]

    if result.safe_missing:
        lines.extend(f"- {path}" for path in result.safe_missing)
    else:
        lines.append("- None missing.")

    if result.safe_applied:
        lines.extend(["", "### Applied"])
        lines.extend(f"- {path}" for path in result.safe_applied)

    lines.extend(["", "## Merge Review Files"])
    if result.merge_missing:
        lines.append("")
        lines.append("### Missing")
        lines.extend(f"- {path}" for path in result.merge_missing)
    if result.merge_different:
        lines.append("")
        lines.append("### Present But Diverged")
        lines.extend(f"- {path}" for path in result.merge_different)
    if not result.merge_missing and not result.merge_different:
        lines.append("- No merge-review gaps detected.")

    lines.extend(["", "## Notes"])
    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- No additional upgrade notes.")

    if result.mode == "linked-child":
        lines.extend(
            [
                "",
                "## Recommended Order",
                "1. Verify the parent workspace spine is the place you want shared truth to live.",
                "2. Run `context:doctor` in the child repo so the vertebra contract and parent workspace surface are both checked.",
                "3. Only promote the child to a full embedded repo spine if repo-local durable memory becomes worth the coupling.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Recommended Order",
                "1. Apply or accept the safe additive files.",
                "2. Review merge-worthy files one by one instead of overwriting project-owned customizations.",
                "3. Run `context:doctor` in the target repo after the upgrade so the new surfaces are immediately audited.",
            ]
        )
    return "\n".join(lines) + "\n"


def render_terminal(result: UpgradeResult, out_path: Path) -> str:
    lines = [
        "===== CONTEXT UPGRADE =====",
        f"runtime_version={result.runtime_version}",
        f"install_state={result.mode} project_mode={result.project_mode}",
        f"safe_missing={len(result.safe_missing)} safe_applied={len(result.safe_applied)} merge_missing={len(result.merge_missing)} merge_different={len(result.merge_different)}",
        f"root_git={'yes' if result.root_git else 'no'} child_repos={result.child_repo_count} child_existing={result.child_existing_count} child_linked={result.child_linked_count} child_partial={result.child_partial_count} child_missing={result.child_missing_count}",
        f"gitignore_mode={result.gitignore_mode or 'none'} gitignore_applied={'yes' if result.gitignore_applied else 'no'}",
        f"scope={project_space_scope_line(result)}",
        "",
    ]
    if result.linked_workspace_root or result.truth_policy:
        lines.extend(
            [
                "Linked child:",
                f"  - workspace_root: {result.linked_workspace_root or 'n/a'}",
                f"  - truth_policy: {result.truth_policy or 'n/a'}",
                "",
            ]
        )
    if result.nearest_workspace_root:
        lines.extend(
            [
                "Hierarchy:",
                f"  - nearest_parent_workspace: {result.nearest_workspace_root}",
                "",
            ]
        )
    if result.safe_missing:
        lines.append("Safe additive files:")
        lines.extend(f"  - {path}" for path in result.safe_missing)
        lines.append("")
    if result.merge_missing or result.merge_different:
        lines.append("Merge review:")
        for path in result.merge_missing:
            lines.append(f"  - missing: {path}")
        for path in result.merge_different:
            lines.append(f"  - diverged: {path}")
        lines.append("")
    if result.notes:
        lines.append("Notes:")
        lines.extend(f"  - {note}" for note in result.notes)
        lines.append("")
    lines.append(f"Report: {out_path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or apply a safe Context Spine upgrade for an existing project.")
    parser.add_argument("--target", required=True, help="Target repository to upgrade")
    parser.add_argument("--source-root", default="", help="Boilerplate source root; defaults to this repo")
    parser.add_argument("--apply-safe", action="store_true", help="Copy missing safe additive files into the target")
    parser.add_argument(
        "--adopt-mode",
        default="",
        choices=["", "linked-child"],
        help="Adopt the target as a specific light-touch project-space mode before evaluation",
    )
    parser.add_argument(
        "--workspace-root",
        default="",
        help="Parent workspace root used when `--adopt-mode linked-child` is requested; defaults to the nearest detected ancestor workspace spine",
    )
    parser.add_argument("--project-id", default="", help="Optional project identifier written into a linked-child vertebra")
    parser.add_argument("--project-name", default="", help="Optional project display name written into a linked-child vertebra")
    parser.add_argument(
        "--truth-policy",
        default=DEFAULT_TRUTH_POLICY,
        choices=sorted(VALID_TRUTH_POLICIES),
        help="Truth policy written into a linked-child vertebra",
    )
    parser.add_argument(
        "--gitignore-mode",
        default=os.environ.get("CONTEXT_SPINE_GITIGNORE_MODE", ""),
        choices=["", "tracked", "local", "none"],
        help="Manage the Context Spine block in the target repo's .gitignore",
    )
    parser.add_argument("--out", default="", help="Output path for the markdown report")
    parser.add_argument("--json-out", default="", help="Output path for machine-readable JSON")
    args = parser.parse_args()

    source_root = Path(args.source_root).expanduser() if args.source_root else Path(__file__).resolve().parents[2]
    target_root = Path(args.target).expanduser()
    generated_at = dt.datetime.now()
    memory_root = target_root / "meta" / "context-spine"
    run_handle = start_run(
        target_root,
        memory_root,
        "context:upgrade",
        args=vars(args),
    )

    result = evaluate(
        target_root,
        source_root,
        args.apply_safe,
        args.gitignore_mode,
        adopt_mode=args.adopt_mode,
        workspace_root_arg=args.workspace_root,
        project_id=args.project_id,
        project_name=args.project_name,
        truth_policy=args.truth_policy,
    )

    out_path = Path(args.out).expanduser() if args.out else target_root / "meta" / "context-spine" / "upgrade-report.md"
    artifact_specs = [
        GeneratedArtifactSpec(
            path=out_path,
            content=render_report(result, generated_at, run_handle.run_id),
            validator=markdown_heading_validator("# Context Spine Upgrade Report"),
        )
    ]
    if args.json_out:
        json_path = Path(args.json_out).expanduser()
        artifact_specs.append(
            GeneratedArtifactSpec(
                path=json_path,
                content=(
                    json.dumps(
                        {
                            "run_id": run_handle.run_id,
                            "runtime_version": result.runtime_version,
                            "generated_at": generated_at.isoformat(),
                            "target_repo": str(result.repo_root),
                            "source_root": str(result.source_root),
                            "mode": result.mode,
                            "project_mode": result.project_mode,
                            "scope_label": result.scope_label,
                            "root_git": result.root_git,
                            "child_repo_count": result.child_repo_count,
                            "child_existing_count": result.child_existing_count,
                            "child_linked_count": result.child_linked_count,
                            "child_partial_count": result.child_partial_count,
                            "child_missing_count": result.child_missing_count,
                            "nearest_workspace_root": result.nearest_workspace_root,
                            "linked_workspace_root": result.linked_workspace_root,
                            "truth_policy": result.truth_policy,
                            "adopt_mode": args.adopt_mode,
                            "safe_missing": result.safe_missing,
                            "safe_applied": result.safe_applied,
                            "merge_missing": result.merge_missing,
                            "merge_different": result.merge_different,
                            "gitignore_mode": result.gitignore_mode,
                            "gitignore_applied": result.gitignore_applied,
                            "notes": result.notes,
                        },
                        indent=2,
                    )
                    + "\n"
                ),
                validator=validate_json_artifact,
            )
        )
    try:
        published = publish_generated_artifacts(artifact_specs, run_id=run_handle.run_id)
    except Exception as exc:
        finish_run(
            run_handle,
            status="fail",
            summary=f"Failed to publish upgrade artifact(s): {exc}",
            artifacts=[],
            extra={"publication_error": str(exc)},
        )
        print(f"Failed to publish upgrade artifact(s): {exc}")
        return 1

    artifacts = [str(item.path) for item in published]

    finish_run(
        run_handle,
        status="success",
        summary=(
            f"Upgrade evaluated: safe_missing={len(result.safe_missing)} "
            f"merge_missing={len(result.merge_missing)} merge_different={len(result.merge_different)}"
        ),
        artifacts=artifacts,
        extra={
            "mode": result.mode,
            "project_mode": result.project_mode,
            "safe_missing": len(result.safe_missing),
            "safe_applied": len(result.safe_applied),
            "merge_missing": len(result.merge_missing),
            "merge_different": len(result.merge_different),
            "artifact_digests": {str(item.path): item.digest for item in published},
        },
    )
    print(f"Run ID: {run_handle.run_id}")
    print(render_terminal(result, out_path), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
