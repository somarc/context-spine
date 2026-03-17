import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT, load_script_module


configure_gitignore = load_script_module("configure_gitignore", "configure-gitignore.py")


class ConfigureGitignoreTest(unittest.TestCase):
    def test_replace_and_remove_block(self):
        original = "node_modules/\n"
        tracked = configure_gitignore.render_block("tracked")
        updated = configure_gitignore.replace_block(original, tracked)

        self.assertIn("mode: tracked", updated)
        self.assertIn("node_modules/", updated)
        self.assertIn("meta/context-spine/memory-state.html", updated)
        self.assertIn("meta/context-spine/records/", updated)

        removed = configure_gitignore.remove_block(updated)
        self.assertEqual(removed, original)

    def test_cli_defaults_to_repo_config_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = repo_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps({"gitignore_mode": "local"}) + "\n", encoding="utf-8")
            (repo_root / ".gitignore").write_text("node_modules/\n", encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "context-spine" / "configure-gitignore.py"),
                    "--repo-root",
                    str(repo_root),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (repo_root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("mode: local", content)
            self.assertIn("meta/context-spine/", content)


if __name__ == "__main__":
    unittest.main()
