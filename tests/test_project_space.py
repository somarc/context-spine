import json
import tempfile
import unittest
from pathlib import Path

import context_config
from helpers import load_script_module


project_space = load_script_module("project_space", "project_space.py")


class ProjectSpaceTest(unittest.TestCase):
    def test_detects_non_git_workspace_with_child_repos(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            config_path = workspace_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "project_space": {
                            "mode": "workspace",
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            child_existing = workspace_root / "repo-a"
            (child_existing / ".git").mkdir(parents=True, exist_ok=True)
            (child_existing / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (child_existing / "meta" / "context-spine" / "spine-notes-repo-a.md").write_text("# A\n", encoding="utf-8")
            (child_existing / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)

            child_missing = workspace_root / "repo-b"
            (child_missing / ".git").mkdir(parents=True, exist_ok=True)

            detected = project_space.detect_project_space(
                workspace_root,
                json.loads(config_path.read_text(encoding="utf-8")),
            )
            summary = project_space.summarize_project_space(detected)

            self.assertEqual(detected.mode, "workspace")
            self.assertFalse(detected.root_git)
            self.assertEqual(summary["child_repo_count"], 2)
            self.assertEqual(summary["child_existing_count"], 1)
            self.assertEqual(summary["child_missing_count"], 1)
            self.assertEqual([child.relative_path for child in detected.child_repos], ["repo-a", "repo-b"])

    def test_detects_linked_child_mode_from_vertebra_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            workspace_root = repo_root.parent / "workspace-root"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (repo_root / ".git").mkdir(parents=True, exist_ok=True)
            (repo_root / ".context-spine.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "mode": "linked-child",
                        "workspace_root": "../workspace-root",
                        "project_id": "repo-a",
                        "project_name": "Repo A",
                        "truth_policy": "external",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            detected = project_space.detect_project_space(repo_root, {})
            summary = project_space.summarize_project_space(detected)

            self.assertEqual(detected.mode, "linked-child")
            self.assertTrue(detected.root_git)
            self.assertTrue(summary["linked_workspace_ready"])
            self.assertIsNotNone(detected.vertebra)
            self.assertEqual(detected.vertebra.project_name, "Repo A")
            self.assertEqual(detected.vertebra.workspace_root, workspace_root.resolve())

    def test_linked_child_mode_beats_implicit_default_repo_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            workspace_root = repo_root.parent / "workspace-root"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (repo_root / ".git").mkdir(parents=True, exist_ok=True)
            (repo_root / ".context-spine.json").write_text(
                '{\n'
                '  "version": 1,\n'
                '  "mode": "linked-child",\n'
                '  "workspace_root": "../workspace-root"\n'
                '}\n',
                encoding="utf-8",
            )

            detected = project_space.detect_project_space(repo_root, context_config.load_config(repo_root))

            self.assertEqual(detected.mode, "linked-child")

    def test_generated_artifacts_do_not_mask_linked_child_install_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            workspace_root = repo_root.parent / "workspace-root"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (repo_root / ".git").mkdir(parents=True, exist_ok=True)
            (repo_root / "meta" / "context-spine" / "runs" / "2026-03-20").mkdir(parents=True, exist_ok=True)
            (repo_root / ".context-spine.json").write_text(
                '{\n'
                '  "version": 1,\n'
                '  "mode": "linked-child",\n'
                '  "workspace_root": "../workspace-root"\n'
                '}\n',
                encoding="utf-8",
            )

            self.assertEqual(project_space.install_state(repo_root), "linked-child")

    def test_nearest_workspace_root_prefers_closest_workspace_ancestor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            top_root = Path(tmpdir) / "aem-code"
            project_root = top_root / "OAK"
            repo_root = project_root / "oak-chain-docs"

            (top_root / "meta" / "context-spine" / "context-spine.json").parent.mkdir(parents=True, exist_ok=True)
            (top_root / "meta" / "context-spine" / "context-spine.json").write_text(
                '{"project_space":{"mode":"workspace","child_repos":["OAK"]}}\n',
                encoding="utf-8",
            )
            (project_root / "meta" / "context-spine" / "context-spine.json").parent.mkdir(parents=True, exist_ok=True)
            (project_root / "meta" / "context-spine" / "context-spine.json").write_text(
                '{"project_space":{"mode":"workspace","child_repos":["oak-chain-docs"]}}\n',
                encoding="utf-8",
            )
            (repo_root / ".git").mkdir(parents=True, exist_ok=True)

            self.assertEqual(project_space.nearest_workspace_root(repo_root), project_root.resolve())

    def test_scope_label_tracks_meta_project_and_repo_layers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            top_root = Path(tmpdir) / "aem-code"
            project_root = top_root / "OAK"
            repo_root = project_root / "oak-chain-docs"

            (top_root / "meta" / "context-spine" / "context-spine.json").parent.mkdir(parents=True, exist_ok=True)
            (top_root / "meta" / "context-spine" / "context-spine.json").write_text(
                '{"project_space":{"mode":"workspace","child_repos":["OAK"]}}\n',
                encoding="utf-8",
            )
            (project_root / "meta" / "context-spine" / "context-spine.json").parent.mkdir(parents=True, exist_ok=True)
            (project_root / "meta" / "context-spine" / "context-spine.json").write_text(
                '{"project_space":{"mode":"workspace","child_repos":["oak-chain-docs"]}}\n',
                encoding="utf-8",
            )
            (repo_root / ".git").mkdir(parents=True, exist_ok=True)

            top_space = project_space.detect_project_space(top_root, project_space.load_local_config(top_root))
            project_space_node = project_space.detect_project_space(project_root, project_space.load_local_config(project_root))
            repo_space = project_space.detect_project_space(repo_root, {})

            self.assertEqual(project_space.summarize_project_space(top_space)["scope_label"], "meta spine")
            self.assertEqual(project_space.summarize_project_space(project_space_node)["scope_label"], "project spine")
            self.assertEqual(project_space.summarize_project_space(repo_space)["scope_label"], "repo spine")


if __name__ == "__main__":
    unittest.main()
