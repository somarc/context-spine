import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


memory_events = load_script_module("memory_events_for_promote", "memory_events.py")
memory_records = load_script_module("memory_records_for_promote", "memory_records.py")
promote = load_script_module("promote", "promote.py")


class PromoteTest(unittest.TestCase):
    def test_record_promotion_writes_record_and_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            (repo_root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "runbooks").mkdir(parents=True, exist_ok=True)

            adr = repo_root / "docs" / "adr" / "0007-native-memory.md"
            runbook = repo_root / "docs" / "runbooks" / "native-memory-apis.md"
            source = repo_root / "docs" / "adr" / "0006-native-codex-memory-direction.md"
            adr.write_text("# ADR\n", encoding="utf-8")
            runbook.write_text("# Runbook\n", encoding="utf-8")
            source.write_text("# Source\n", encoding="utf-8")

            result = promote.record_promotion(
                repo_root,
                memory_root,
                summary="Promoted the native memory API boundary into durable docs.",
                surface_kind="adr",
                files="docs/adr/0007-native-memory.md,docs/runbooks/native-memory-apis.md",
                refs="docs/adr/0006-native-codex-memory-direction.md",
                supersedes="draft note about runtime-owned memory",
                tags="adr,boundary",
            )

            record = memory_records.load_record(result["record_path"])
            event = memory_events.load_event(result["event_path"])

            self.assertEqual(result["promotion_schema"], "context-spine.promotion.v1")
            self.assertEqual(record["category"], "promotions")
            self.assertEqual(record["surface_kind"], "adr")
            self.assertEqual(record["files"][0], "docs/adr/0007-native-memory.md")
            self.assertEqual(record["refs"], ["docs/adr/0006-native-codex-memory-direction.md"])
            self.assertEqual(record["supersedes"], ["draft note about runtime-owned memory"])
            self.assertEqual(event["event_type"], "promotion")
            self.assertEqual(event["record_id"], record["record_id"])
            self.assertIn("docs/runbooks/native-memory-apis.md", event["files"])
            self.assertTrue(result["run_id"].startswith("ctx-context-promote-"))

    def test_record_promotion_requires_existing_repo_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)

            with self.assertRaises(ValueError):
                promote.record_promotion(
                    repo_root,
                    memory_root,
                    summary="Should fail.",
                    files="docs/missing.md",
                )


if __name__ == "__main__":
    unittest.main()
