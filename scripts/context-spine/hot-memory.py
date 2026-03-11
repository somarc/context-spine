#!/usr/bin/env python3
import argparse
import datetime as dt
from pathlib import Path


def default_memory_root() -> Path:
    return Path(__file__).resolve().parents[2] / "meta" / "context-spine"


def infer_collection_root(memory_root: Path) -> Path:
    if memory_root.name == "context-spine" and memory_root.parent.name == "meta":
        return memory_root.parent
    return memory_root


def infer_repo_root(memory_root: Path) -> Path:
    if not (memory_root.name == "context-spine" and memory_root.parent.name == "meta"):
        return memory_root
    parents = memory_root.parents
    if len(parents) > 2:
        return parents[2]
    return memory_root


def main():
    parser = argparse.ArgumentParser(description="Generate a hot-memory index from recent file mtimes.")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days")
    parser.add_argument("--collection", default="context-spine-meta", help="QMD collection name for links")
    parser.add_argument("--root", default="", help="Override memory root directory")
    args = parser.parse_args()

    memory_root = Path(args.root).expanduser() if args.root else default_memory_root()
    collection_root = infer_collection_root(memory_root)
    repo_root = infer_repo_root(memory_root)
    cutoff = dt.datetime.now() - dt.timedelta(days=args.days)

    exclude = {"README.md", "hot-memory-index.md", "memory-scorecard.md"}
    items = []
    for path in memory_root.rglob("*.md"):
        if path.name in exclude:
            continue
        try:
            mtime = dt.datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        rel_collection = path.relative_to(collection_root)
        rel_repo = path.relative_to(repo_root)
        qmd_path = f"qmd://{args.collection}/{rel_collection.as_posix()}" if args.collection else ""
        items.append((mtime, qmd_path, rel_repo.as_posix()))

    items.sort(key=lambda item: item[0], reverse=True)

    lines = [
        "# Hot Memory Index",
        "",
        f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Window: last {args.days} days (by file modified time)",
        "",
    ]
    if not items:
        lines.append("- No recent memory entries found.")
    else:
        for mtime, qmd_path, rel_repo in items:
            stamp = mtime.strftime("%Y-%m-%d %H:%M")
            if qmd_path:
                lines.append(f"- {stamp} - {qmd_path} ({rel_repo})")
            else:
                lines.append(f"- {stamp} - {rel_repo}")

    out_file = memory_root / "hot-memory-index.md"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
