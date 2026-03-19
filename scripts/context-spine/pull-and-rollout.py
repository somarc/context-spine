#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def default_source_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_is_dirty(source_root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(source_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Failed to inspect git status for source repo.")
    return bool(result.stdout.strip())


def build_pull_command() -> list[str]:
    return ["git", "pull", "--ff-only"]


def build_upgrade_command(
    source_root: Path,
    target_root: Path,
    *,
    apply_safe: bool,
    gitignore_mode: str,
    out: str,
    json_out: str,
) -> list[str]:
    command = [
        "python3",
        str(source_root / "scripts" / "context-spine" / "upgrade.py"),
        "--target",
        str(target_root),
    ]
    if apply_safe:
        command.append("--apply-safe")
    if gitignore_mode and gitignore_mode != "none":
        command.extend(["--gitignore-mode", gitignore_mode])
    if out:
        command.extend(["--out", out])
    if json_out:
        command.extend(["--json-out", json_out])
    return command


def build_rollout_command(
    source_root: Path,
    repo_roots: list[Path],
    *,
    apply_safe: bool,
    out: str,
    json_out: str,
) -> list[str]:
    command = [
        "python3",
        str(source_root / "scripts" / "context-spine" / "rollout.py"),
        "--repos",
        *[str(path) for path in repo_roots],
    ]
    if apply_safe:
        command.append("--apply-safe")
    if out:
        command.extend(["--out", out])
    if json_out:
        command.extend(["--json-out", json_out])
    return command


def selected_targets(args: argparse.Namespace) -> list[Path]:
    if args.target:
        return [Path(args.target).expanduser().resolve()]
    return [Path(item).expanduser().resolve() for item in args.repos]


def mode_for(repo_roots: list[Path], gitignore_mode: str) -> str:
    if len(repo_roots) == 1:
        return "upgrade"
    if gitignore_mode and gitignore_mode != "none":
        raise ValueError("`--gitignore-mode` is only supported for single-target upgrades.")
    return "rollout"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update a Context Spine source checkout with git pull --ff-only, then run upgrade or rollout against target repos."
    )
    parser.add_argument("--source-root", default="", help="Context Spine source checkout; defaults to this repo")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--target", help="Single target repository to upgrade")
    target_group.add_argument("--repos", nargs="+", help="One or more target repositories to assess or upgrade")
    parser.add_argument("--apply-safe", action="store_true", help="Apply safe additive upgrade files when supported")
    parser.add_argument(
        "--gitignore-mode",
        default="none",
        choices=["tracked", "local", "none"],
        help="Managed Context Spine gitignore mode for single-target upgrades",
    )
    parser.add_argument("--out", default="", help="Optional report output path")
    parser.add_argument("--json-out", default="", help="Optional machine-readable report output path")
    parser.add_argument("--no-pull-source", action="store_true", help="Skip pulling the source checkout before upgrade or rollout")
    parser.add_argument(
        "--allow-dirty-source",
        action="store_true",
        help="Allow pull attempts from a source checkout with local changes",
    )
    args = parser.parse_args()

    source_root = Path(args.source_root).expanduser().resolve() if args.source_root else default_source_root()
    repo_roots = selected_targets(args)

    if not args.no_pull_source:
        if not args.allow_dirty_source and source_is_dirty(source_root):
            print(
                "Source repo has local changes. Commit or stash them first, or rerun with `--no-pull-source` or `--allow-dirty-source`.",
                file=sys.stderr,
            )
            return 2

        print(f"Updating source checkout at {source_root}")
        pull_result = subprocess.run(build_pull_command(), cwd=str(source_root), check=False)
        if pull_result.returncode != 0:
            return pull_result.returncode

    try:
        mode = mode_for(repo_roots, args.gitignore_mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if mode == "upgrade":
        command = build_upgrade_command(
            source_root,
            repo_roots[0],
            apply_safe=args.apply_safe,
            gitignore_mode=args.gitignore_mode,
            out=args.out,
            json_out=args.json_out,
        )
        print(f"Running single-target upgrade for {repo_roots[0]}")
    else:
        command = build_rollout_command(
            source_root,
            repo_roots,
            apply_safe=args.apply_safe,
            out=args.out,
            json_out=args.json_out,
        )
        print(f"Running rollout across {len(repo_roots)} repos")

    result = subprocess.run(command, cwd=str(source_root), check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
