#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


SAFE_ADDITIVE_FILES = [
    "docs/README.md",
    "docs/archive/README.md",
    "docs/drafts/README.md",
    "docs/runbooks/doctor.md",
]

MERGE_REVIEW_FILES = [
    ".gitignore",
    "package.json",
    "scripts/context-spine/bootstrap.sh",
    "docs/runbooks/session-start.md",
    "docs/runbooks/how-to-use-context-spine.md",
    "docs/runbooks/project-drop-in.md",
    "meta/context-spine/spine-notes-context-spine.md",
]


@dataclass
class UpgradeResult:
    repo_root: Path
    source_root: Path
    mode: str
    safe_missing: list[str] = field(default_factory=list)
    safe_applied: list[str] = field(default_factory=list)
    merge_missing: list[str] = field(default_factory=list)
    merge_different: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_mode(repo_root: Path) -> str:
    has_meta = (repo_root / "meta" / "context-spine").is_dir()
    has_scripts = (repo_root / "scripts" / "context-spine").is_dir()
    has_baseline = any((repo_root / "meta" / "context-spine").glob("spine-notes-*.md")) if has_meta else False
    if has_meta and has_scripts and has_baseline:
        return "existing"
    if has_meta or has_scripts:
        return "partial"
    return "missing"


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


def evaluate(target_root: Path, source_root: Path, apply_safe: bool) -> UpgradeResult:
    result = UpgradeResult(repo_root=target_root, source_root=source_root, mode=detect_mode(target_root))

    for relative_path in SAFE_ADDITIVE_FILES:
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

    for relative_path in MERGE_REVIEW_FILES:
        source = source_root / relative_path
        target = target_root / relative_path
        if not source.exists():
            result.notes.append(f"Boilerplate source missing: {relative_path}")
            continue
        if not target.exists():
            result.merge_missing.append(relative_path)
        elif not file_exists_and_same(target, source):
            result.merge_different.append(relative_path)

    if (target_root / "docs").is_dir() and not (target_root / "docs" / "README.md").exists():
        result.notes.append("Target repo has docs but no docs/README.md authority map.")
    if dirty := dirty_paths(target_root):
        result.notes.append(f"Target repo currently has {len(dirty)} dirty worktree paths.")
    return result


def render_report(result: UpgradeResult, generated_at: dt.datetime) -> str:
    lines = [
        "# Context Spine Upgrade Report",
        "",
        f"- Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Target repo: {result.repo_root}",
        f"- Boilerplate source: {result.source_root}",
        f"- Detected mode: {result.mode}",
        "",
        "## Summary",
        f"- Safe additive files missing: {len(result.safe_missing)}",
        f"- Safe additive files applied: {len(result.safe_applied)}",
        f"- Merge-review files missing: {len(result.merge_missing)}",
        f"- Merge-review files different: {len(result.merge_different)}",
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
        f"mode={result.mode}",
        f"safe_missing={len(result.safe_missing)} safe_applied={len(result.safe_applied)} merge_missing={len(result.merge_missing)} merge_different={len(result.merge_different)}",
        "",
    ]
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
    parser.add_argument("--out", default="", help="Output path for the markdown report")
    parser.add_argument("--json-out", default="", help="Output path for machine-readable JSON")
    args = parser.parse_args()

    source_root = Path(args.source_root).expanduser() if args.source_root else Path(__file__).resolve().parents[2]
    target_root = Path(args.target).expanduser()
    generated_at = dt.datetime.now()

    result = evaluate(target_root, source_root, args.apply_safe)

    out_path = Path(args.out).expanduser() if args.out else target_root / "meta" / "context-spine" / "upgrade-report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_report(result, generated_at), encoding="utf-8")

    if args.json_out:
        json_path = Path(args.json_out).expanduser()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {
                    "generated_at": generated_at.isoformat(),
                    "target_repo": str(result.repo_root),
                    "source_root": str(result.source_root),
                    "mode": result.mode,
                    "safe_missing": result.safe_missing,
                    "safe_applied": result.safe_applied,
                    "merge_missing": result.merge_missing,
                    "merge_different": result.merge_different,
                    "notes": result.notes,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(render_terminal(result, out_path), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
