#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_config import load_config, resolve_repo_path
from query_core import QUERY_MODES, build_rehydrate_payload
from run_state import finish_run, start_run


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_memory_root(repo_root: Path) -> Path:
    config = load_config(repo_root)
    return resolve_repo_path(repo_root, str(config.get("memory_root", "meta/context-spine"))).resolve()


def main():
    parser = argparse.ArgumentParser(description="Emit a compact Context Spine rehydration packet.")
    parser.add_argument("--mode", default="active-delivery", choices=sorted(QUERY_MODES))
    parser.add_argument("--objective", default="", help="Optional caller-supplied objective for this rehydration packet.")
    parser.add_argument("--limit", type=int, default=6, help="Maximum number of surfaces to include in list fields.")
    parser.add_argument("--root", default="", help="Override memory root directory.")
    args = parser.parse_args()

    repo_root = default_repo_root()
    memory_root = (Path(args.root).expanduser() if args.root else default_memory_root(repo_root)).resolve()
    handle = start_run(repo_root, memory_root, "context:rehydrate", args=vars(args))

    try:
        payload = build_rehydrate_payload(
            repo_root,
            memory_root,
            mode=args.mode,
            requested_objective=args.objective,
            limit=max(1, args.limit),
            exclude_run_id=handle.run_id,
        )
        print(json.dumps(payload, indent=2))
        finish_run(
            handle,
            status="success",
            summary=f"Built rehydration packet in {args.mode} mode.",
            extra={
                "mode": args.mode,
                "objective": args.objective,
                "output_schema": payload["rehydrate_schema"],
            },
        )
    except Exception as exc:
        finish_run(
            handle,
            status="failure",
            summary=f"Failed to build rehydration packet: {exc}",
            extra={"mode": args.mode, "objective": args.objective},
        )
        raise


if __name__ == "__main__":
    main()
