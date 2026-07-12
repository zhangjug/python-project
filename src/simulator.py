"""
simulator.py — Discrete-event simulation engine for fab-like job-shop scheduling.

Models a fab production system where:
  - Each lot follows a fixed route (sequence of operations on specific tools).
  - Each tool processes one operation at a time.
  - An operation starts when: (a) the lot's previous op is done, and
    (b) the target tool is free.
  - When multiple operations compete for the same tool, a dispatching rule
    selects the winner.

Usage:
    from simulator import run_simulation
    events, summary = run_simulation(operations, lot_data, rule_name="FIFO")
"""

import csv
import os
import sys
from copy import deepcopy
from collections import defaultdict

# Allow importing from sibling src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dispatch_rules import RULES, RULE_LABELS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _load_operations(csv_path: str) -> list[dict]:
    """Load operations.csv into a list of dicts."""
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["operation_seq"] = int(r["operation_seq"])
            r["run_time"] = float(r["run_time"])
            rows.append(r)
    return rows


def _load_lot_data(csv_path: str) -> dict:
    """Load dim_lot.csv → dict[lot_id] = {release_ts, due_ts, priority, product_family}."""
    lots = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lots[r["lot_id"]] = r
    return lots


def _timestamp_to_hours(ts_str: str, epoch_ts_str: str) -> float:
    """Convert ISO timestamp to hours offset from epoch."""
    from datetime import datetime
    fmt = "%Y-%m-%d %H:%M:%S"
    dt = datetime.strptime(ts_str, fmt)
    epoch = datetime.strptime(epoch_ts_str, fmt)
    return (dt - epoch).total_seconds() / 3600.0


