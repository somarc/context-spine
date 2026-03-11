#!/usr/bin/env python3
import re
import sys
from pathlib import Path


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


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: validate-codex-skill.py <skill_directory>")
    skill_dir = Path(sys.argv[1]).expanduser().resolve()
    validate_skill(skill_dir)
    print("Skill is valid!")


if __name__ == "__main__":
    main()
