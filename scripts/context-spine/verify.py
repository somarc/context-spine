#!/usr/bin/env python3
import argparse
import datetime as dt
import subprocess
from pathlib import Path

from context_config import load_config, resolve_repo_path
from run_state import finish_run, start_run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def tail_lines(text: str, limit: int = 12) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    return lines[-limit:]


def summarize_output(stdout: str, stderr: str, returncode: int) -> str:
    for text in (stdout, stderr):
        lines = tail_lines(text, limit=1)
        if lines:
            return lines[-1]
    return f"Command exited with code {returncode}."


def verify_steps(repo_root: Path) -> list[dict]:
    return [
        {
            "name": "tests",
            "command": ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
            "cwd": repo_root,
        },
        {
            "name": "doctor",
            "command": ["python3", "./scripts/context-spine/doctor.py"],
            "cwd": repo_root,
        },
        {
            "name": "score",
            "command": ["python3", "./scripts/context-spine/mem-score.py"],
            "cwd": repo_root,
        },
        {
            "name": "skill_validate",
            "command": ["bash", "./scripts/context-spine/install-codex-skill.sh", "--validate-only"],
            "cwd": repo_root,
        },
    ]


def run_step(step: dict) -> dict:
    started = dt.datetime.now(dt.UTC)
    result = subprocess.run(
        step["command"],
        cwd=str(step["cwd"]),
        capture_output=True,
        text=True,
        check=False,
    )
    finished = dt.datetime.now(dt.UTC)
    status = "success" if result.returncode == 0 else "fail"
    return {
        "name": step["name"],
        "command": step["command"],
        "cwd": str(step["cwd"]),
        "status": status,
        "returncode": result.returncode,
        "started_at": started.replace(microsecond=0).isoformat(),
        "finished_at": finished.replace(microsecond=0).isoformat(),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "summary": summarize_output(result.stdout, result.stderr, result.returncode),
        "stdout_tail": tail_lines(result.stdout),
        "stderr_tail": tail_lines(result.stderr),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the standard Context Spine verification flow with structured capture.")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    repo_root = default_repo_root()
    config = load_config(repo_root)
    memory_root = (
        Path(args.root).expanduser()
        if args.root
        else resolve_repo_path(repo_root, str(config.get("memory_root", default_memory_root(repo_root))))
    ).resolve()

    run_handle = start_run(
        repo_root,
        memory_root,
        "context:verify",
        args=vars(args),
    )

    steps = [run_step(step) for step in verify_steps(repo_root)]
    failed = [step["name"] for step in steps if step["status"] != "success"]
    status = "success" if not failed else "fail"
    summary = (
        "Verification passed across tests, doctor, score, and skill validation."
        if not failed
        else f"Verification failed in {len(failed)} step(s): {', '.join(failed)}."
    )

    finish_run(
        run_handle,
        status=status,
        summary=summary,
        artifacts=[],
        extra={
            "steps": steps,
            "failed_steps": failed,
        },
    )

    print(f"Run ID: {run_handle.run_id}")
    print("===== CONTEXT VERIFY =====")
    for step in steps:
        print(f"[{step['status'].upper()}] {step['name']}: {step['summary']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
