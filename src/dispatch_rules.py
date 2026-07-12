"""
dispatch_rules.py — Dispatching rules for the fab capacity simulation.

Each rule receives:
    ready_queue : list[dict] — operations ready for dispatch.
        Each dict has keys:
            lot_id, operation_id, operation_seq, tool_id, run_time,
            queue_start_time (timestamp in hours float)

    current_time : float — current simulation clock (hours from epoch)

    lot_info : dict[str, dict] — lot-level metadata keyed by lot_id.
        Each has keys: due_ts_hours, total_remaining_run_time

Returns:
    The selected operation dict from ready_queue.
"""

import math


# ---------------------------------------------------------------------------
# Rule 1: First-In-First-Out
# The operation that entered the queue earliest goes first.
# ---------------------------------------------------------------------------
def fifo(ready_queue: list[dict], current_time: float, lot_info: dict) -> dict:
    """Earliest queue_start_time first."""
    return min(ready_queue, key=lambda op: op["queue_start_time"])


# ---------------------------------------------------------------------------
# Rule 2: Shortest Processing Time
# The operation with the shortest run_time goes first.
# ---------------------------------------------------------------------------
def spt(ready_queue: list[dict], current_time: float, lot_info: dict) -> dict:
    """Shortest run_time first.  Reduces average flow time."""
    return min(ready_queue, key=lambda op: op["run_time"])


# ---------------------------------------------------------------------------
# Rule 3: Earliest Due Date
# The lot with the earliest due date goes first.
# ---------------------------------------------------------------------------
def edd(ready_queue: list[dict], current_time: float, lot_info: dict) -> dict:
    """Earliest due date (lot-level) first.  Improves on-time performance."""
    return min(ready_queue, key=lambda op: lot_info[op["lot_id"]]["due_ts_hours"])


# ---------------------------------------------------------------------------
# Rule 4: Critical Ratio
# CR = (due_date - current_time) / remaining_processing_time
# Smaller CR → higher delay risk → dispatch first.
# ---------------------------------------------------------------------------
def cr(ready_queue: list[dict], current_time: float, lot_info: dict) -> dict:
    """Smallest Critical Ratio first.  Prioritises at-risk lots."""
    def _critical_ratio(op):
        due = lot_info[op["lot_id"]]["due_ts_hours"]
        remaining = lot_info[op["lot_id"]]["total_remaining_run_time"]
        slack = due - current_time
        if remaining <= 0:
            return -float("inf") if slack < 0 else float("inf")
        return slack / remaining

    return min(ready_queue, key=_critical_ratio)


# ---------------------------------------------------------------------------
# Optional: Longest Remaining Processing Time
# ---------------------------------------------------------------------------
def lrpt(ready_queue: list[dict], current_time: float, lot_info: dict) -> dict:
    """Longest remaining processing time first."""
    return max(ready_queue, key=lambda op: lot_info[op["lot_id"]]["total_remaining_run_time"])


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------
RULES = {
    "FIFO": fifo,
    "SPT":  spt,
    "EDD":  edd,
    "CR":   cr,
    "LRPT": lrpt,
}

RULE_LABELS = {
    "FIFO": "First-In-First-Out",
    "SPT":  "Shortest Processing Time",
    "EDD":  "Earliest Due Date",
    "CR":   "Critical Ratio",
    "LRPT": "Longest Remaining Processing Time",
}
