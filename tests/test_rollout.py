import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


rollout = load_script_module("rollout", "rollout.py")


class RolloutTest(unittest.TestCase):
    def test_doctor_status_reads_json_even_when_command_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            script = root / "fake-doctor.py"
            script.write_text(
                "import json, sys\n"
                "out = sys.argv[-1]\n"
                "with open(out, 'w', encoding='utf-8') as handle:\n"
                "    json.dump({'counts': {'pass': 0, 'warn': 1, 'fail': 1}}, handle)\n"
                "sys.exit(1)\n",
                encoding="utf-8",
            )

            counts = rollout.doctor_status(root, script)

            self.assertEqual(counts, {"pass": 0, "warn": 1, "fail": 1})

    def test_expand_targets_includes_workspace_children(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            config_path = workspace_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                '{\n'
                '  "project_space": {\n'
                '    "mode": "workspace"\n'
                "  }\n"
                "}\n",
                encoding="utf-8",
            )

            child_repo = workspace_root / "repo-a"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)

            targets = rollout.expand_targets([workspace_root])

            self.assertEqual(len(targets), 2)
            self.assertEqual(targets[0][1], "workspace-root")
            self.assertEqual(targets[1][1], "child-repo")
            self.assertEqual(targets[1][2], workspace_root.resolve())

    def test_expand_targets_includes_linked_child_repos(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            config_path = workspace_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text('{"project_space":{"mode":"workspace"}}\n', encoding="utf-8")

            child_repo = workspace_root / "repo-linked"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / ".context-spine.json").write_text(
                '{\n'
                '  "version": 1,\n'
                '  "mode": "linked-child",\n'
                '  "workspace_root": ".."\n'
                '}\n',
                encoding="utf-8",
            )

            targets = rollout.expand_targets([workspace_root])

            self.assertEqual(len(targets), 2)
            self.assertEqual(targets[1][0], child_repo.resolve())
            self.assertEqual(targets[1][1], "child-repo")


if __name__ == "__main__":
    unittest.main()
