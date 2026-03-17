import datetime as dt
import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


memory_records = load_script_module("memory_records", "memory_records.py")


class MemoryRecordsTest(unittest.TestCase):
    def test_write_record_persists_structured_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir) / "meta" / "context-spine"
            record_path = memory_records.write_record(
                memory_root,
                "observations",
                {"summary": "Observation", "files": ["README.md"]},
                record_id="obs-demo",
                recorded_at=dt.datetime(2026, 3, 17, 1, 0, 0, tzinfo=dt.UTC),
            )

            self.assertTrue(record_path.exists())
            self.assertIn("records/observations/2026-03-17", record_path.as_posix())
            payload = memory_records.load_record(record_path)
            self.assertEqual(payload["record_schema"], "context-spine.memory-record.v1")
            self.assertEqual(payload["category"], "observations")
            self.assertEqual(payload["record_id"], "obs-demo")
            self.assertEqual(payload["summary"], "Observation")

    def test_latest_record_returns_newest_by_mtime(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir) / "meta" / "context-spine"
            first = memory_records.write_record(
                memory_root,
                "sessions",
                {"title": "First"},
                record_id="first",
                recorded_at=dt.datetime(2026, 3, 17, 1, 0, 0, tzinfo=dt.UTC),
            )
            second = memory_records.write_record(
                memory_root,
                "sessions",
                {"title": "Second"},
                record_id="second",
                recorded_at=dt.datetime(2026, 3, 17, 2, 0, 0, tzinfo=dt.UTC),
            )

            latest_path, latest_payload = memory_records.latest_record(memory_root, "sessions")

            self.assertEqual(latest_path, second)
            self.assertEqual(latest_payload["title"], "Second")
            self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
