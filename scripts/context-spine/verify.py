#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import signal
import shutil
import subprocess
from pathlib import Path

from context_config import load_config, resolve_repo_path
from memory_events import write_event
from run_state import finish_run, start_run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    return repo_root / "meta" / "context-spine"


def has_test_suite(repo_root: Path) -> bool:
    tests_dir = repo_root / "tests"
    return tests_dir.is_dir() and any(tests_dir.glob("test_*.py"))


def configured_skills_root(repo_root: Path, config: dict | None = None) -> Path | None:
    loaded = config or load_config(repo_root)
    collections = loaded.get("collections", {})
    raw_path = str(collections.get("skills_root", "")).strip()
    if not raw_path:
        return None
    return resolve_repo_path(repo_root, raw_path)


def has_installable_skill_source(repo_root: Path, config: dict | None = None) -> bool:
    skills_root = configured_skills_root(repo_root, config)
    if skills_root is None or not skills_root.is_dir():
        return False
    return any(path.is_dir() and (path / "SKILL.md").exists() for path in skills_root.iterdir())


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


def verify_steps(repo_root: Path, config: dict | None = None) -> list[dict]:
    loaded = config or load_config(repo_root)
    steps = []
    if has_test_suite(repo_root):
        steps.append(
            {
                "name": "tests",
                "command": ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
                "cwd": repo_root,
            }
        )
    steps.append(
        {
            "name": "bootstrap",
            "command": ["bash", "./scripts/context-spine/bootstrap.sh"],
            "cwd": repo_root,
        }
    )
    if has_installable_skill_source(repo_root, loaded):
        steps.append(
            {
                "name": "skill_validate",
                "command": ["bash", "./scripts/context-spine/install-codex-skill.sh", "--validate-only"],
                "cwd": repo_root,
            }
        )
    if shutil.which("qmd"):
        steps.extend(
            [
                {
                    "name": "retrieval_lexical",
                    "command": ["bash", "./scripts/context-spine/refresh.sh"],
                    "cwd": repo_root,
                },
                {
                    "name": "retrieval_embed",
                    "command": ["bash", "./scripts/context-spine/qmd-refresh.sh", "--embed"],
                    "cwd": repo_root,
                    "optional_on_failure": True,
                    "timeout_seconds": 30,
                },
            ]
        )
    steps.extend(
        [
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
        ]
    )
    return steps


def run_step(step: dict) -> dict:
    started = dt.datetime.now(dt.UTC)
    timeout_seconds = step.get("timeout_seconds")
    process = subprocess.Popen(
        step["command"],
        cwd=str(step["cwd"]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        stdout_tail = tail_lines(stdout)
        stderr_tail = tail_lines(stderr)
        summary = summarize_output(stdout, stderr, process.returncode)
        status = "success"
        if process.returncode != 0:
            status = "warn" if step.get("optional_on_failure") else "fail"
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        finished = dt.datetime.now(dt.UTC)
        status = "warn" if step.get("optional_on_failure") else "fail"
        return {
            "name": step["name"],
            "command": step["command"],
            "cwd": str(step["cwd"]),
            "status": status,
            "optional_on_failure": bool(step.get("optional_on_failure")),
            "returncode": -1,
            "started_at": started.replace(microsecond=0).isoformat(),
            "finished_at": finished.replace(microsecond=0).isoformat(),
            "duration_seconds": round((finished - started).total_seconds(), 3),
            "summary": f"Timed out after {timeout_seconds} second(s).",
            "stdout_tail": tail_lines((exc.stdout or "") + (stdout or "")),
            "stderr_tail": tail_lines((exc.stderr or "") + (stderr or "")),
        }
    finished = dt.datetime.now(dt.UTC)
    return {
        "name": step["name"],
        "command": step["command"],
        "cwd": str(step["cwd"]),
        "status": status,
        "optional_on_failure": bool(step.get("optional_on_failure")),
        "returncode": process.returncode,
        "started_at": started.replace(microsecond=0).isoformat(),
        "finished_at": finished.replace(microsecond=0).isoformat(),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "summary": summary,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }


def verification_event_payload(
    run_handle,
    steps: list[dict],
    failed: list[str],
    warned: list[str],
    summary: str,
    status: str,
) -> dict:
    return {
        "summary": summary,
        "source": "context-spine",
        "source_command": "context:verify",
        "status": status,
        "run_id": run_handle.run_id,
        "refs": [str(run_handle.path)],
        "verification_steps": [
            {
                "name": step["name"],
                "status": step["status"],
                "summary": step["summary"],
                "duration_seconds": step["duration_seconds"],
                "optional_on_failure": step.get("optional_on_failure", False),
            }
            for step in steps
        ],
        "failed_steps": failed,
        "warned_steps": warned,
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

    steps = [run_step(step) for step in verify_steps(repo_root, config)]
    failed = [step["name"] for step in steps if step["status"] == "fail"]
    warned = [step["name"] for step in steps if step["status"] == "warn"]
    if failed:
        status = "fail"
        summary = f"Verification failed in {len(failed)} required step(s): {', '.join(failed)}."
    elif warned:
        status = "warn"
        summary = (
            "Verification passed on the core path, but optional capability checks warned in "
            f"{len(warned)} step(s): {', '.join(warned)}."
        )
    else:
        status = "success"
        summary = "Verification passed across the configured core path."

    finish_run(
        run_handle,
        status=status,
        summary=summary,
        artifacts=[],
        extra={
            "steps": steps,
            "failed_steps": failed,
            "warned_steps": warned,
        },
    )
    event_path = write_event(
        memory_root,
        "verification",
        verification_event_payload(run_handle, steps, failed, warned, summary, status),
        event_id=f"verification-{run_handle.run_id}",
    )

    print(f"Run ID: {run_handle.run_id}")
    print("===== CONTEXT VERIFY =====")
    for step in steps:
        print(f"[{step['status'].upper()}] {step['name']}: {step['summary']}")
    print(f"Event: {event_path}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
