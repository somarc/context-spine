import json
import tempfile
import unittest
import datetime as dt
from pathlib import Path
from unittest import mock

from helpers import load_script_module


mem_score = load_script_module("mem_score", "mem-score.py")


class MemoryScoreTest(unittest.TestCase):
    def test_iso_age_days_handles_utc_timestamps_without_negative_age(self):
        value = (dt.datetime.now(dt.UTC) - dt.timedelta(minutes=5)).replace(microsecond=0).isoformat()

        age_days = mem_score.iso_age_days(value)

        self.assertIsNotNone(age_days)
        self.assertGreaterEqual(age_days, 0)

    def test_latest_run_payload_ignores_running_verify_runs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir)
            older = memory_root / "runs" / "2026-03-17" / "older.json"
            older.parent.mkdir(parents=True, exist_ok=True)
            older.write_text(
                json.dumps({"command": "context:verify", "status": "warn", "started_at": "2026-03-17T00:00:00+00:00"})
                + "\n",
                encoding="utf-8",
            )
            newer = memory_root / "runs" / "2026-03-18" / "newer.json"
            newer.parent.mkdir(parents=True, exist_ok=True)
            newer.write_text(
                json.dumps({"command": "context:verify", "status": "running", "started_at": "2026-03-18T00:00:00+00:00"})
                + "\n",
                encoding="utf-8",
            )

            payload = mem_score.latest_run_payload(memory_root, "context:verify")

        self.assertEqual(payload["status"], "warn")

    def test_score_retrieval_treats_missing_qmd_as_partial_not_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir)
            with mock.patch.object(mem_score.shutil, "which", return_value=None):
                score, details, recommendations = mem_score.score_retrieval(memory_root)

        self.assertEqual(score, 6)
        self.assertTrue(any("not installed" in detail for detail in details))
        self.assertTrue(any("Install QMD" in rec for rec in recommendations))

    def test_score_retrieval_penalizes_failed_embed_probe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir)
            local_index = memory_root / ".qmd" / "index.sqlite"
            local_index.parent.mkdir(parents=True, exist_ok=True)
            local_index.write_text("", encoding="utf-8")

            run_path = memory_root / "runs" / "2026-03-17" / "verify.json"
            run_path.parent.mkdir(parents=True, exist_ok=True)
            run_path.write_text(
                json.dumps(
                    {
                        "command": "context:verify",
                        "extra": {
                            "steps": [
                                {"name": "retrieval_lexical", "status": "success", "summary": "Lexical ready."},
                                {"name": "retrieval_embed", "status": "warn", "summary": "sqlite-vec unavailable"},
                            ]
                        },
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(mem_score.shutil, "which", return_value="/usr/bin/qmd"):
                score, details, recommendations = mem_score.score_retrieval(memory_root)

        self.assertEqual(score, 11)
        self.assertTrue(any("warned" in detail for detail in details))
        self.assertTrue(any("embeddings optional" in rec for rec in recommendations))


if __name__ == "__main__":
    unittest.main()
