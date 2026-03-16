import json
import tempfile
import unittest
from pathlib import Path

import context_config


class ContextConfigTest(unittest.TestCase):
    def test_deep_merge_preserves_nested_defaults(self):
        merged = context_config.deep_merge(
            {"collections": {"meta": "default-meta", "docs": "default-docs"}},
            {"collections": {"docs": "custom-docs"}},
        )

        self.assertEqual(merged["collections"]["meta"], "default-meta")
        self.assertEqual(merged["collections"]["docs"], "custom-docs")

    def test_load_config_merges_repo_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = repo_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "project": "demo-repo",
                        "collections": {"docs": "demo-docs"},
                        "gitignore_mode": "local",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            config = context_config.load_config(repo_root)

            self.assertEqual(config["project"], "demo-repo")
            self.assertEqual(config["collections"]["docs"], "demo-docs")
            self.assertEqual(config["collections"]["meta"], context_config.DEFAULT_CONFIG["collections"]["meta"])
            self.assertEqual(config["gitignore_mode"], "local")

    def test_shell_variables_resolve_repo_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = repo_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "project": "demo-repo",
                        "memory_root": ".memory/context",
                        "collections": {"meta": "demo-meta"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            variables = context_config.shell_variables(repo_root)

            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT"], "demo-repo")
            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_COLLECTION"], "demo-meta")
            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_ROOT"], str((repo_root / ".memory" / "context").resolve()))


if __name__ == "__main__":
    unittest.main()
