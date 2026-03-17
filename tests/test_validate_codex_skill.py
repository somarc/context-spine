import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


validate_codex_skill = load_script_module("validate_codex_skill", "validate-codex-skill.py")


def write_skill(skill_dir: Path, *, description: str = "Demo skill") -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: demo-skill\n"
        f"description: {description}\n"
        "---\n\n"
        "# Demo\n",
        encoding="utf-8",
    )


class ValidateCodexSkillTest(unittest.TestCase):
    def test_compare_skill_dirs_matches_when_contents_align(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            target_dir = Path(tmpdir) / "target"
            write_skill(source_dir)
            write_skill(target_dir)

            source_digest, target_digest = validate_codex_skill.compare_skill_dirs(source_dir, target_dir)

            self.assertEqual(source_digest, target_digest)

    def test_compare_skill_dirs_detects_drift(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            target_dir = Path(tmpdir) / "target"
            write_skill(source_dir, description="Source skill")
            write_skill(target_dir, description="Target skill")

            with self.assertRaises(ValueError):
                validate_codex_skill.compare_skill_dirs(source_dir, target_dir)


if __name__ == "__main__":
    unittest.main()
