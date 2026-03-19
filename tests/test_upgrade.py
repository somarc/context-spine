import json
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

import upgrade


class UpgradeTest(unittest.TestCase):
    def test_context_config_file_is_safe_additive_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)

            result = upgrade.evaluate(target_root, ROOT, apply_safe=False, gitignore_mode="")

            self.assertIn("meta/context-spine/context-spine.json", result.safe_missing)
            self.assertIn("scripts/context-spine/pull-and-rollout.py", result.safe_missing)
            self.assertIn("scripts/context-spine/setup.sh", result.safe_missing)
            self.assertIn("scripts/context-spine/refresh.sh", result.safe_missing)

    def test_context_config_file_is_merge_review_when_customized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            config_path = target_root / "meta" / "context-spine" / "context-spine.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps({"project": "custom-project"}) + "\n", encoding="utf-8")

            result = upgrade.evaluate(target_root, ROOT, apply_safe=False, gitignore_mode="")

            self.assertIn("meta/context-spine/context-spine.json", result.merge_different)


if __name__ == "__main__":
    unittest.main()
