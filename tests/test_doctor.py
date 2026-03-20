import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import doctor
import context_config


class DoctorConfigTest(unittest.TestCase):
    def test_check_config_warns_when_explicit_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            config_path = context_config.default_config_path(repo_root)

            result = doctor.check_config(
                repo_root,
                memory_root,
                context_config.DEFAULT_CONFIG,
                config_path,
                "",
                project_mode="repo",
            )

            self.assertEqual(result.status, doctor.WARN)
            self.assertIn("No explicit `context-spine.json` config is present.", result.summary)

    def test_check_config_suggests_linked_child_when_parent_workspace_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir) / "OAK"
            repo_root = workspace_root / "repo-a"
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (workspace_root / "meta" / "context-spine" / "context-spine.json").parent.mkdir(parents=True, exist_ok=True)
            (workspace_root / "meta" / "context-spine" / "context-spine.json").write_text(
                '{"project_space":{"mode":"workspace","child_repos":["repo-a"]}}\n',
                encoding="utf-8",
            )

            result = doctor.check_config(
                repo_root,
                memory_root,
                context_config.DEFAULT_CONFIG,
                context_config.default_config_path(repo_root),
                "",
                project_mode="repo",
            )

            self.assertTrue(any("Nearest workspace spine" in detail for detail in result.details))
            self.assertTrue(any("adopt-mode linked-child" in action for action in result.actions))

    def test_check_config_passes_with_explicit_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = context_config.default_config_path(repo_root)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "project": "demo-repo",
                        "memory_root": "meta/context-spine",
                        "baseline": {"preferred_file": "spine-notes-demo.md"},
                        "collections": {"meta": "demo-meta"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            config = context_config.load_config(repo_root)
            memory_root = context_config.resolve_repo_path(repo_root, config["memory_root"])

            result = doctor.check_config(repo_root, memory_root, config, config_path, "", project_mode="repo")

            self.assertEqual(result.status, doctor.PASS)
            self.assertIn("Explicit Context Spine config is present.", result.summary)

    def test_check_retrieval_warns_without_qmd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir)
            with mock.patch.object(doctor.shutil, "which", return_value=None):
                result = doctor.check_retrieval(memory_root)

            self.assertEqual(result.status, doctor.WARN)
            self.assertIn("QMD is not installed", result.summary)

    def test_check_retrieval_warns_when_latest_embed_probe_failed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir)
            local_index = memory_root / ".qmd" / "index.sqlite"
            local_index.parent.mkdir(parents=True, exist_ok=True)
            local_index.write_text("", encoding="utf-8")

            run_path = memory_root / "runs" / "2026-03-17" / "verify.json"
            run_path.parent.mkdir(parents=True, exist_ok=True)
            run_path.write_text(
                json.dumps(
                    {
                        "command": "context:verify",
                        "extra": {
                            "steps": [
                                {"name": "retrieval_embed", "status": "warn", "summary": "sqlite-vec unavailable"}
                            ]
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with mock.patch.object(doctor.shutil, "which", return_value="/usr/bin/qmd"):
                result = doctor.check_retrieval(memory_root)

            self.assertEqual(result.status, doctor.WARN)
            self.assertIn("latest embed capability probe warned", result.summary)

    def test_check_project_space_accepts_non_git_workspace_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            child_repo = repo_root / "repo-a"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine" / "spine-notes-repo-a.md").write_text("# A\n", encoding="utf-8")
            (child_repo / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)

            config = {
                "project_space": {
                    "mode": "workspace",
                }
            }

            result = doctor.check_project_space(repo_root, config)

            self.assertEqual(result.status, doctor.PASS)
            self.assertIn("Project mode: workspace", result.details)
            self.assertIn("Workspace root has no `.git`, which is valid in workspace mode.", result.details)

    def test_check_config_accepts_linked_child_vertebra(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            workspace_root = repo_root.parent / "workspace-root"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (repo_root / ".context-spine.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "mode": "linked-child",
                        "workspace_root": "../workspace-root",
                        "project_name": "Repo A",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = doctor.check_config(
                repo_root,
                workspace_root / "meta" / "context-spine",
                {},
                context_config.default_config_path(repo_root),
                "",
                project_mode="linked-child",
            )

            self.assertEqual(result.status, doctor.PASS)
            self.assertIn("Linked-child vertebra contract is present", result.summary)

    def test_check_linked_workspace_surface_passes_when_parent_spine_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            workspace_root = repo_root.parent / "workspace-root"
            parent_memory = workspace_root / "meta" / "context-spine"
            parent_memory.mkdir(parents=True, exist_ok=True)
            (parent_memory / "spine-notes-workspace.md").write_text("# Workspace\n", encoding="utf-8")
            (repo_root / ".context-spine.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "mode": "linked-child",
                        "workspace_root": "../workspace-root",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            project_space = doctor.detect_project_space(repo_root, {})
            result = doctor.check_linked_workspace_surface(project_space)

            self.assertEqual(result.status, doctor.PASS)
            self.assertIn("parent workspace spine", result.summary)


if __name__ == "__main__":
    unittest.main()
