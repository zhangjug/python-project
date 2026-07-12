"""
metrics.py — Compute and compare manufacturing KPIs across simulation scenarios.

Produces:
  - Per-scenario summary table (rule comparison)
  - Capacity scenario improvement analysis
  - Bottleneck ranking across scenarios
"""

import csv
import os
from collections import defaultdict


# ---------------------------------------------------------------------------
# Rule comparison table
# ---------------------------------------------------------------------------
def rule_comparison_table(summaries: list[dict]) -> list[dict]:
    """Return a list of dicts suitable for a comparison table.

    Each dict: rule_name, makespan, avg_cycle_time, avg_queue_time,
               queue_time_ratio, on_time_rate, avg_tool_utilization,
               bottleneck_tool, bottleneck_utilization
    """
    return sorted(summaries, key=lambda s: s["makespan"])


def print_comparison(summaries: list[dict]):
    """Pretty-print the rule comparison table."""
    header = (f"{'Rule':<8} {'Makespan':>10} {'AvgCycle':>10} {'AvgQueue':>10} "
              f"{'Q%':>6} {'OnTime%':>8} {'Util%':>7} {'BN_Tool':>10} {'BN_Util%':>9}")
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for s in sorted(summaries, key=lambda x: x["makespan"]):
        print(f"{s['rule_name']:<8} {s['makespan']:>8.1f}h {s['avg_cycle_time']:>8.1f}h "
              f"{s['avg_queue_time']:>8.1f}h {s['queue_time_ratio']:>5.1f}% "
              f"{s['on_time_rate']:>7.1f}% {s['avg_tool_utilization']:>6.1f}% "
              f"{s['bottleneck_tool']:>10} {s['bottleneck_utilization']:>8.1f}%")
    print(sep)


# ---------------------------------------------------------------------------
# Scenario improvement analysis
# ---------------------------------------------------------------------------
def scenario_improvement(
    baseline_summaries: list[dict],
    scenario_summaries: list[dict],
    scenario_label: str,
) -> list[dict]:
    """Compare a capacity scenario against baseline, per rule.

    Returns list of dicts with improvement percentages.
    """
    baseline_by_rule = {s["rule_name"]: s for s in baseline_summaries}
    improvements = []

    for sc in scenario_summaries:
        base = baseline_by_rule.get(sc["rule_name"])
        if base is None:
            continue
        improvements.append({
            "scenario": scenario_label,
            "rule_name": sc["rule_name"],
            "makespan_change_pct": _pct_change(base["makespan"], sc["makespan"]),
            "avg_cycle_change_pct": _pct_change(base["avg_cycle_time"], sc["avg_cycle_time"]),
            "avg_queue_change_pct": _pct_change(base["avg_queue_time"], sc["avg_queue_time"]),
            "on_time_change_pp": round(sc["on_time_rate"] - base["on_time_rate"], 1),
            "utilization_change_pp": round(sc["avg_tool_utilization"] - base["avg_tool_utilization"], 1),
        })

    return improvements


def _pct_change(old: float, new: float) -> float:
    """Percentage change (negative = improvement for time metrics)."""
    if old == 0:
        return 0.0
    return round((new - old) / old * 100, 1)


def print_improvements(improvements: list[dict]):
    """Pretty-print scenario improvements."""
    print(f"\n{'Scenario Improvement':—^70}")
    header = (f"{'Scenario':<20} {'Rule':<8} {'Makespan%':>10} {'Cycle%':>8} "
              f"{'Queue%':>8} {'OnTimeΔ':>8} {'UtilΔ':>7}")
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for imp in improvements:
        print(f"{imp['scenario']:<20} {imp['rule_name']:<8} "
              f"{imp['makespan_change_pct']:>9.1f}% {imp['avg_cycle_change_pct']:>7.1f}% "
              f"{imp['avg_queue_change_pct']:>7.1f}% {imp['on_time_change_pp']:>7.1f}pp "
              f"{imp['utilization_change_pp']:>6.1f}pp")
    print(sep)


