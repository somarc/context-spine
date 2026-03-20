import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import load_script_module


hot_memory = load_script_module("hot_memory", "hot-memory.py")
project_space = load_script_module("project_space_for_hot_memory", "project_space.py")


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

    def test_workspace_working_set_surfaces_child_spines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            memory_root = workspace_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (memory_root / "spine-notes-workspace.md").write_text("# Workspace\n", encoding="utf-8")

            child_repo = workspace_root / "repo-a"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine").mkdir(parents=True, exist_ok=True)
            (child_repo / "meta" / "context-spine" / "spine-notes-repo-a.md").write_text("# Child\n", encoding="utf-8")
            (child_repo / "meta" / "context-spine" / "hot-memory-index.md").write_text("# Hot Memory Index\n", encoding="utf-8")
            (child_repo / "scripts" / "context-spine").mkdir(parents=True, exist_ok=True)

            detected = project_space.detect_project_space(
                workspace_root,
                {"project_space": {"mode": "workspace"}},
            )

            items = hot_memory.build_working_set(
                memory_root,
                workspace_root,
                7,
                project_mode=detected.mode,
                children=detected.child_repos,
            )

            project_vertebrae = [item for item in items if item.section == "Project Vertebrae"]
            self.assertEqual(len(project_vertebrae), 1)
            self.assertIn("repo-a", project_vertebrae[0].title)
            self.assertEqual(project_vertebrae[0].path.name, "hot-memory-index.md")

    def test_workspace_working_set_can_surface_linked_child_vertebra(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            memory_root = workspace_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (memory_root / "spine-notes-workspace.md").write_text("# Workspace\n", encoding="utf-8")

            child_repo = workspace_root / "repo-linked"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / ".context-spine.json").write_text(
                '{\n'
                '  "version": 1,\n'
                '  "mode": "linked-child",\n'
                '  "workspace_root": "..",\n'
                '  "project_name": "Repo Linked"\n'
                '}\n',
                encoding="utf-8",
            )

            detected = project_space.detect_project_space(
                workspace_root,
                {"project_space": {"mode": "workspace"}},
            )

            items = hot_memory.build_working_set(
                memory_root,
                workspace_root,
                7,
                project_mode=detected.mode,
                children=detected.child_repos,
            )

            project_vertebrae = [item for item in items if item.section == "Project Vertebrae"]
            self.assertEqual(len(project_vertebrae), 1)
            self.assertEqual(project_vertebrae[0].path.name, ".context-spine.json")

    def test_main_uses_overridden_root_config_for_workspace_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            memory_root = workspace_root / "meta" / "context-spine"
            memory_root.mkdir(parents=True, exist_ok=True)
            (memory_root / "spine-notes-workspace.md").write_text("# Workspace\n", encoding="utf-8")
            (memory_root / "context-spine.json").write_text('{"project_space":{"mode":"workspace","child_repos":["repo-linked"]}}\n', encoding="utf-8")

            child_repo = workspace_root / "repo-linked"
            (child_repo / ".git").mkdir(parents=True, exist_ok=True)
            (child_repo / ".context-spine.json").write_text(
                '{\n'
                '  "version": 1,\n'
                '  "mode": "linked-child",\n'
                '  "workspace_root": ".."\n'
                '}\n',
                encoding="utf-8",
            )

            with mock.patch("sys.argv", ["hot-memory.py", "--root", str(memory_root)]):
                result = hot_memory.main()

            rendered = (memory_root / "hot-memory-index.md").read_text(encoding="utf-8")

            self.assertEqual(result, 0)
            self.assertIn("Project space: workspace", rendered)
            self.assertIn("## Project Vertebrae", rendered)
            self.assertIn(".context-spine.json", rendered)


if __name__ == "__main__":
    unittest.main()
