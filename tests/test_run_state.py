import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import run_state


class RunStateTest(unittest.TestCase):
    def test_start_and_finish_run_persist_json_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            manifest_path = repo_root / "scripts" / "context-spine" / "runtime-manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text('{"runtime_version":"test-version"}\n', encoding="utf-8")

            handle = run_state.start_run(
                repo_root,
                memory_root,
                "context:test",
                args={"strict": True},
            )

            self.assertTrue(handle.path.exists())
            started_payload = json.loads(handle.path.read_text(encoding="utf-8"))
            self.assertEqual(started_payload["status"], "running")
            self.assertEqual(started_payload["runtime_version"], "test-version")
            self.assertIn("automatic_capture", started_payload)
            self.assertFalse(started_payload["automatic_capture"]["git_start"]["available"])

            run_state.finish_run(
                handle,
                status="success",
                summary="Completed test run.",
                artifacts=["/tmp/report.md"],
                extra={"count": 1},
            )

            finished_payload = json.loads(handle.path.read_text(encoding="utf-8"))
            self.assertEqual(finished_payload["status"], "success")
            self.assertEqual(finished_payload["summary"], "Completed test run.")
            self.assertEqual(finished_payload["artifacts"], ["/tmp/report.md"])
            self.assertEqual(finished_payload["extra"]["count"], 1)
            self.assertIsNotNone(finished_payload["finished_at"])

    def test_run_state_captures_git_snapshot_and_diff_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            manifest_path = repo_root / "scripts" / "context-spine" / "runtime-manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text('{"runtime_version":"test-version"}\n', encoding="utf-8")

            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True, capture_output=True, text=True)

            tracked = repo_root / "README.md"
            tracked.write_text("# Demo\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=repo_root, check=True, capture_output=True, text=True)

            tracked.write_text("# Demo\n\nchanged\n", encoding="utf-8")

            handle = run_state.start_run(repo_root, memory_root, "context:verify")
            run_state.finish_run(handle, status="success", summary="Captured git state.")

            payload = json.loads(handle.path.read_text(encoding="utf-8"))
            automatic_capture = payload["automatic_capture"]
            self.assertTrue(automatic_capture["git_start"]["available"])
            self.assertTrue(automatic_capture["git_finish"]["available"])
            self.assertEqual(automatic_capture["classification"]["family"], "verification")
            self.assertIn("tests", automatic_capture["classification"]["signals"])
            self.assertGreaterEqual(automatic_capture["git_start"]["changed_path_count"], 1)
            self.assertGreaterEqual(automatic_capture["git_start"]["diff_vs_head"]["files_changed"], 1)
            self.assertFalse(automatic_capture["git_delta"]["head_changed"])


if __name__ == "__main__":
    unittest.main()
