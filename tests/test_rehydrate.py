import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


rehydrate_core = load_script_module("query_core_for_rehydrate", "query_core.py")


class RehydrateTest(unittest.TestCase):
    def test_build_rehydrate_payload_returns_compact_packet(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (memory_root / "spine-notes-demo.md").write_text(
                "# Baseline\n\n## Current State\n- Project truth is available.\n",
                encoding="utf-8",
            )
            sessions_dir = memory_root / "sessions"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            (sessions_dir / "2026-03-17-session.md").write_text(
                "# Session\n\n## Summary\n- Ship the first runtime packet.\n\n## Next Actions\n- Emit the rehydrate JSON packet.\n",
                encoding="utf-8",
            )

            payload = rehydrate_core.build_rehydrate_payload(
                repo_root,
                memory_root,
                mode="active-delivery",
                requested_objective="Hand a compact packet to an external runtime.",
            )

            self.assertEqual(payload["rehydrate_schema"], "context-spine.rehydrate.v1")
            self.assertEqual(payload["active_objective"]["text"], "Hand a compact packet to an external runtime.")
            self.assertIn("authoritative_surfaces", payload)
            self.assertIn("source_hydration", payload)
            self.assertIn("critical_path", payload)
            self.assertIn("metacognitive_check", payload)
            self.assertNotIn("memory_state_export", payload)


if __name__ == "__main__":
    unittest.main()
