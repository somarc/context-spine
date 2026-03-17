import tempfile
import unittest
from pathlib import Path

from helpers import load_script_module


generated_artifact = load_script_module("generated_artifact", "generated_artifact.py")


class GeneratedArtifactTest(unittest.TestCase):
    def test_publish_generated_artifacts_promotes_valid_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "hot-memory-index.md"

            published = generated_artifact.publish_generated_artifacts(
                [
                    generated_artifact.GeneratedArtifactSpec(
                        path=target,
                        content="# Hot Memory Index\n\nBody.\n",
                        validator=generated_artifact.markdown_heading_validator("# Hot Memory Index"),
                    )
                ],
                run_id="ctx-hot-memory",
            )

            self.assertEqual(target.read_text(encoding="utf-8"), "# Hot Memory Index\n\nBody.\n")
            self.assertEqual([item.path for item in published], [target])
            leftover = [path for path in root.iterdir() if path.name.endswith(".candidate")]
            self.assertEqual(leftover, [])

    def test_publish_generated_artifacts_keeps_active_file_when_validation_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "doctor-report.md"
            target.write_text("# Context Doctor Report\n\nExisting.\n", encoding="utf-8")

            with self.assertRaises(generated_artifact.ArtifactValidationError):
                generated_artifact.publish_generated_artifacts(
                    [
                        generated_artifact.GeneratedArtifactSpec(
                            path=target,
                            content="# Wrong Heading\n\nBroken.\n",
                            validator=generated_artifact.markdown_heading_validator("# Context Doctor Report"),
                        )
                    ],
                    run_id="ctx-doctor",
                )

            self.assertEqual(target.read_text(encoding="utf-8"), "# Context Doctor Report\n\nExisting.\n")
            leftover = [path for path in root.iterdir() if path.name.endswith(".candidate")]
            self.assertEqual(leftover, [])

    def test_publish_generated_artifacts_validates_all_candidates_before_promotion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            markdown_target = root / "rollout-report.md"
            json_target = root / "rollout-report.json"
            markdown_target.write_text("# Context Spine Rollout Report\n\nExisting.\n", encoding="utf-8")
            json_target.write_text('{"status":"existing"}\n', encoding="utf-8")

            with self.assertRaises(generated_artifact.ArtifactValidationError):
                generated_artifact.publish_generated_artifacts(
                    [
                        generated_artifact.GeneratedArtifactSpec(
                            path=markdown_target,
                            content="# Context Spine Rollout Report\n\nNew.\n",
                            validator=generated_artifact.markdown_heading_validator("# Context Spine Rollout Report"),
                        ),
                        generated_artifact.GeneratedArtifactSpec(
                            path=json_target,
                            content="not-json\n",
                            validator=generated_artifact.validate_json_artifact,
                        ),
                    ],
                    run_id="ctx-rollout",
                )

            self.assertEqual(markdown_target.read_text(encoding="utf-8"), "# Context Spine Rollout Report\n\nExisting.\n")
            self.assertEqual(json_target.read_text(encoding="utf-8"), '{"status":"existing"}\n')
            leftover = [path for path in root.iterdir() if path.name.endswith(".candidate")]
            self.assertEqual(leftover, [])


if __name__ == "__main__":
    unittest.main()
