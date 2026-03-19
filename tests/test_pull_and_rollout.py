import unittest
from pathlib import Path

from helpers import load_script_module


pull_and_rollout = load_script_module("pull_and_rollout", "pull-and-rollout.py")


class PullAndRolloutTest(unittest.TestCase):
    def test_build_pull_command_uses_ff_only(self):
        self.assertEqual(pull_and_rollout.build_pull_command(), ["git", "pull", "--ff-only"])

    def test_single_target_selects_upgrade_mode(self):
        self.assertEqual(pull_and_rollout.mode_for([Path("/tmp/repo")], "none"), "upgrade")

    def test_multi_target_selects_rollout_mode(self):
        self.assertEqual(
            pull_and_rollout.mode_for([Path("/tmp/repo-a"), Path("/tmp/repo-b")], "none"),
            "rollout",
        )

    def test_multi_target_rejects_gitignore_mode(self):
        with self.assertRaises(ValueError):
            pull_and_rollout.mode_for([Path("/tmp/repo-a"), Path("/tmp/repo-b")], "tracked")

    def test_build_upgrade_command_forwards_flags(self):
        command = pull_and_rollout.build_upgrade_command(
            Path("/src/context-spine"),
            Path("/work/project"),
            apply_safe=True,
            gitignore_mode="tracked",
            out="/tmp/upgrade.md",
            json_out="/tmp/upgrade.json",
        )

        self.assertEqual(command[0:4], ["python3", "/src/context-spine/scripts/context-spine/upgrade.py", "--target", "/work/project"])
        self.assertIn("--apply-safe", command)
        self.assertIn("tracked", command)
        self.assertTrue(command[-4:] == ["--out", "/tmp/upgrade.md", "--json-out", "/tmp/upgrade.json"])

    def test_build_rollout_command_forwards_flags(self):
        command = pull_and_rollout.build_rollout_command(
            Path("/src/context-spine"),
            [Path("/work/project-a"), Path("/work/project-b")],
            apply_safe=True,
            out="/tmp/rollout.md",
            json_out="/tmp/rollout.json",
        )

        self.assertEqual(command[0:3], ["python3", "/src/context-spine/scripts/context-spine/rollout.py", "--repos"])
        self.assertIn("/work/project-a", command)
        self.assertIn("/work/project-b", command)
        self.assertIn("--apply-safe", command)
        self.assertTrue(command[-4:] == ["--out", "/tmp/rollout.md", "--json-out", "/tmp/rollout.json"])


if __name__ == "__main__":
    unittest.main()
