import json
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


if __name__ == "__main__":
    unittest.main()