# ---------------------------------------------------------------------------
# Simulation core
# ---------------------------------------------------------------------------
def run_simulation(
    operations: list[dict],
    lot_data: dict,
    rule_name: str = "FIFO",
    scenario_id: str = "baseline",
    bottleneck_speedup: dict[str, float] | None = None,
    extra_tool: str | None = None,
) -> tuple[list[dict], dict]:
    """Run one discrete-event simulation.

    Parameters
    ----------
    operations : list[dict]
        Parsed operations with keys: instance_id, lot_id, operation_seq, tool_id, run_time.
    lot_data : dict
        lot_id → {release_ts, due_ts, priority, …}
    rule_name : str
        One of FIFO, SPT, EDD, CR, LRPT.
    scenario_id : str
        Label for this simulation scenario (e.g. "baseline", "bottleneck_+10%").
    bottleneck_speedup : dict or None
        tool_id → speedup_factor (e.g. {"T03": 0.9} → 10% less run time).
    extra_tool : str or None
        If set, adds a parallel tool identical to the named tool (increases capacity).

    Returns
    -------
    events : list[dict]
        Per-operation event log.
    summary : dict
        Aggregate KPIs for this scenario.
    """
    # --- prepare data structures ---
    # Group operations by lot, sorted by op_seq
    lot_ops: dict[str, list[dict]] = defaultdict(list)
    for op in operations:
        lot_ops[op["lot_id"]].append(deepcopy(op))
    for ops in lot_ops.values():
        ops.sort(key=lambda x: x["operation_seq"])

    # Determine epoch (earliest release_ts)
    from datetime import datetime
    fmt = "%Y-%m-%d %H:%M:%S"
    all_release = [lot_data[lid]["release_ts"] for lid in lot_ops]
    epoch_str = min(all_release)
    epoch_dt = datetime.strptime(epoch_str, fmt)

    def ts_to_h(ts_str: str) -> float:
        return (datetime.strptime(ts_str, fmt) - epoch_dt).total_seconds() / 3600.0

    # Build lot_info for dispatching rules
    lot_info: dict[str, dict] = {}
    for lot_id in lot_ops:
        # Total remaining run time = sum of all op run times
        total_run = sum(op["run_time"] for op in lot_ops[lot_id])
        # Apply speedup if any op's tool is in bottleneck_speedup
        if bottleneck_speedup:
            adjusted_run = 0.0
            for op in lot_ops[lot_id]:
                factor = bottleneck_speedup.get(op["tool_id"], 1.0)
                adjusted_run += op["run_time"] * factor
            total_run = adjusted_run

        lot_info[lot_id] = {
            "release_ts_hours": ts_to_h(lot_data[lot_id]["release_ts"]),
            "due_ts_hours": ts_to_h(lot_data[lot_id]["due_ts"]),
            "total_remaining_run_time": total_run,
        }

    # --- state trackers ---
    tool_available: dict[str, float] = defaultdict(float)   # tool_id → next free time
    lot_ready: dict[str, float] = {}                         # lot_id → when last op finished
    for lot_id in lot_ops:
        lot_ready[lot_id] = lot_info[lot_id]["release_ts_hours"]

    # For extra_tool: create a virtual second tool
    extra_tool_id = None
    if extra_tool:
        extra_tool_id = f"{extra_tool}_EXTRA"
        tool_available[extra_tool_id] = 0.0

    # Track which operation index each lot is on
    next_op_idx: dict[str, int] = {lot_id: 0 for lot_id in lot_ops}

    # --- event log ---
    events: list[dict] = []
    event_counter = 0

    # --- simulation loop ---
    total_ops = sum(len(ops) for ops in lot_ops.values())
    completed = 0
    max_iterations = total_ops * 10  # safety limit

    for _ in range(max_iterations):
        if completed >= total_ops:
            break

        # Step A: For each tool, collect ready operations
        tool_queues: dict[str, list[dict]] = defaultdict(list)

        for lot_id, ops in lot_ops.items():
            idx = next_op_idx[lot_id]
            if idx >= len(ops):
                continue  # lot done

            op = ops[idx]
            tool_id = op["tool_id"]

            # Check if lot is ready (previous op done)
            if lot_ready[lot_id] is None:
                continue
            op_ready_time = max(lot_ready[lot_id], 0)

            # Apply bottleneck speedup to this op's run_time
            run_time = op["run_time"]
            if bottleneck_speedup and tool_id in bottleneck_speedup:
                run_time *= bottleneck_speedup[tool_id]

            # Build queue entry for the tool
            tool_queues[tool_id].append({
                "lot_id": lot_id,
                "tool_id": tool_id,
                "operation_id": f"{lot_id}_OP{op['operation_seq']:03d}",
                "operation_seq": op["operation_seq"],
                "instance_id": op["instance_id"],
                "run_time": run_time,
                "queue_start_time": op_ready_time,
                "lot_ready_time": lot_ready[lot_id],
            })

            # Also consider extra tool
            if extra_tool_id and tool_id == extra_tool:
                tool_queues[extra_tool_id].append({
                    "lot_id": lot_id,
                    "tool_id": extra_tool_id,
                    "operation_id": f"{lot_id}_OP{op['operation_seq']:03d}",
                    "operation_seq": op["operation_seq"],
                    "instance_id": op["instance_id"],
                    "run_time": run_time,
                    "queue_start_time": op_ready_time,
                    "lot_ready_time": lot_ready[lot_id],
                })

        # Step B: For each tool with a queue and available, dispatch one operation
        dispatched_any = False
        dispatched_lots: set[str] = set()

        # Sort tools by availability so earlier-free tools dispatch first
        sorted_tools = sorted(tool_queues.keys(), key=lambda t: tool_available.get(t, 0.0))

        for tool_id in sorted_tools:
            queue = tool_queues[tool_id]
            # Filter: only ops whose lot hasn't been dispatched yet this round
            queue = [op for op in queue if op["lot_id"] not in dispatched_lots]

            if not queue:
                continue

            # Apply dispatching rule
            rule_fn = RULES.get(rule_name, RULES["FIFO"])
            try:
                selected = rule_fn(queue, max(tool_available.get(tool_id, 0.0), 0.0), lot_info)
            except Exception:
                selected = queue[0]  # fallback

            if selected is None:
                continue

            lot_id = selected["lot_id"]

            # Calculate times
            start_time = max(selected["lot_ready_time"], tool_available.get(tool_id, 0.0))
            end_time = start_time + selected["run_time"]
            queue_time = start_time - selected["queue_start_time"]
            if queue_time < 0:
                queue_time = 0.0

            # Record event
            event_counter += 1
            events.append({
                "scenario_id": scenario_id,
                "rule_name": rule_name,
                "event_id": f"EVT{event_counter:06d}",
                "lot_id": lot_id,
                "operation_id": selected["operation_id"],
                "operation_seq": selected["operation_seq"],
                "tool_id": selected["tool_id"],
                "queue_start_time": round(selected["queue_start_time"], 4),
                "start_time": round(start_time, 4),
                "end_time": round(end_time, 4),
                "queue_time": round(queue_time, 4),
                "run_time": round(selected["run_time"], 4),
            })

            # Update state
            tool_available[tool_id] = end_time
            lot_ready[lot_id] = end_time
            next_op_idx[lot_id] += 1
            dispatched_lots.add(lot_id)
            dispatched_any = True
            completed += 1

            # Update lot_info remaining run time
            lot_info[lot_id]["total_remaining_run_time"] -= selected["run_time"]
            if lot_info[lot_id]["total_remaining_run_time"] < 0:
                lot_info[lot_id]["total_remaining_run_time"] = 0.0

        # Step C: If nothing dispatched, advance time to the next tool-free event
        if not dispatched_any:
            # Find the minimum future available time across tools with waiting work
            next_time = float("inf")
            for lot_id, ops in lot_ops.items():
                idx = next_op_idx[lot_id]
                if idx >= len(ops):
                    continue
                candidate = max(lot_ready[lot_id], 0)
                if candidate < next_time:
                    next_time = candidate
            for t_id, t_avail in tool_available.items():
                if t_avail < next_time:
                    next_time = t_avail

            if next_time == float("inf") or next_time <= max(tool_available.values(), default=0):
                break  # deadlock or done

            # Advance: set all earlier tools to this time
            for t_id in list(tool_available.keys()):
                if tool_available[t_id] < next_time:
                    tool_available[t_id] = next_time

    # --- compute summary ---
    summary = _compute_summary(events, lot_data, rule_name, scenario_id, epoch_str)

    return events, summary


