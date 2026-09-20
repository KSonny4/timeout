#!/usr/bin/env python3
"""Emit actual unittest results as a machine-readable release/CI artefact."""
import json
from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[1]
suite = unittest.defaultTestLoader.discover(str(root / "tests"))
result = unittest.TextTestRunner(verbosity=2).run(suite)
report = {"tests_run": result.testsRun, "failures": len(result.failures),
          "errors": len(result.errors), "skips": len(result.skipped),
          "successful": result.wasSuccessful(),
          "failure_details": [(str(test), text) for test, text in result.failures + result.errors],
          "skip_details": [(str(test), text) for test, text in result.skipped]}
destination = root / ".build/reports"
destination.mkdir(parents=True, exist_ok=True)
(destination / "contract.json").write_text(json.dumps(report, indent=2) + "\n")
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
