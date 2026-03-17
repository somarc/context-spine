import unittest

import runtime_manifest

from helpers import ROOT


class RuntimeManifestTest(unittest.TestCase):
    def test_manifest_loads_with_runtime_version(self):
        manifest = runtime_manifest.load_runtime_manifest(ROOT)

        self.assertIn("runtime_version", manifest)
        self.assertTrue(str(manifest["runtime_version"]).strip())

    def test_declared_runtime_files_exist(self):
        for relative_path in runtime_manifest.runtime_files(ROOT):
            self.assertTrue((ROOT / relative_path).exists(), relative_path)


if __name__ == "__main__":
    unittest.main()
