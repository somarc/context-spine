import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


hot_memory = load_script_module("hot_memory", "hot-memory.py")


class HotMemoryTest(unittest.TestCase):
    def test_parse_source_of_truth_resolves_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            docs_file = repo_root / "docs" / "runbooks" / "doctor.md"
            docs_file.parent.mkdir(parents=True, exist_ok=True)
            docs_file.write_text("# Doctor\n", encoding="utf-8")

            note_path = repo_root / "meta" / "context-spine" / "spine-notes-demo.md"
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(
                "---\n"
                "source_of_truth:\n"
                "  - docs/runbooks/doctor.md\n"
                "---\n",
                encoding="utf-8",
            )

            paths = hot_memory.parse_source_of_truth(note_path, repo_root)

            self.assertEqual(paths, [docs_file.resolve()])

    def test_latest_session_file_prefers_session_date_over_mtime(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            older_session = sessions_dir / "2026-03-15-session.md"
            newer_session = sessions_dir / "2026-03-16-session.md"
            older_session.write_text("# Older\n", encoding="utf-8")
            newer_session.write_text("# Newer\n", encoding="utf-8")

            # Touch the older session after the newer session to simulate later edits.
            older_session.touch()

            latest = hot_memory.latest_session_file([older_session, newer_session])

            self.assertEqual(latest, newer_session)


if __name__ == "__main__":
    unittest.main()