# ---------------------------------------------------------------------------
# Bottleneck analysis from events
# ---------------------------------------------------------------------------
def bottleneck_ranking_from_events(
    events: list[dict],
    tool_groups: dict[str, str] | None = None,
) -> list[dict]:
    """Rank tools by utilization, queue time, and WIP.

    If tool_groups is provided (tool_id → tool_group), aggregates by group.
    """
    tool_util = defaultdict(float)
    tool_queue = defaultdict(list)
    tool_wip = defaultdict(int)

    for ev in events:
        tid = ev["tool_id"]
        tool_util[tid] += ev["run_time"]
        tool_queue[tid].append(ev["queue_time"])
        tool_wip[tid] += 1

    # Compute makespan
    if events:
        makespan = max(ev["end_time"] for ev in events)
    else:
        makespan = 1.0

    # Aggregate by group if mapping provided
    if tool_groups:
        group_util = defaultdict(float)
        group_queue = defaultdict(list)
        group_wip = defaultdict(int)
        for tid in tool_util:
            g = tool_groups.get(tid, tid)
            group_util[g] += tool_util[tid]
            group_queue[g].extend(tool_queue[tid])
            group_wip[g] += tool_wip[tid]
        keys = list(group_util.keys())
        util_map = {k: group_util[k] / makespan for k in keys}
        queue_map = {k: sum(group_queue[k]) / len(group_queue[k]) if group_queue[k] else 0 for k in keys}
        wip_map = {k: group_wip[k] for k in keys}
    else:
        keys = list(tool_util.keys())
        util_map = {k: tool_util[k] / makespan for k in keys}
        queue_map = {k: sum(tool_queue[k]) / len(tool_queue[k]) if tool_queue[k] else 0 for k in keys}
        wip_map = {k: tool_wip[k] for k in keys}

    # Normalize and score
    def _norm(vals):
        mn, mx = min(vals), max(vals)
        if mx == mn:
            return [0.5] * len(vals)
        return [(v - mn) / (mx - mn) for v in vals]

    util_vals = [util_map[k] for k in keys]
    queue_vals = [queue_map[k] for k in keys]
    wip_vals = [wip_map[k] for k in keys]

    u_norm = _norm(util_vals)
    q_norm = _norm(queue_vals)
    w_norm = _norm(wip_vals)

    ranking = []
    for i, k in enumerate(keys):
        score = u_norm[i] * 0.4 + q_norm[i] * 0.4 + w_norm[i] * 0.2
        ranking.append({
            "entity": k,
            "utilization_pct": round(util_map[k] * 100, 1),
            "avg_queue_hours": round(queue_map[k], 2),
            "total_wip": wip_map[k],
            "bottleneck_score": round(score, 4),
        })

    ranking.sort(key=lambda x: x["bottleneck_score"], reverse=True)
    for i, r in enumerate(ranking):
        r["rank"] = i + 1

    return ranking


# ---------------------------------------------------------------------------
# Capacity gap analysis (for LP-like thinking)
# ---------------------------------------------------------------------------
def capacity_gap_analysis(
    events: list[dict],
    capacity_hours_per_tool: dict[str, float],
    target_util: float = 0.85,
) -> list[dict]:
    """Identify tools where demand exceeds target-util-adjusted capacity.

    Returns list of gaps sorted by severity.
    """
    tool_demand = defaultdict(float)
    for ev in events:
        tool_demand[ev["tool_id"]] += ev["run_time"]

    gaps = []
    for tid, demand in tool_demand.items():
        capacity = capacity_hours_per_tool.get(tid, demand / target_util if target_util > 0 else demand)
        target_capacity = demand / target_util if target_util > 0 else demand
        gap = max(0, target_capacity - capacity)
        gaps.append({
            "tool_id": tid,
            "demand_hours": round(demand, 2),
            "capacity_hours": round(capacity, 2),
            "target_capacity_at_85": round(target_capacity, 2),
            "capacity_gap_hours": round(gap, 2),
            "current_util_pct": round(demand / capacity * 100, 1) if capacity > 0 else 0,
        })

    gaps.sort(key=lambda x: x["capacity_gap_hours"], reverse=True)
    return gaps


# ---------------------------------------------------------------------------
# Write summary CSV
# ---------------------------------------------------------------------------
def write_summary_csv(summaries: list[dict], path: str):
    """Write scenario_summary.csv."""
    if not summaries:
        return
    fieldnames = [
        "scenario_id", "rule_name", "rule_label",
        "makespan", "avg_cycle_time", "median_cycle_time",
        "avg_queue_time", "queue_time_ratio", "max_lateness",
        "on_time_rate", "avg_tool_utilization",
        "bottleneck_tool", "bottleneck_utilization",
        "total_lots", "total_operations",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(summaries)
    print(f"[wrote] {path}")


def main():
    """Standalone: load events CSV and print comparisons."""
    import argparse

    ap = argparse.ArgumentParser(description="Compute metrics from simulation events")
    ap.add_argument("--events", required=True, help="Path to combined events CSV")
    ap.add_argument("--summary-out", default=None, help="Path to write summary CSV")
    args = ap.parse_args()

    # Load events, group by scenario+rule
    groups = defaultdict(list)
    with open(args.events, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row.get("scenario_id", ""), row.get("rule_name", ""))
            groups[key].append(row)

    # This is a lightweight standalone; full summary needs lot_data too.
    print(f"Loaded {sum(len(v) for v in groups.values())} events across {len(groups)} scenarios×rules")


if __name__ == "__main__":
    main()