# ---------------------------------------------------------------------------
# KPI summary
# ---------------------------------------------------------------------------
def _compute_summary(
    events: list[dict],
    lot_data: dict,
    rule_name: str,
    scenario_id: str,
    epoch_str: str,
) -> dict:
    """Compute aggregate KPIs from the event log."""
    from datetime import datetime
    fmt = "%Y-%m-%d %H:%M:%S"

    if not events:
        return {"rule_name": rule_name, "scenario_id": scenario_id, "error": "no events"}

    # --- lot-level cycle time ---
    lot_events = defaultdict(list)
    for ev in events:
        lot_events[ev["lot_id"]].append(ev)

    lot_cycles = []
    for lot_id, evs in lot_events.items():
        release_h = (datetime.strptime(lot_data[lot_id]["release_ts"], fmt)
                     - datetime.strptime(epoch_str, fmt)).total_seconds() / 3600.0
        finish_h = max(ev["end_time"] for ev in evs)
        total_queue = sum(ev["queue_time"] for ev in evs)
        total_run = sum(ev["run_time"] for ev in evs)
        cycle_h = finish_h - release_h if finish_h > release_h else total_queue + total_run

        due_h = (datetime.strptime(lot_data[lot_id]["due_ts"], fmt)
                 - datetime.strptime(epoch_str, fmt)).total_seconds() / 3600.0
        on_time = 1 if finish_h <= due_h else 0
        lateness = max(0, finish_h - due_h)

        lot_cycles.append({
            "lot_id": lot_id,
            "cycle_time": cycle_h,
            "queue_time": total_queue,
            "run_time": total_run,
            "queue_ratio": total_queue / (total_queue + total_run) if (total_queue + total_run) > 0 else 0,
            "on_time": on_time,
            "lateness": lateness,
        })

    # --- tool-level utilization ---
    tool_usage = defaultdict(float)
    for ev in events:
        tool_usage[ev["tool_id"]] += ev["run_time"]

    # Total simulation span
    makespan = max(ev["end_time"] for ev in events)

    # Utilization = total busy time / (makespan * number of tools) — simplified per-tool
    unique_tools = set(ev["tool_id"] for ev in events)
    tool_utils = {}
    for tid in unique_tools:
        tool_utils[tid] = tool_usage[tid] / makespan if makespan > 0 else 0

    if tool_utils:
        bottleneck_tool = max(tool_utils, key=tool_utils.get)
        bottleneck_util = tool_utils[bottleneck_tool]
    else:
        bottleneck_tool = ""
        bottleneck_util = 0

    # --- composite bottleneck (utilisation 0.4 + queue 0.4 + WIP 0.2) ---
    tool_queue_sum = defaultdict(float)
    tool_wip_count = defaultdict(int)
    for ev in events:
        tool_queue_sum[ev["tool_id"]] += ev["queue_time"]
        tool_wip_count[ev["tool_id"]] += 1

    util_vals = [tool_utils[t] for t in unique_tools]
    queue_vals = [tool_queue_sum[t] / max(tool_wip_count[t], 1) for t in unique_tools]
    wip_vals = [tool_wip_count[t] for t in unique_tools]

    def _norm(vals):
        mn, mx = min(vals), max(vals)
        return [(v - mn) / (mx - mn) if mx > mn else 0.5 for v in vals]

    u_n, q_n, w_n = _norm(util_vals), _norm(queue_vals), _norm(wip_vals)
    tools_sorted = sorted(unique_tools)
    comp_scores = {}
    for i, t in enumerate(tools_sorted):
        comp_scores[t] = u_n[i] * 0.4 + q_n[i] * 0.4 + w_n[i] * 0.2
    composite_bn = max(comp_scores, key=comp_scores.get) if comp_scores else ""
    composite_bn_score = round(comp_scores.get(composite_bn, 0), 4)

    n = len(lot_cycles)
    cyc = [lc["cycle_time"] for lc in lot_cycles]
    cyc.sort()
    qtimes = [lc["queue_time"] for lc in lot_cycles]
    lates = [lc["lateness"] for lc in lot_cycles]

    avg_util = sum(tool_utils.values()) / len(tool_utils) if tool_utils else 0
    on_time_count = sum(lc["on_time"] for lc in lot_cycles)

    summary = {
        "scenario_id": scenario_id,
        "rule_name": rule_name,
        "rule_label": RULE_LABELS.get(rule_name, rule_name),
        "makespan": round(makespan, 2),
        "avg_cycle_time": round(sum(cyc) / n, 2) if n else 0,
        "median_cycle_time": round(cyc[n // 2], 2) if n else 0,
        "avg_queue_time": round(sum(qtimes) / n, 2) if n else 0,
        "queue_time_ratio": round(sum(lc["queue_ratio"] for lc in lot_cycles) / n * 100, 1) if n else 0,
        "max_lateness": round(max(lates), 2) if lates else 0,
        "on_time_rate": round(on_time_count / n * 100, 1) if n else 0,
        "avg_tool_utilization": round(avg_util * 100, 1),
        "bottleneck_tool": bottleneck_tool,
        "bottleneck_utilization": round(bottleneck_util * 100, 1),
        "composite_bottleneck_tool": composite_bn,
        "composite_bottleneck_score": composite_bn_score,
        "total_lots": n,
        "total_operations": len(events),
    }
    return summary


# ---------------------------------------------------------------------------
# Batch runner — compare multiple rules
# ---------------------------------------------------------------------------
def run_all_rules(
    operations: list[dict],
    lot_data: dict,
    rule_names: list[str] | None = None,
    scenario_id: str = "baseline",
    bottleneck_speedup: dict[str, float] | None = None,
    extra_tool: str | None = None,
) -> tuple[dict[str, list[dict]], list[dict]]:
    """Run simulation for multiple dispatching rules.

    Returns (all_events, summaries) where all_events[rule_name] = list of event dicts.
    """
    if rule_names is None:
        rule_names = ["FIFO", "SPT", "EDD", "CR"]

    all_events = {}
    summaries = []
    for rn in rule_names:
        events, summary = run_simulation(
            operations, lot_data,
            rule_name=rn,
            scenario_id=scenario_id,
            bottleneck_speedup=bottleneck_speedup,
            extra_tool=extra_tool,
        )
        all_events[rn] = events
        summaries.append(summary)
        print(f"  [{rn:6s}] makespan={summary['makespan']:8.2f}h  "
              f"avg_cycle={summary['avg_cycle_time']:7.2f}h  "
              f"on_time={summary['on_time_rate']:5.1f}%  "
              f"bottleneck={summary['bottleneck_tool']}")

    return all_events, summaries


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fab Capacity Simulation")
    parser.add_argument("--rules", nargs="+", default=["FIFO", "SPT", "EDD", "CR"],
                        help="Dispatching rules to run")
    parser.add_argument("--scenario", default="baseline",
                        help="Scenario ID label")
    parser.add_argument("--operations", default=None,
                        help="Path to operations.csv")
    parser.add_argument("--lots", default=None,
                        help="Path to dim_lot.csv")
    parser.add_argument("--output-events", default=None,
                        help="Output events CSV path")
    parser.add_argument("--output-summary", default=None,
                        help="Output summary CSV path")
    args = parser.parse_args()

    # Default paths
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ops_path = args.operations or os.path.join(base, "data", "processed", "operations.csv")
    lot_path = args.lots or os.path.join(base, "data", "processed", "dim_lot.csv")

    ops = _load_operations(ops_path)
    lots = _load_lot_data(lot_path)

    print(f"Loaded {len(ops)} operations, {len(lots)} lots")
    print(f"Running rules: {args.rules}\n")

    all_events, summaries = run_all_rules(ops, lots, args.rules, args.scenario)

    print("\n" + "=" * 70)
    print(f"{'Rule':<8} {'Makespan':>10} {'AvgCycle':>10} {'AvgQueue':>10} "
          f"{'OnTime%':>8} {'Util%':>7} {'Bottleneck':>12}")
    print("-" * 70)
    for s in summaries:
        print(f"{s['rule_name']:<8} {s['makespan']:>8.1f}h {s['avg_cycle_time']:>8.1f}h "
              f"{s['avg_queue_time']:>8.1f}h {s['on_time_rate']:>7.1f}% "
              f"{s['avg_tool_utilization']:>6.1f}% {s['bottleneck_tool']:>12}")

    # Write outputs if requested
    if args.output_events:
        _write_events_csv(all_events, args.output_events)
    if args.output_summary:
        _write_summary_csv(summaries, args.output_summary)


def _write_events_csv(all_events: dict[str, list[dict]], path: str):
    """Write combined event log for all rules."""
    flat = []
    for rule, evs in all_events.items():
        flat.extend(evs)
    if not flat:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=flat[0].keys())
        w.writeheader()
        w.writerows(flat)


def _write_summary_csv(summaries: list[dict], path: str):
    """Write scenario summary CSV."""
    if not summaries:
        return
    # flatten dict
    fieldnames = list(summaries[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(summaries)


if __name__ == "__main__":
    main()
