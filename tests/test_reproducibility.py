"""
test_reproducibility.py — Validate Python simulation pipeline outputs.

Checks that all expected CSV files and chart outputs exist with the
minimum required row counts and key KPI thresholds.
"""

import csv
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FIGURES_DIR = os.path.join(PROJECT_DIR, "outputs", "figures")

# (filename, min_rows, description)
EXPECTED_CSVS = [
    ("operations.csv",                 1_100,  "Parsed operations"),
    ("dim_lot.csv",                       80,  "Lot dimension"),
    ("dim_tool.csv",                      15,  "Tool dimension"),
    ("fact_schedule_event_fifo_baseline.csv", 1_100, "FIFO baseline events"),
    ("fact_capacity_calendar.csv",         60,  "Capacity calendar"),
]

EXPECTED_FIGURES = [
    "gantt_fifo.png",
    "rule_comparison.png",
    "utilization_heatmap_fifo.png",
    "bottleneck_ranking.png",
    "queue_distribution_fifo.png",
    "scenario_improvement_waterfall.png",
]

# Thresholds for the FIFO baseline summary CSV
EXPECTED_KPI = {
    "makespan": (70, 100),         # hours
    "avg_cycle_time": (40, 70),    # hours
    "on_time_rate": (90, 101),     # %
}


def test_csv_exists_and_nonempty():
    """Every expected CSV must exist and have at least the header."""
    for fname, _, desc in EXPECTED_CSVS:
        path = os.path.join(DATA_DIR, fname)
        assert os.path.exists(path), f"[FAIL] {desc} ({fname}): file not found"
        with open(path, newline="", encoding="utf-8") as f:
            row_count = sum(1 for _ in csv.reader(f))
        assert row_count >= 2, f"[FAIL] {desc} ({fname}): only {row_count} row(s)"


def test_csv_row_counts():
    """Each CSV must meet its minimum row count."""
    for fname, min_rows, desc in EXPECTED_CSVS:
        path = os.path.join(DATA_DIR, fname)
        with open(path, newline="", encoding="utf-8") as f:
            row_count = sum(1 for _ in csv.reader(f)) - 1
        assert row_count >= min_rows, (
            f"[FAIL] {desc} ({fname}): {row_count} rows < {min_rows}"
        )
        print(f"  [OK] {fname}: {row_count} rows ≥ {min_rows}")


def test_figures_exist():
    """All expected chart files must exist and be non-trivial."""
    for fname in EXPECTED_FIGURES:
        path = os.path.join(FIGURES_DIR, fname)
        assert os.path.exists(path), f"[FAIL] Figure not found: {fname}"
        size = os.path.getsize(path)
        assert size > 10_000, f"[FAIL] {fname} too small: {size} bytes"
        print(f"  [OK] {fname} ({size:,} bytes)")


def test_simulation_summary_kpi():
    """FIFO baseline KPI values must fall within expected ranges."""
    path = os.path.join(DATA_DIR, "simulation_summary.csv")
    if not os.path.exists(path):
        print("  [SKIP] simulation_summary.csv not found (run run_all.py first)")
        return
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("rule_name") != "FIFO":
                continue
            for k, (lo, hi) in EXPECTED_KPI.items():
                val = float(row[k])
                assert lo <= val <= hi, (
                    f"[FAIL] FIFO {k}={val} outside [{lo}, {hi}]"
                )
                print(f"  [OK] FIFO {k}={val} in [{lo}, {hi}]")
            return
    print("  [SKIP] No FIFO row in simulation_summary.csv")


def test_script_imports():
    """All source modules must be importable (syntax check)."""
    src_dir = os.path.join(PROJECT_DIR, "src")
    for fname in sorted(os.listdir(src_dir)):
        if not fname.endswith(".py") or fname.startswith("__"):
            continue
        path = os.path.join(src_dir, fname)
        with open(path, encoding="utf-8") as f:
            try:
                compile(f.read(), path, "exec")
                print(f"  [OK] {fname}: syntax OK")
            except SyntaxError as e:
                raise AssertionError(f"[FAIL] {fname}: syntax error: {e}")


if __name__ == "__main__":
    errors = []
    for name, fn in [
        ("CSV exists & nonempty", test_csv_exists_and_nonempty),
        ("CSV row counts", test_csv_row_counts),
        ("Figures exist", test_figures_exist),
        ("KPI thresholds", test_simulation_summary_kpi),
        ("Script imports", test_script_imports),
    ]:
        try:
            print(f"\n=== {name} ===")
            fn()
        except (AssertionError, FileNotFoundError) as e:
            print(f"  {e}")
            errors.append(str(e))

    print(f"\n{'='*40}")
    if errors:
        print(f"FAILED: {len(errors)} check(s)")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)
