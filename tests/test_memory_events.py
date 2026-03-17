import datetime as dt
import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


memory_events = load_script_module("memory_events", "memory_events.py")


class MemoryEventsTest(unittest.TestCase):
    def test_write_event_persists_structured_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir) / "meta" / "context-spine"
            event_path = memory_events.write_event(
                memory_root,
                "decision",
                {"summary": "Boundary clarified", "source": "codex"},
                event_id="decision-demo",
                recorded_at=dt.datetime(2026, 3, 17, 2, 0, 0, tzinfo=dt.UTC),
            )

            self.assertTrue(event_path.exists())
            self.assertIn("events/2026-03-17", event_path.as_posix())
            payload = memory_events.load_event(event_path)
            self.assertEqual(payload["event_schema"], "context-spine.memory-event.v1")
            self.assertEqual(payload["event_type"], "decision")
            self.assertEqual(payload["summary"], "Boundary clarified")

    def test_latest_events_returns_newest_first(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir) / "meta" / "context-spine"
            memory_events.write_event(
                memory_root,
                "retrieval",
                {"summary": "Earlier event"},
                event_id="retrieval-early",
                recorded_at=dt.datetime(2026, 3, 17, 1, 0, 0, tzinfo=dt.UTC),
            )
            latest_path = memory_events.write_event(
                memory_root,
                "verification",
                {"summary": "Later event"},
                event_id="verification-late",
                recorded_at=dt.datetime(2026, 3, 17, 2, 0, 0, tzinfo=dt.UTC),
            )

            items = memory_events.latest_events(memory_root, limit=2)

            self.assertEqual(items[0][0], latest_path)
            self.assertEqual(items[0][1]["summary"], "Later event")


if __name__ == "__main__":
    unittest.main()
