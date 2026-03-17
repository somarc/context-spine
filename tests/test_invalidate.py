import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


invalidate = load_script_module("invalidate", "invalidate.py")
memory_events = load_script_module("memory_events_for_invalidate", "memory_events.py")
memory_records = load_script_module("memory_records_for_invalidate", "memory_records.py")


class InvalidateTest(unittest.TestCase):
    def test_record_invalidation_writes_record_and_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            (repo_root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
            (repo_root / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)

            baseline = repo_root / "meta" / "context-spine" / "spine-notes-demo.md"
            replacement = repo_root / "docs" / "adr" / "0007-native-memory.md"
            baseline.write_text("# Baseline\n", encoding="utf-8")
            replacement.write_text("# ADR\n", encoding="utf-8")

            result = invalidate.record_invalidation(
                repo_root,
                memory_root,
                summary="Invalidated the old prompt-owned memory assumption.",
                subject="Prompt-owned global memory as durable project truth",
                replacement="docs/adr/0007-native-memory.md",
                files="meta/context-spine/spine-notes-demo.md,docs/adr/0007-native-memory.md",
                refs="docs/adr/0007-native-memory.md",
                tags="boundary,invalidation",
                status="superseded",
            )

            record = memory_records.load_record(result["record_path"])
            event = memory_events.load_event(result["event_path"])

            self.assertEqual(record["category"], "invalidations")
            self.assertEqual(record["subject"], "Prompt-owned global memory as durable project truth")
            self.assertEqual(record["replacement"], "docs/adr/0007-native-memory.md")
            self.assertEqual(record["status"], "superseded")
            self.assertEqual(event["event_type"], "invalidation")
            self.assertEqual(event["status"], "superseded")
            self.assertIn("meta/context-spine/spine-notes-demo.md", event["files"])
            self.assertTrue(result["run_id"].startswith("ctx-context-invalidate-"))


if __name__ == "__main__":
    unittest.main()
