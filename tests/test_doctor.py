import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import doctor
import context_config


class DoctorConfigTest(unittest.TestCase):
    def test_check_config_warns_when_explicit_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            memory_root = repo_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            config_path = context_config.default_config_path(repo_root)

            result = doctor.check_config(
                repo_root,
                memory_root,
                context_config.DEFAULT_CONFIG,
                config_path,
                "",
            )

            self.assertEqual(result.status, doctor.WARN)
            self.assertIn("No explicit `context-spine.json` config is present.", result.summary)

    def test_check_config_passes_with_explicit_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            config_path = context_config.default_config_path(repo_root)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(
                    {
                        "project": "demo-repo",
                        "memory_root": "meta/context-spine",
                        "baseline": {"preferred_file": "spine-notes-demo.md"},
                        "collections": {"meta": "demo-meta"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            config = context_config.load_config(repo_root)
            memory_root = context_config.resolve_repo_path(repo_root, config["memory_root"])

            result = doctor.check_config(repo_root, memory_root, config, config_path, "")

            self.assertEqual(result.status, doctor.PASS)
            self.assertIn("Explicit Context Spine config is present.", result.summary)

    def test_check_retrieval_warns_without_qmd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_root = Path(tmpdir)
            with mock.patch.object(doctor.shutil, "which", return_value=None):
                result = doctor.check_retrieval(memory_root)

            self.assertEqual(result.status, doctor.WARN)
            self.assertIn("QMD is not installed", result.summary)

    def test_check_retrieval_warns_when_latest_embed_probe_failed(self):
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
                                {"name": "retrieval_embed", "status": "warn", "summary": "sqlite-vec unavailable"}
                            ]
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with mock.patch.object(doctor.shutil, "which", return_value="/usr/bin/qmd"):
                result = doctor.check_retrieval(memory_root)

            self.assertEqual(result.status, doctor.WARN)
            self.assertIn("latest embed capability probe warned", result.summary)


if __name__ == "__main__":
    unittest.main()
