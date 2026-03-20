import unittest
from unittest import mock
import json
import tempfile
from pathlib import Path

from helpers import load_script_module


verify = load_script_module("verify", "verify.py")


class VerifyHelpersTest(unittest.TestCase):
    def test_tail_lines_returns_last_nonempty_lines(self):
        payload = verify.tail_lines("one\n\ntwo\nthree\n", limit=2)
        self.assertEqual(payload, ["two", "three"])

    def test_summarize_output_prefers_stdout_then_stderr(self):
        self.assertEqual(verify.summarize_output("alpha\nbeta\n", "", 0), "beta")
        self.assertEqual(verify.summarize_output("", "error\nboom\n", 1), "boom")
        self.assertEqual(verify.summarize_output("", "", 2), "Command exited with code 2.")

    def test_verification_event_payload_condenses_steps(self):
        class Handle:
            run_id = "ctx-demo"
            path = "/tmp/demo.json"

        payload = verify.verification_event_payload(
            Handle(),
            [{"name": "tests", "status": "success", "summary": "OK", "duration_seconds": 0.2, "optional_on_failure": False}],
            [],
            [],
            "Verification passed.",
            "success",
        )

        self.assertEqual(payload["source_command"], "context:verify")
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["run_id"], "ctx-demo")
        self.assertEqual(payload["verification_steps"][0]["name"], "tests")
        self.assertEqual(payload["warned_steps"], [])

    def test_verify_steps_include_bootstrap_and_core_checks_without_qmd(self):
        with mock.patch.object(verify.shutil, "which", return_value=None):
            steps = verify.verify_steps(verify.default_repo_root())

        names = [step["name"] for step in steps]
        self.assertIn("bootstrap", names)
        self.assertIn("doctor", names)
        self.assertIn("score", names)
        self.assertNotIn("retrieval_lexical", names)
        self.assertNotIn("retrieval_embed", names)

    def test_verify_steps_skip_tests_and_skill_validate_when_surfaces_absent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (repo_root / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)

            with mock.patch.object(verify.shutil, "which", return_value=None):
                steps = verify.verify_steps(repo_root)

        names = [step["name"] for step in steps]
        self.assertNotIn("tests", names)
        self.assertNotIn("skill_validate", names)
        self.assertIn("bootstrap", names)

    def test_verify_steps_use_configured_skills_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = repo_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "collections": {
                            "skills_root": ".agents/skills",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            skill_dir = repo_root / ".agents" / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

            with mock.patch.object(verify.shutil, "which", return_value=None):
                steps = verify.verify_steps(repo_root)

        names = [step["name"] for step in steps]
        self.assertIn("skill_validate", names)

    def test_verify_steps_add_qmd_checks_when_available(self):
        with mock.patch.object(verify.shutil, "which", return_value="/usr/bin/qmd"):
            steps = verify.verify_steps(verify.default_repo_root())

        names = [step["name"] for step in steps]
        self.assertIn("retrieval_lexical", names)
        self.assertIn("retrieval_embed", names)
        embed_step = next(step for step in steps if step["name"] == "retrieval_embed")
        self.assertTrue(embed_step["optional_on_failure"])
        self.assertEqual(embed_step["timeout_seconds"], 30)


if __name__ == "__main__":
    unittest.main()
