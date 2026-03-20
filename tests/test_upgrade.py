import json
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

import upgrade


class UpgradeTest(unittest.TestCase):
    def test_context_config_file_is_safe_additive_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)

            result = upgrade.evaluate(target_root, ROOT, apply_safe=False, gitignore_mode="")

            self.assertIn("meta/context-spine/context-spine.json", result.safe_missing)
            self.assertIn("scripts/context-spine/pull-and-rollout.py", result.safe_missing)
            self.assertIn("scripts/context-spine/setup.sh", result.safe_missing)
            self.assertIn("scripts/context-spine/refresh.sh", result.safe_missing)

    def test_context_config_file_is_merge_review_when_customized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            config_path = target_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps({"project": "custom-project"}) + "\n", encoding="utf-8")

            result = upgrade.evaluate(target_root, ROOT, apply_safe=False, gitignore_mode="")

            self.assertIn("meta/context-spine/context-spine.json", result.merge_different)

    def test_workspace_target_reports_child_repo_topology(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            config_path = target_root / "meta" / "context-spine" / "context-spine.json"
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
            (target_root / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)
            (target_root / "meta" / "context-spine" / "spine-notes-workspace.md").write_text("# Workspace\n", encoding="utf-8")

            child_repo = target_root / "repo-a"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine" / "spine-notes-repo-a.md").write_text("# Child\n", encoding="utf-8")
            (child_repo / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)

            result = upgrade.evaluate(target_root, ROOT, apply_safe=False, gitignore_mode="")

            self.assertEqual(result.project_mode, "workspace")
            self.assertFalse(result.root_git)
            self.assertEqual(result.child_repo_count, 1)
            self.assertEqual(result.child_existing_count, 1)

    def test_linked_child_target_is_not_treated_as_missing_install(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            workspace_root = target_root.parent / "workspace-root"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (target_root / ".git").mkdir(parents=True, exist_ok=True)
            (target_root / ".context-spine.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "mode": "linked-child",
                        "workspace_root": "../workspace-root",
                        "truth_policy": "external",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = upgrade.evaluate(target_root, ROOT, apply_safe=False, gitignore_mode="")

            self.assertEqual(result.mode, "linked-child")
            self.assertEqual(result.project_mode, "linked-child")
            self.assertEqual(result.safe_missing, [])
            self.assertIn("Linked child points to workspace root", " ".join(result.notes))

    def test_upgrade_can_adopt_linked_child_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace_root = root / "workspace-root"
            target_root = root / "repo-a"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            (target_root / ".git").mkdir(parents=True, exist_ok=True)
            (target_root / "meta" / "context-spine" / "runs" / "2026-03-20").mkdir(parents=True, exist_ok=True)

            result = upgrade.evaluate(
                target_root,
                ROOT,
                apply_safe=False,
                gitignore_mode="",
                adopt_mode="linked-child",
                workspace_root_arg=str(workspace_root),
                project_name="Repo A",
                truth_policy="external",
            )

            payload = json.loads((target_root / ".context-spine.json").read_text(encoding="utf-8"))

            self.assertEqual(result.mode, "linked-child")
            self.assertEqual(result.project_mode, "linked-child")
            self.assertEqual(payload["workspace_root"], "../workspace-root")
            self.assertEqual(payload["project_id"], "repo-a")
            self.assertEqual(payload["project_name"], "Repo A")
            self.assertIn("Wrote linked-child vertebra contract", " ".join(result.notes))

    def test_upgrade_can_autodiscover_parent_workspace_for_linked_child(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "aem-code"
            workspace_root = root / "OAK"
            target_root = workspace_root / "repo-a"
            (workspace_root / "meta" / "context-spine" / "context-spine.json").parent.mkdir(parents=True, exist_ok=True)
            (workspace_root / "meta" / "context-spine" / "context-spine.json").write_text(
                '{"project_space":{"mode":"workspace","child_repos":["repo-a"]}}\n',
                encoding="utf-8",
            )
            target_root.mkdir(parents=True, exist_ok=True)
            (target_root / ".git").mkdir(parents=True, exist_ok=True)
            (target_root / "meta" / "context-spine" / "runs" / "2026-03-20").mkdir(parents=True, exist_ok=True)

            result = upgrade.evaluate(
                target_root,
                ROOT,
                apply_safe=False,
                gitignore_mode="",
                adopt_mode="linked-child",
                project_name="Repo A",
                truth_policy="external",
            )

            payload = json.loads((target_root / ".context-spine.json").read_text(encoding="utf-8"))

            self.assertEqual(result.mode, "linked-child")
            self.assertEqual(payload["workspace_root"], "..")
            self.assertIn("Auto-discovered parent workspace spine", " ".join(result.notes))

    def test_upgrade_does_not_overwrite_existing_linked_child_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace_root = root / "workspace-root"
            target_root = root / "repo-a"
            (workspace_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            (target_root / ".git").mkdir(parents=True, exist_ok=True)
            contract_path = target_root / ".context-spine.json"
            contract_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "mode": "linked-child",
                        "workspace_root": "../workspace-root",
                        "project_id": "existing-id",
                        "project_name": "Existing Name",
                        "truth_policy": "external",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = upgrade.evaluate(
                target_root,
                ROOT,
                apply_safe=False,
                gitignore_mode="",
                adopt_mode="linked-child",
                workspace_root_arg=str(workspace_root),
                project_name="New Name",
                truth_policy="external",
            )

            payload = json.loads(contract_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["project_name"], "Existing Name")
            self.assertIn("differs; review it manually", " ".join(result.notes))


if __name__ == "__main__":
    unittest.main()
