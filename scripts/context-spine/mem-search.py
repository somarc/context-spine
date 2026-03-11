#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


def run_qmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or f"qmd failed: {' '.join(cmd)}")
    return result.stdout


def parse_indices(value):
    if not value:
        return []
    values = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            values.extend(range(int(start), int(end) + 1))
        else:
            values.append(int(part))
    return values


def main():
    parser = argparse.ArgumentParser(description="Search Context Spine memory with progressive disclosure.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", type=int, default=8, help="Number of results")
    parser.add_argument("-c", "--collection", default="context-spine-meta", help="QMD collection")
    parser.add_argument("--mode", choices=["search", "query", "vsearch"], default="search", help="QMD mode")
    parser.add_argument("--get", default="", help="Comma-separated result indices to fetch")
    parser.add_argument("--lines", type=int, default=200, help="Lines to fetch per document")
    args = parser.parse_args()

    raw = run_qmd(["qmd", args.mode, args.query, "-n", str(args.n), "--json", "-c", args.collection])
    try:
        results = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Unexpected qmd output: {exc}") from exc

    if not results:
        print("No results.")
        return

    for index, item in enumerate(results, start=1):
        score = item.get("score", "")
        file_path = item.get("file", "")
        snippet = item.get("snippet", "").replace("\n", " ").strip()
        print(f"[{index}] score={score} file={file_path}")
        if snippet:
            print(f"    {snippet}")

    for index in parse_indices(args.get):
        if index < 1 or index > len(results):
            print(f"Skipping invalid index: {index}", file=sys.stderr)
            continue
        file_path = results[index - 1].get("file")
        if not file_path:
            continue
        print("\n" + "=" * 80)
        print(f"FILE: {file_path}")
        print("=" * 80)
        print(run_qmd(["qmd", "get", file_path, "-l", str(args.lines)]).rstrip())


if __name__ == "__main__":
    main()
