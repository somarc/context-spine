#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepoStatus:
    repo: Path
    doctor_counts: dict[str, int]
    upgrade_mode: str
    safe_missing: int
    safe_applied: int
    merge_missing: int
    merge_different: int


def doctor_status(repo: Path, doctor_script: Path) -> dict:
    with tempfile.NamedTemporaryFile(prefix="context-spine-doctor-", suffix=".json", delete=False) as tmp:
        json_path = Path(tmp.name)
    try:
        subprocess.run(
            ["python3", str(doctor_script), "--repo-root", str(repo), "--json-out", str(json_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return data.get("counts", {})
    finally:
        json_path.unlink(missing_ok=True)


def upgrade_status(repo: Path, upgrade_script: Path, apply_safe: bool) -> dict:
    with tempfile.NamedTemporaryFile(prefix="context-spine-upgrade-", suffix=".json", delete=False) as tmp:
        json_path = Path(tmp.name)
    cmd = ["python3", str(upgrade_script), "--target", str(repo), "--json-out", str(json_path)]
    if apply_safe:
        cmd.append("--apply-safe")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(json_path.read_text(encoding="utf-8"))
    finally:
        json_path.unlink(missing_ok=True)


def severity(status: RepoStatus) -> tuple[int, int, int, int]:
    return (
        0 if status.doctor_counts.get("fail", 0) > 0 else 1,
        0 if status.upgrade_mode == "missing" else 1 if status.upgrade_mode == "partial" else 2,
        -(status.merge_missing + status.merge_different),
        -(status.safe_missing),
    )


def recommendation(status: RepoStatus) -> str:
    if status.doctor_counts.get("fail", 0) > 0:
        return "Repair broken core surfaces before rollout."
    if status.upgrade_mode == "missing":
        return "Install Context Spine first, then run doctor."
    if status.upgrade_mode == "partial":
        return "Apply safe additive surfaces and finish the partial install."
    if status.merge_missing or status.merge_different:
        return "Review merge-worthy files before calling the repo current."
    if status.safe_missing:
        return "Apply the remaining safe additive files."
    return "Repo looks current; keep it on the normal doctor/score loop."


def render_report(statuses: list[RepoStatus], out_path: Path) -> None:
    lines = [
        "# Context Spine Rollout Report",
        "",
        "## Summary",
        f"- Repos scanned: {len(statuses)}",
        "",
        "## Repo Status",
    ]
    for status in statuses:
        lines.extend(
            [
                "",
                f"### {status.repo}",
                f"- Doctor: pass={status.doctor_counts.get('pass', 0)} warn={status.doctor_counts.get('warn', 0)} fail={status.doctor_counts.get('fail', 0)}",
                f"- Upgrade mode: {status.upgrade_mode}",
                f"- Safe additive gaps: {status.safe_missing}",
                f"- Safe additive applied: {status.safe_applied}",
                f"- Merge-review missing: {status.merge_missing}",
                f"- Merge-review diverged: {status.merge_different}",
                f"- Recommendation: {recommendation(status)}",
            ]
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_json(statuses: list[RepoStatus], out_path: Path) -> None:
    payload = {
        "repos": [
            {
                "repo": str(status.repo),
                "doctor_counts": status.doctor_counts,
                "upgrade_mode": status.upgrade_mode,
                "safe_missing": status.safe_missing,
                "safe_applied": status.safe_applied,
                "merge_missing": status.merge_missing,
                "merge_different": status.merge_different,
                "recommendation": recommendation(status),
            }
            for status in statuses
        ]
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess Context Spine status across multiple local repos.")
    parser.add_argument("--repos", nargs="+", required=True, help="Repo paths to scan")
    parser.add_argument("--apply-safe", action="store_true", help="Apply safe additive upgrade files while scanning")
    parser.add_argument("--out", default="", help="Output markdown report path")
    parser.add_argument("--json-out", default="", help="Optional JSON report path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    doctor_script = root / "scripts" / "context-spine" / "doctor.py"
    upgrade_script = root / "scripts" / "context-spine" / "upgrade.py"

    statuses: list[RepoStatus] = []
    for repo_arg in args.repos:
        repo = Path(repo_arg).expanduser()
        doctor_counts = doctor_status(repo, doctor_script)
        upgrade = upgrade_status(repo, upgrade_script, args.apply_safe)
        statuses.append(
            RepoStatus(
                repo=repo,
                doctor_counts=doctor_counts,
                upgrade_mode=upgrade.get("mode", "unknown"),
                safe_missing=len(upgrade.get("safe_missing", [])),
                safe_applied=len(upgrade.get("safe_applied", [])),
                merge_missing=len(upgrade.get("merge_missing", [])),
                merge_different=len(upgrade.get("merge_different", [])),
            )
        )

    statuses.sort(key=severity)

    out_path = Path(args.out).expanduser() if args.out else root / "meta" / "context-spine" / "rollout-report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    render_report(statuses, out_path)
    if args.json_out:
        json_out_path = Path(args.json_out).expanduser()
        json_out_path.parent.mkdir(parents=True, exist_ok=True)
        render_json(statuses, json_out_path)

    print("===== CONTEXT SPINE ROLLOUT =====")
    for status in statuses:
        print(f"{status.repo}")
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
