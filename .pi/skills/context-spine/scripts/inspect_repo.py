#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path


def load_package_scripts(root: Path) -> dict[str, str]:
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def preferred_commands(root: Path, scripts: dict[str, str]) -> dict[str, str]:
    commands = {}
    for name in ("init", "update", "embed", "bootstrap", "session", "score", "skill:install", "skill:validate"):
        script_name = f"context:{name}"
        if script_name in scripts:
            commands[name] = f"npm run {script_name}"

    script_root = root / "scripts" / "context-spine"
    fallback = {
        "init": "bash ./scripts/context-spine/init-qmd.sh",
        "update": "bash ./scripts/context-spine/qmd-refresh.sh",
        "embed": "bash ./scripts/context-spine/qmd-refresh.sh --embed",
        "bootstrap": "bash ./scripts/context-spine/bootstrap.sh",
        "session": f"python3 ./scripts/context-spine/mem-session.py --project {root.name}",
        "score": "python3 ./scripts/context-spine/mem-score.py --root ./meta/context-spine",
        "skill:install": "bash ./scripts/context-spine/install-codex-skill.sh",
        "skill:validate": "bash ./scripts/context-spine/install-codex-skill.sh --validate-only",
    }
    for key, value in fallback.items():
        if key in commands:
            continue
        if key.startswith("skill:") and not (script_root / "install-codex-skill.sh").exists():
            continue
        if key == "update" and not (script_root / "qmd-refresh.sh").exists():
            continue
        if key == "embed" and not (script_root / "qmd-refresh.sh").exists():
            continue
        if key == "init" and not (script_root / "init-qmd.sh").exists():
            continue
        if key == "bootstrap" and not (script_root / "bootstrap.sh").exists():
            continue
        if key == "session" and not (script_root / "mem-session.py").exists():
            continue
        if key == "score" and not (script_root / "mem-score.py").exists():
            continue
        commands[key] = value
    return commands


def latest_session_info(memory_root: Path) -> dict[str, object] | None:
    sessions_dir = memory_root / "sessions"
    if not sessions_dir.is_dir():
        return None
    sessions = sorted(sessions_dir.glob("*-session.md"))
    if not sessions:
        return None
    latest = sessions[-1]
    session_date = latest.name[:10]
    age_days = None
    try:
        age_days = (dt.date.today() - dt.date.fromisoformat(session_date)).days
    except ValueError:
        pass
    return {
        "path": str(latest),
        "age_days": age_days,
    }


def classify_repo(root: Path, memory_root: Path, script_root: Path) -> str:
    has_memory = memory_root.is_dir()
    has_scripts = script_root.is_dir()
    if has_memory and has_scripts:
        return "existing"
    if has_memory or has_scripts:
        return "partial"
    return "missing"


def build_report(root: Path) -> dict[str, object]:
    memory_root = root / "meta" / "context-spine"
    script_root = root / "scripts" / "context-spine"
    package_scripts = load_package_scripts(root)
    commands = preferred_commands(root, package_scripts)
    baseline_notes = sorted(memory_root.glob("spine-notes-*.md")) if memory_root.is_dir() else []
    latest_session = latest_session_info(memory_root)
    report = {
        "repo_root": str(root),
        "mode": classify_repo(root, memory_root, script_root),
        "surfaces": {
            "meta_context_spine": memory_root.is_dir(),
            "scripts_context_spine": script_root.is_dir(),
            "docs_adr": (root / "docs" / "adr").is_dir(),
            "docs_runbooks": (root / "docs" / "runbooks").is_dir(),
            "agent_diagrams": (root / ".agent" / "diagrams").is_dir(),
            "local_skill_source": (root / ".pi" / "skills" / "context-spine").is_dir(),
        },
        "baseline_notes": [str(path) for path in baseline_notes],
        "latest_session": latest_session,
        "preferred_commands": commands,
        "next_steps": [],
    }

    if report["mode"] == "existing":
        if "init" in commands:
            report["next_steps"].append(commands["init"])
        if "bootstrap" in commands:
            report["next_steps"].append(commands["bootstrap"])
        if baseline_notes:
            report["next_steps"].append(f"Open {baseline_notes[0]}")
        if not latest_session and "session" in commands:
            report["next_steps"].append(commands["session"])
    elif report["mode"] == "partial":
        report["next_steps"].append("Restore missing Context Spine surfaces before broad repo work.")
        if not baseline_notes:
            report["next_steps"].append("Add a baseline spine-notes file under meta/context-spine/.")
    else:
        report["next_steps"].append("Install Context Spine surfaces into this repo before bootstrapping.")
        report["next_steps"].append("Create one baseline note and wire repo-local wrappers.")

    return report


def print_text_report(report: dict[str, object]) -> None:
    print(f"Repo root: {report['repo_root']}")
    print(f"Mode: {report['mode']}")
    print("Surfaces:")
    for key, value in report["surfaces"].items():
        print(f"  - {key}: {'yes' if value else 'no'}")
    print("Baseline notes:")
    baseline_notes = report["baseline_notes"]
    if baseline_notes:
        for path in baseline_notes:
            print(f"  - {path}")
    else:
        print("  - none")
    print("Latest session:")
    latest_session = report["latest_session"]
    if latest_session:
        age = latest_session["age_days"]
        age_text = "unknown" if age is None else f"{age}d"
        print(f"  - {latest_session['path']} (age: {age_text})")
    else:
        print("  - none")
    print("Preferred commands:")
    commands = report["preferred_commands"]
    if commands:
        for key, value in sorted(commands.items()):
            print(f"  - {key}: {value}")
    else:
        print("  - none")
    print("Next steps:")
    for step in report["next_steps"]:
        print(f"  - {step}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a repo for Context Spine readiness.")
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    report = build_report(root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text_report(report)


if __name__ == "__main__":
    main()
