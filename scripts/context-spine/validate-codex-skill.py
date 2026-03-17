#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

from runtime_manifest import directory_digest


MAX_SKILL_NAME_LENGTH = 64
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}


def extract_frontmatter(content: str) -> str:
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise ValueError("Invalid or missing YAML frontmatter")
    return match.group(1)


def parse_top_level_keys(frontmatter: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        data[key] = value
    return data


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def validate_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise ValueError("SKILL.md not found")

    content = skill_md.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    data = parse_top_level_keys(frontmatter)

    unexpected = sorted(set(data) - ALLOWED_FRONTMATTER_KEYS)
    if unexpected:
        allowed = ", ".join(sorted(ALLOWED_FRONTMATTER_KEYS))
        raise ValueError(
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(unexpected)}. "
            f"Allowed properties are: {allowed}"
        )

    for required in ("name", "description"):
        if required not in data:
            raise ValueError(f"Missing '{required}' in frontmatter")

    name = unquote(data["name"].strip())
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ValueError("Name must be hyphen-case (lowercase letters, digits, and hyphens only)")
    if name.startswith("-") or name.endswith("-") or "--" in name:
        raise ValueError("Name cannot start/end with hyphen or contain consecutive hyphens")
    if len(name) > MAX_SKILL_NAME_LENGTH:
        raise ValueError(f"Name is too long ({len(name)} characters); max is {MAX_SKILL_NAME_LENGTH}")

    description = unquote(data["description"].strip())
    if not description:
        raise ValueError("Description must not be empty")
    if "<" in description or ">" in description:
        raise ValueError("Description cannot contain angle brackets")
    if len(description) > 1024:
        raise ValueError(f"Description is too long ({len(description)} characters); max is 1024")


def compare_skill_dirs(source_dir: Path, target_dir: Path) -> tuple[str, str]:
    validate_skill(source_dir)
    validate_skill(target_dir)
    source_digest = directory_digest(source_dir)
    target_digest = directory_digest(target_dir)
    if source_digest != target_digest:
        raise ValueError(
            "Installed skill drift detected. "
            f"source={source_digest} target={target_digest}"
        )
    return source_digest, target_digest


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or compare Context Spine Codex skill directories.")
    parser.add_argument("skill_directory", nargs="?", help="Single skill directory to validate")
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("SOURCE_DIR", "TARGET_DIR"),
        help="Validate both skill directories and compare normalized directory digests",
    )
    args = parser.parse_args()

    if args.compare:
        source_dir = Path(args.compare[0]).expanduser().resolve()
        target_dir = Path(args.compare[1]).expanduser().resolve()
        source_digest, target_digest = compare_skill_dirs(source_dir, target_dir)
        print(f"Skill digests match: {source_digest}")
        print(f"Source: {source_dir}")
        print(f"Target: {target_dir}")
        assert source_digest == target_digest
        return

    if not args.skill_directory:
        raise SystemExit("Usage: validate-codex-skill.py <skill_directory> | --compare <source_dir> <target_dir>")

    skill_dir = Path(args.skill_directory).expanduser().resolve()
    validate_skill(skill_dir)
    print("Skill is valid!")


if __name__ == "__main__":
    main()
