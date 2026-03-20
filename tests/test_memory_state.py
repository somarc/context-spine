import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


memory_events = load_script_module("memory_events_for_state", "memory_events.py")
memory_records = load_script_module("memory_records_for_state", "memory_records.py")
memory_state = load_script_module("memory_state", "memory-state.py")
run_state = load_script_module("run_state_for_state", "run_state.py")


class MemoryStateTest(unittest.TestCase):
    def test_build_state_summarizes_layers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)

            (repo_root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "runbooks").mkdir(parents=True, exist_ok=True)
            (repo_root / ".agent" / "diagrams").mkdir(parents=True, exist_ok=True)
            (repo_root / "meta" / "context-spine" / "evidence-packs" / "2026-03-17").mkdir(parents=True, exist_ok=True)

            (memory_root / "spine-notes-demo.md").write_text("# Baseline\n", encoding="utf-8")
            (memory_root / "sessions").mkdir(parents=True, exist_ok=True)
            (memory_root / "sessions" / "2026-03-17-session.md").write_text("# Session\n", encoding="utf-8")
            (repo_root / "docs" / "adr" / "0001-demo.md").write_text("# ADR\n", encoding="utf-8")
            (repo_root / "docs" / "runbooks" / "demo.md").write_text("# Runbook\n", encoding="utf-8")
            (repo_root / ".agent" / "diagrams" / "demo.html").write_text("<html></html>\n", encoding="utf-8")
            (repo_root / "meta" / "context-spine" / "evidence-packs" / "2026-03-17" / "demo.md").write_text("# Evidence\n", encoding="utf-8")
            (memory_root / "hot-memory-index.md").write_text("# Hot Memory Index\n", encoding="utf-8")

            memory_records.write_record(
                memory_root,
                "sessions",
                {"title": "Session record"},
                record_id="session-demo",
            )
            memory_records.write_record(
                memory_root,
                "observations",
                {"summary": "Observation record"},
                record_id="observation-demo",
            )
            memory_records.write_record(
                memory_root,
                "promotions",
                {"summary": "Promotion record"},
                record_id="promotion-demo",
            )
            memory_records.write_record(
                memory_root,
                "invalidations",
                {"summary": "Invalidation record"},
                record_id="invalidation-demo",
            )
            memory_events.write_event(
                memory_root,
                "decision",
                {"summary": "Promoted a durable boundary.", "source": "codex"},
                event_id="decision-demo",
            )
            handle = run_state.start_run(repo_root, memory_root, "context:verify")
            run_state.finish_run(
                handle,
                status="success",
                summary="Verify completed.",
                extra={
                    "steps": [
                        {"name": "tests", "status": "success"},
                        {"name": "doctor", "status": "success"},
                    ]
                },
            )

            payload = memory_state.build_state(repo_root, memory_root)

            self.assertEqual(payload["state_schema"], "context-spine.memory-state.v1")
            self.assertEqual(payload["layers"]["project"]["adr_count"], 1)
            self.assertEqual(payload["layers"]["project"]["runbook_count"], 1)
            self.assertEqual(payload["layers"]["project"]["diagram_count"], 1)
            self.assertEqual(payload["layers"]["project"]["evidence_pack_count"], 1)
            self.assertEqual(payload["layers"]["project"]["project_mode"], "repo")
            self.assertEqual(payload["layers"]["project"]["scope_label"], "repo spine")
            self.assertEqual(payload["layers"]["project"]["child_repo_count"], 0)
            self.assertEqual(payload["layers"]["project"]["child_linked_count"], 0)
            self.assertEqual(payload["layers"]["machine"]["records"]["sessions"]["count"], 1)
            self.assertEqual(payload["layers"]["machine"]["records"]["observations"]["count"], 1)
            self.assertEqual(payload["layers"]["machine"]["records"]["promotions"]["count"], 1)
            self.assertEqual(payload["layers"]["machine"]["records"]["invalidations"]["count"], 1)
            self.assertEqual(payload["layers"]["machine"]["events"]["count"], 1)
            self.assertEqual(payload["layers"]["machine"]["runs"]["count"], 1)
            self.assertEqual(payload["layers"]["machine"]["runs"]["recent"][0]["command"], "context:verify")
            self.assertEqual(payload["layers"]["machine"]["runs"]["recent"][0]["step_count"], 2)
            self.assertTrue(payload["layers"]["generated"]["hot_memory"]["exists"])
            self.assertIsNotNone(payload["layers"]["session"]["latest_markdown"])
            self.assertEqual(payload["exports"]["json"], "meta/context-spine/memory-state.json")
            self.assertEqual(payload["exports"]["html"], "meta/context-spine/memory-state.html")
            self.assertEqual(payload["summary"]["machine_record_total"], 4)
            self.assertEqual(payload["summary"]["machine_event_total"], 1)

    def test_render_memory_state_html_includes_layers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            payload = memory_state.build_state(repo_root, memory_root)

            html = memory_state.render_memory_state_html(payload)

            self.assertIn("Context Spine Memory State", html)
            self.assertIn("Visual Memory State", html)
            self.assertIn("Generated Aids", html)
            self.assertIn("meta/context-spine/memory-state.html", html)
            self.assertIn("High-Signal Events", html)
            self.assertIn("Recent Runtime Activity", html)


if __name__ == "__main__":
    unittest.main()
