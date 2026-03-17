import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


memory_events = load_script_module("memory_events_for_query", "memory_events.py")
memory_records = load_script_module("memory_records_for_query", "memory_records.py")
query_core = load_script_module("query_core", "query_core.py")
run_state = load_script_module("run_state_for_query", "run_state.py")


class QueryTest(unittest.TestCase):
    def test_build_query_payload_returns_layered_runtime_view(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "runbooks").mkdir(parents=True, exist_ok=True)

            baseline = memory_root / "spine-notes-demo.md"
            baseline.write_text(
                "---\n"
                "source_of_truth:\n"
                "  - docs/adr/0001-demo.md\n"
                "  - docs/runbooks/demo.md\n"
                "---\n\n"
                "# Baseline\n\n"
                "## Current State\n"
                "- Durable project truth exists.\n",
                encoding="utf-8",
            )
            (repo_root / "docs" / "adr" / "0001-demo.md").write_text("# ADR\n", encoding="utf-8")
            (repo_root / "docs" / "runbooks" / "demo.md").write_text("# Runbook\n", encoding="utf-8")

            sessions_dir = memory_root / "sessions"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            (sessions_dir / "2026-03-17-session.md").write_text(
                "# Session\n\n"
                "## Summary\n"
                "- Build query and rehydrate commands.\n\n"
                "## Next Actions\n"
                "- Implement the JSON query contract.\n"
                "- Add tests.\n",
                encoding="utf-8",
            )
            (memory_root / "hot-memory-index.md").write_text("# Hot Memory Index\n", encoding="utf-8")
            (memory_root / "memory-state.json").write_text("{}\n", encoding="utf-8")

            memory_records.write_record(
                memory_root,
                "sessions",
                {"title": "Session record"},
                record_id="session-demo",
            )
            memory_events.write_event(
                memory_root,
                "decision",
                {"summary": "Accepted a native memory API boundary.", "source": "codex"},
                event_id="decision-demo",
            )
            handle = run_state.start_run(repo_root, memory_root, "context:verify")
            run_state.finish_run(handle, status="success", summary="Verify completed.")

            payload = query_core.build_query_payload(repo_root, memory_root, mode="active-delivery")

            self.assertEqual(payload["query_schema"], "context-spine.query.v1")
            self.assertEqual(payload["flow_state"]["inferred"], "active")
            self.assertEqual(payload["active_objective"]["text"], "Implement the JSON query contract.")
            self.assertGreaterEqual(len(payload["authoritative_surfaces"]), 3)
            self.assertTrue(any(item["kind"] == "baseline" for item in payload["authoritative_surfaces"]))
            self.assertTrue(any(item["kind"] == "session" for item in payload["authoritative_surfaces"]))
            self.assertTrue(any(item["kind"] == "source-of-truth" for item in payload["authoritative_surfaces"]))
            self.assertTrue(any(item["kind"] == "generated-hot-memory" for item in payload["source_hydration"]))
            self.assertTrue(any(item["kind"] == "generated-state" for item in payload["source_hydration"]))
            self.assertEqual(payload["next_actions"][0]["text"], "Implement the JSON query contract.")
            self.assertEqual(payload["machine_context"]["recent_runs"][0]["command"], "context:verify")
            self.assertEqual(payload["machine_context"]["recent_events"][0]["event_type"], "decision")
            self.assertEqual(payload["metacognitive_check"]["status"], "grounded")

    def test_build_query_payload_flags_missing_session_as_recovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (memory_root / "spine-notes-demo.md").write_text("# Baseline\n", encoding="utf-8")

            payload = query_core.build_query_payload(repo_root, memory_root, mode="active-delivery")

            self.assertEqual(payload["flow_state"]["inferred"], "recovery")
            self.assertTrue(any(item["label"] == "Missing latest session" for item in payload["stale_or_suspect_truths"]))
            self.assertEqual(payload["metacognitive_check"]["status"], "partial")


if __name__ == "__main__":
    unittest.main()
