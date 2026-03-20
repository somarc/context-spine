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

    def test_shell_variables_expose_skills_collection_and_query(self):
        variables = context_config.shell_variables(Path("/tmp/context-spine-test-root"))

        self.assertEqual(
            variables["CONFIG_CONTEXT_SPINE_SKILLS_COLLECTION"],
            context_config.DEFAULT_CONFIG["collections"]["skills"],
        )
        self.assertEqual(
            variables["CONFIG_CONTEXT_SPINE_QMD_QUERY_SKILLS"],
            context_config.DEFAULT_CONFIG["qmd"]["queries"]["skills"],
        )
        self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_MODE"], "repo")
        self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_SCOPE_LABEL"], "repo spine")
        self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_REPO_COUNT"], "0")
        self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_LINKED_COUNT"], "0")

    def test_shell_variables_detect_workspace_topology(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = repo_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "project": "oak-workspace",
                        "project_space": {
                            "mode": "workspace",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            child_repo = repo_root / "oak-child"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine" / "spine-notes-oak-child.md").write_text("# Baseline\n", encoding="utf-8")
            (child_repo / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)

            variables = context_config.shell_variables(repo_root)

            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_MODE"], "workspace")
            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_SCOPE_LABEL"], "meta spine")
            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_ROOT_GIT"], "0")
            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_REPO_COUNT"], "1")
            self.assertEqual(variables["CONFIG_CONTEXT_SPINE_PROJECT_SPACE_CHILD_EXISTING_COUNT"], "1")


if __name__ == "__main__":
    unittest.main()
