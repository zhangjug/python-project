"""Run full simulation suite + generate all charts."""
import sys, os, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from simulator import run_all_rules, _load_operations, _load_lot_data
from metrics import (
    print_comparison, scenario_improvement, print_improvements,
    bottleneck_ranking_from_events
)
from visualization import generate_all_charts

PROJECT = os.path.dirname(__file__)
ops = _load_operations(os.path.join(PROJECT, "data", "processed", "operations.csv"))
lots = _load_lot_data(os.path.join(PROJECT, "data", "processed", "dim_lot.csv"))

RULES = ["FIFO", "SPT", "EDD", "CR"]

# --- Baseline ---
print("=" * 60)
print("BASELINE")
print("=" * 60)
base_ev, base_sum = run_all_rules(ops, lots, RULES, "baseline")
print_comparison(base_sum)

# --- Bottleneck ---
ranking = bottleneck_ranking_from_events(base_ev["FIFO"])
bn_composite = ranking[0]["entity"]
bn_util = base_sum[0].get("bottleneck_tool", "?")
print(f"\n>>> Composite Bottleneck: {bn_composite}  |  Highest-Utilisation Tool: {bn_util}")

# --- Capacity Scenarios ---
all_summaries = list(base_sum)
all_improvements = []

for sc_id, speedup, extra in [
    ("Bottleneck +10% Capacity", {bn_composite: 0.9}, None),
    ("Bottleneck +20% Capacity", {bn_composite: 0.8}, None),
    ("Extra Parallel Tool", None, bn_composite),
]:
    print(f"\n{'='*60}")
    print(sc_id.upper())
    print("=" * 60)
    ev, su = run_all_rules(ops, lots, RULES, sc_id.replace(" ", "_").lower(),
                           bottleneck_speedup=speedup, extra_tool=extra)
    print_comparison(su)
    all_summaries.extend(su)
    all_improvements.extend(scenario_improvement(base_sum, su, sc_id))

# --- Improvement Summary ---
print(f"\n{'='*60}")
print("IMPROVEMENT SUMMARY")
print("=" * 60)
print_improvements(all_improvements)

# --- Save scenario_summary.csv ---
path = os.path.join(PROJECT, "data", "processed", "scenario_summary.csv")
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=all_summaries[0].keys())
    w.writeheader()
    w.writerows(all_summaries)
print(f"\nSaved: {path} ({len(all_summaries)} rows)")

# --- Save simulation_events.csv & simulation_summary.csv (baseline) ---
flat_events = []
for ev_list in base_ev.values():
    flat_events.extend(ev_list)

events_path = os.path.join(PROJECT, "data", "processed", "simulation_events.csv")
with open(events_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=flat_events[0].keys())
    w.writeheader()
    w.writerows(flat_events)
print(f"Saved: {events_path} ({len(flat_events)} rows)")

summary_path = os.path.join(PROJECT, "data", "processed", "simulation_summary.csv")
with open(summary_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=base_sum[0].keys())
    w.writeheader()
    w.writerows(base_sum)
print(f"Saved: {summary_path} ({len(base_sum)} rows)")

# --- Charts ---
all_ev = flat_events

print("\nGenerating charts...")
generate_all_charts(all_ev, base_sum, ranking=ranking, improvements=all_improvements)
print("All done!")
