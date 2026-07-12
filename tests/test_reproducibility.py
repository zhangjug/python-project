"""
test_reproducibility.py — Validate Python simulation pipeline outputs.

Usage:
    python -m unittest discover -s tests -v          # unittest
    python -m pytest tests -v                         # pytest
    python tests/test_reproducibility.py              # standalone
"""

import csv
import os
import sys
import unittest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FIGURES_DIR = os.path.join(PROJECT_DIR, "outputs", "figures")

EXPECTED_CSVS = [
    ("operations.csv",                    1_100,  "Parsed operations"),
    ("dim_lot.csv",                          80,  "Lot dimension"),
    ("dim_tool.csv",                         15,  "Tool dimension"),
    ("fact_schedule_event_fifo_baseline.csv", 1_100, "FIFO baseline events"),
    ("fact_capacity_calendar.csv",           60,  "Capacity calendar"),
]

EXPECTED_FIGURES = [
    "gantt_fifo.png",
    "gantt_cr.png",
    "rule_comparison.png",
    "utilization_heatmap_fifo.png",
    "utilization_heatmap_cr.png",
    "bottleneck_ranking.png",
    "queue_distribution_fifo.png",
    "queue_distribution_cr.png",
    "scenario_improvement_waterfall.png",
]

EXPECTED_KPI = {
    "makespan": (70, 100),
    "avg_cycle_time": (40, 70),
    "on_time_rate": (90, 101),
}


class TestReproducibility(unittest.TestCase):

    def test_csv_exists_and_nonempty(self):
        """Every expected CSV must exist and have at least the header."""
        for fname, _, desc in EXPECTED_CSVS:
            path = os.path.join(DATA_DIR, fname)
            self.assertTrue(os.path.exists(path),
                            f"{desc} ({fname}): file not found")
            with open(path, newline="", encoding="utf-8") as f:
                row_count = sum(1 for _ in csv.reader(f))
            self.assertGreaterEqual(row_count, 2,
                                    f"{desc} ({fname}): only {row_count} row(s)")

    def test_csv_row_counts(self):
        """Each CSV must meet its minimum row count."""
        for fname, min_rows, desc in EXPECTED_CSVS:
            path = os.path.join(DATA_DIR, fname)
            with open(path, newline="", encoding="utf-8") as f:
                row_count = sum(1 for _ in csv.reader(f)) - 1
            self.assertGreaterEqual(
                row_count, min_rows,
                f"{desc} ({fname}): {row_count} rows < {min_rows}")

    def test_figures_exist(self):
        """All expected chart files must exist and be non-trivial."""
        for fname in EXPECTED_FIGURES:
            path = os.path.join(FIGURES_DIR, fname)
            self.assertTrue(os.path.exists(path),
                            f"Figure not found: {fname}")
            size = os.path.getsize(path)
            self.assertGreater(size, 10_000,
                               f"{fname} too small: {size} bytes")

    def test_simulation_summary_kpi(self):
        """FIFO baseline KPI values must fall within expected ranges."""
        path = os.path.join(DATA_DIR, "simulation_summary.csv")
        if not os.path.exists(path):
            self.skipTest("simulation_summary.csv not found (run run_all.py first)")
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("rule_name") != "FIFO":
                    continue
                for k, (lo, hi) in EXPECTED_KPI.items():
                    val = float(row[k])
                    self.assertGreaterEqual(val, lo, f"FIFO {k}={val} < {lo}")
                    self.assertLessEqual(val, hi, f"FIFO {k}={val} > {hi}")
                return
            self.fail("No FIFO row in simulation_summary.csv")

    def test_script_imports(self):
        """All source modules must be syntactically valid."""
        src_dir = os.path.join(PROJECT_DIR, "src")
        for fname in sorted(os.listdir(src_dir)):
            if not fname.endswith(".py") or fname.startswith("__"):
                continue
            path = os.path.join(src_dir, fname)
            with open(path, encoding="utf-8") as f:
                try:
                    compile(f.read(), path, "exec")
                except SyntaxError as e:
                    self.fail(f"{fname}: syntax error: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
