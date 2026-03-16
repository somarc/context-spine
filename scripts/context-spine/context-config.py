#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_config import load_config, render_shell_variables


def main() -> int:
    parser = argparse.ArgumentParser(description="Print Context Spine repo configuration.")
    parser.add_argument("--repo-root", default="", help="Target repo root; defaults to this repo")
    parser.add_argument("--format", choices=["json", "shell"], default="json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser() if args.repo_root else None
    if args.format == "shell":
        print(render_shell_variables(repo_root), end="")
    else:
        print(json.dumps(load_config(repo_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
