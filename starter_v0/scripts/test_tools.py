from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure starter_v0 root is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.test_tools import (
    TestLookupTicketTool,
    TestCheckSoftwareCatalogTool,
    TestRegistryAndDeclarationIntegrity,
)


def run_all():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestLookupTicketTool))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckSoftwareCatalogTool))
    suite.addTests(loader.loadTestsFromTestCase(TestRegistryAndDeclarationIntegrity))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run_all()
