"""
visualization.py — Generate charts for the fab capacity simulation project.

Produces:
  1. Gantt chart — lot flow across tools over time
  2. Rule comparison bar chart — makespan, cycle time, on-time rate
  3. Tool utilization heatmap — tool load by tool
  4. Bottleneck ranking — tools sorted by bottleneck score
  5. Queue time distribution — histogram
  6. Capacity scenario improvement waterfall (optional)

Requires: matplotlib
"""

import os
import sys
from collections import defaultdict

# Allow importing from sibling src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "figures")


def _ensure_figures_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Gantt chart
# ---------------------------------------------------------------------------
def plot_gantt(
    events: list[dict],
    rule_name: str = "FIFO",
    max_lots: int = 15,
    save: bool = True,
):
    """Plot a Gantt chart showing lot flow across tools.

    Each horizontal bar = one operation on a tool.
    Y-axis = tool_id; colour = lot_id.
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    _ensure_figures_dir()

    # Filter to selected rule and top lots
    evs = [e for e in events if e.get("rule_name", "") == rule_name]
    lot_ids = sorted(set(e["lot_id"] for e in evs))[:max_lots]
    evs = [e for e in evs if e["lot_id"] in lot_ids]

    if not evs:
        print(f"[gantt] No events for rule={rule_name}")
        return

    tools = sorted(set(e["tool_id"] for e in evs))
    tool_to_y = {t: i for i, t in enumerate(tools)}

    # Colour map per lot
    cmap = plt.get_cmap("tab20", len(lot_ids))
    lot_colors = {lid: cmap(i) for i, lid in enumerate(lot_ids)}

    fig, ax = plt.subplots(figsize=(16, max(6, len(tools) * 0.5)))

    labeled = set()
    for ev in evs:
        y = tool_to_y[ev["tool_id"]]
        start = ev["start_time"]
        duration = ev["run_time"]
        color = lot_colors[ev["lot_id"]]
        lbl = ev["lot_id"] if ev["lot_id"] not in labeled else None
        if lbl:
            labeled.add(lbl)
        ax.barh(y, duration, left=start, height=0.7,
                color=color, edgecolor="white", linewidth=0.3,
                label=lbl)

    ax.set_yticks(range(len(tools)))
    ax.set_yticklabels(tools)
    ax.set_xlabel("Time (hours from epoch)")
    ax.set_ylabel("Tool")
    ax.set_title(f"Gantt Chart — {rule_name} Dispatching (top {len(lot_ids)} lots)")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    # Deduplicated legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(),
              loc="upper right", fontsize=7, ncol=2, title="Lot")

    fig.tight_layout()
    if save:
        path = os.path.join(FIGURES_DIR, f"gantt_{rule_name.lower()}.png")
        fig.savefig(path, dpi=150)
        print(f"[saved] {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Rule comparison bar chart
# ---------------------------------------------------------------------------
def plot_rule_comparison(summaries: list[dict], save: bool = True):
    """Grouped bar chart comparing makespan, avg_cycle_time, on_time_rate across rules."""
    import matplotlib.pyplot as plt
    import numpy as np

    _ensure_figures_dir()

    if not summaries:
        return

    rules = [s["rule_name"] for s in summaries]
    makespan = [s["makespan"] for s in summaries]
    avg_cycle = [s["avg_cycle_time"] for s in summaries]
    avg_queue = [s["avg_queue_time"] for s in summaries]
    on_time = [s["on_time_rate"] for s in summaries]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000"]

    # --- Panel A: makespan ---
    bars = axes[0].bar(rules, makespan, color=colors[:len(rules)], edgecolor="white")
    axes[0].set_title("Makespan (hours)")
    axes[0].set_ylabel("Hours")
    for bar, val in zip(bars, makespan):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     f"{val:.1f}", ha="center", fontsize=9)

    # --- Panel B: cycle time ---
    x = np.arange(len(rules))
    w = 0.35
    axes[1].bar(x - w / 2, avg_cycle, w, label="Avg Cycle Time", color="#4472C4", edgecolor="white")
    axes[1].bar(x + w / 2, avg_queue, w, label="Avg Queue Time", color="#ED7D31", edgecolor="white")
    axes[1].set_title("Cycle Time vs Queue Time (hours)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(rules)
    axes[1].legend(fontsize=8)

    # --- Panel C: on-time rate ---
    bars = axes[2].bar(rules, on_time, color=colors[:len(rules)], edgecolor="white")
    axes[2].set_title("On-Time Rate (%)")
    axes[2].set_ylabel("%")
    axes[2].set_ylim(0, 105)
    for bar, val in zip(bars, on_time):
        axes[2].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f"{val:.1f}%", ha="center", fontsize=9)

    fig.suptitle("Dispatching Rule Comparison", fontsize=14, fontweight="bold")
    fig.tight_layout()

    if save:
        path = os.path.join(FIGURES_DIR, "rule_comparison.png")
        fig.savefig(path, dpi=150)
        print(f"[saved] {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Tool utilization heatmap
# ---------------------------------------------------------------------------
def plot_utilization_heatmap(events: list[dict], rule_name: str = "FIFO", save: bool = True):
    """Heatmap showing utilization per tool."""
    import matplotlib.pyplot as plt
    import numpy as np

    _ensure_figures_dir()

    evs = [e for e in events if e.get("rule_name", "") == rule_name]
    if not evs:
        return

    tools = sorted(set(e["tool_id"] for e in evs))

    # Compute per-tool utilization
    makespan = max(e["end_time"] for e in evs)
    tool_busy = defaultdict(float)
    for ev in evs:
        tool_busy[ev["tool_id"]] += ev["run_time"]

    utils = [tool_busy[t] / makespan * 100 if makespan > 0 else 0 for t in tools]

    fig, ax = plt.subplots(figsize=(max(8, len(tools) * 0.8), 3))

    # Reshape to 1-row heatmap
    data = np.array(utils).reshape(1, -1)
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=max(100, max(utils)))

    ax.set_xticks(range(len(tools)))
    ax.set_xticklabels(tools)
    ax.set_yticks([])
    ax.set_title(f"Tool Utilization Heatmap — {rule_name}")

    # Add text annotations
    for i, u in enumerate(utils):
        ax.text(i, 0, f"{u:.1f}%", ha="center", va="center",
                fontsize=9, color="white" if u > 60 else "black")

    fig.colorbar(im, ax=ax, label="Utilization %", shrink=0.6)
    fig.tight_layout()

    if save:
        path = os.path.join(FIGURES_DIR, f"utilization_heatmap_{rule_name.lower()}.png")
        fig.savefig(path, dpi=150)
        print(f"[saved] {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Bottleneck ranking chart
# ---------------------------------------------------------------------------
def plot_bottleneck_ranking(ranking: list[dict], title_suffix: str = "", save: bool = True):
    """Horizontal bar chart ranking tools by bottleneck score."""
    import matplotlib.pyplot as plt

    _ensure_figures_dir()

    if not ranking:
        return

    entities = [r["entity"] for r in ranking[:10]]
    scores = [r["bottleneck_score"] for r in ranking[:10]]
    utils = [r["utilization_pct"] for r in ranking[:10]]

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.barh(entities, scores, color=plt.colormaps["Reds"]([s / max(scores) for s in scores]),
                   edgecolor="white")
    ax.set_xlabel("Bottleneck Score")
    ax.set_title(f"Bottleneck Ranking{title_suffix}")
    ax.invert_yaxis()

    # Add utilization labels
    for bar, u in zip(bars, utils):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"util: {u:.0f}%", va="center", fontsize=8)

    fig.tight_layout()
    if save:
        path = os.path.join(FIGURES_DIR, "bottleneck_ranking.png")
        fig.savefig(path, dpi=150)
        print(f"[saved] {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Queue time distribution
# ---------------------------------------------------------------------------
def plot_queue_distribution(events: list[dict], rule_name: str = "FIFO", save: bool = True):
    """Histogram of queue times."""
    import matplotlib.pyplot as plt

    _ensure_figures_dir()

    evs = [e for e in events if e.get("rule_name", "") == rule_name]
    if not evs:
        return

    queue_times = [e["queue_time"] for e in evs if e.get("queue_time", 0) > 0]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(queue_times, bins=40, color="#4472C4", edgecolor="white", alpha=0.85)
    ax.axvline(x=sum(queue_times) / len(queue_times) if queue_times else 0,
               color="red", linestyle="--", linewidth=2,
               label=f"Mean: {sum(queue_times)/len(queue_times):.1f}h" if queue_times else "N/A")
    ax.set_xlabel("Queue Time (hours)")
    ax.set_ylabel("Operation Count")
    ax.set_title(f"Queue Time Distribution — {rule_name}")
    ax.legend()

    fig.tight_layout()
    if save:
        path = os.path.join(FIGURES_DIR, f"queue_distribution_{rule_name.lower()}.png")
        fig.savefig(path, dpi=150)
        print(f"[saved] {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Scenario improvement waterfall (optional)
# ---------------------------------------------------------------------------
def plot_improvement_waterfall(
    improvements: list[dict],
    save: bool = True,
):
    """Waterfall chart showing improvement across capacity scenarios."""
    import matplotlib.pyplot as plt
    import numpy as np

    _ensure_figures_dir()

    if not improvements:
        return

    # Group by scenario, average across rules
    scenarios = sorted(set(imp["scenario"] for imp in improvements))
    avg_makespan = []
    for sc in scenarios:
        vals = [imp["makespan_change_pct"] for imp in improvements if imp["scenario"] == sc]
        avg_makespan.append(sum(vals) / len(vals) if vals else 0)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4472C4" if v <= 0 else "#ED7D31" for v in avg_makespan]
    bars = ax.bar(scenarios, avg_makespan, color=colors, edgecolor="white")
    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.set_ylabel("Makespan Change (%)")
    ax.set_title("Capacity Scenario — Makespan Improvement")

    for bar, val in zip(bars, avg_makespan):
        y_pos = bar.get_height() - 0.5 if val < 0 else bar.get_height() + 0.3
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f"{val:+.1f}%", ha="center", fontsize=9)

    fig.tight_layout()
    if save:
        path = os.path.join(FIGURES_DIR, "scenario_improvement_waterfall.png")
        fig.savefig(path, dpi=150)
        print(f"[saved] {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Generate all charts
# ---------------------------------------------------------------------------
def generate_all_charts(
    events: list[dict],
    summaries: list[dict],
    ranking: list[dict] | None = None,
    improvements: list[dict] | None = None,
    events_by_rule: dict[str, list[dict]] | None = None,
):
    """Convenience function — generate all available chart types.

    Generates FIFO charts by default, plus CR charts when events_by_rule is provided.
    """
    rule_names = sorted(set(s.get("rule_name", "FIFO") for s in summaries))
    primary_rule = "FIFO" if "FIFO" in rule_names else rule_names[0]
    extra_rules = [r for r in ["CR"] if r in rule_names and r != primary_rule]

    print("Generating charts...")
    _ensure_figures_dir()

    # 1. Gantt (FIFO baseline + extra rules)
    plot_gantt(events, rule_name=primary_rule)
    for r in extra_rules:
        if events_by_rule and r in events_by_rule:
            plot_gantt(events_by_rule[r], rule_name=r)

    # 2. Rule comparison
    plot_rule_comparison(summaries)

    # 3. Utilisation heatmap (FIFO + extra rules)
    plot_utilization_heatmap(events, rule_name=primary_rule)
    for r in extra_rules:
        if events_by_rule and r in events_by_rule:
            plot_utilization_heatmap(events_by_rule[r], rule_name=r)

    # 4. Bottleneck ranking
    if ranking:
        plot_bottleneck_ranking(ranking)
    else:
        from metrics import bottleneck_ranking_from_events
        fifo_events = [e for e in events if e.get("rule_name", "") == primary_rule]
        br = bottleneck_ranking_from_events(fifo_events)
        plot_bottleneck_ranking(br)

    # 5. Queue distribution (FIFO + extra rules)
    plot_queue_distribution(events, rule_name=primary_rule)
    for r in extra_rules:
        if events_by_rule and r in events_by_rule:
            plot_queue_distribution(events_by_rule[r], rule_name=r)

    # 6. Scenario improvement
    if improvements:
        plot_improvement_waterfall(improvements)

    print("Done — figures saved to outputs/figures/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Generate simulation charts")
    ap.add_argument("--events", default=None, help="Path to events CSV")
    ap.add_argument("--summary", default=None, help="Path to summary CSV")
    ap.add_argument("--rule", default="FIFO", help="Rule for Gantt/heatmap")
    args = ap.parse_args()

    if not args.events:
        print("No events file provided; nothing to plot.")
        return

    # Simple CLI: just Gantt and heatmap
    import csv
    events = []
    with open(args.events, newline="", encoding="utf-8") as f:
        events = list(csv.DictReader(f))

    plot_gantt(events, rule_name=args.rule)
    plot_utilization_heatmap(events, rule_name=args.rule)
    plot_queue_distribution(events, rule_name=args.rule)


if __name__ == "__main__":
    main()
