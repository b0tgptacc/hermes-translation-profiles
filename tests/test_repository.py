from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_repository.py"
spec = importlib.util.spec_from_file_location("verify_repository", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RepositoryTest(unittest.TestCase):
    def test_manifest_and_secret_scan(self):
        result = module.verify()
        self.assertEqual(result["status"], "PASS", result["failures"])

    def test_expected_profiles(self):
        result = module.verify()
        self.assertEqual([p["name"] for p in result["profiles"]], ["translator", "fasttranslator"])

    def test_skill_count(self):
        result = module.verify()
        self.assertEqual(result["skills"], 8)


if __name__ == "__main__":
    unittest.main()
