"""
parser.py — Parse raw JSP benchmark instances into operation-level CSV.

Input:  data/raw/abz5 ~ abz9
Output: data/processed/operations.csv

JSP data format:
    Line 1: <num_jobs> <num_machines>
    Lines 2+: Each line = one job's route: <machine_id> <proc_time> <machine_id> <proc_time> ...

Fab-like mapping:
    job → lot
    machine → tool
    processing time → run_time (hours; raw values treated as minutes)
"""

import csv
import os
from collections import defaultdict

# ---------- config ----------
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
INSTANCES = ["abz5", "abz6", "abz7", "abz8", "abz9"]


def read_instance(instance_id: str) -> tuple:
    """Return (num_jobs, num_machines, routes).

    routes[job_idx] = [(machine_id, run_time_minutes), ...]
    """
    path = os.path.join(RAW_DIR, instance_id)
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]

    header = lines[0].split()
    num_jobs = int(header[0])
    num_machines = int(header[1])

    routes = []
    for line in lines[1:]:
        tokens = list(map(int, line.split()))
        ops = [(tokens[i], tokens[i + 1]) for i in range(0, len(tokens), 2)]
        routes.append(ops)

    return num_jobs, num_machines, routes


def parse_all_instances() -> list[dict]:
    """Parse all instances into a unified operation-level list.

    Returns a list of dicts with keys:
        instance_id, lot_id, operation_seq, tool_id, run_time
    """
    rows = []
    lot_counter = 0

    for instance_id in INSTANCES:
        num_jobs, num_machines, routes = read_instance(instance_id)
        print(f"[parsed] {instance_id}: {num_jobs} lots × {num_machines} tools")

        for job_idx, op_list in enumerate(routes):
            lot_counter += 1
            lot_id = f"L{lot_counter:04d}"
            for op_seq, (machine_id, run_time_min) in enumerate(op_list, start=1):
                rows.append({
                    "instance_id": instance_id,
                    "lot_id": lot_id,
                    "operation_seq": op_seq,
                    "tool_id": f"T{machine_id:02d}",
                    "run_time": round(run_time_min / 60.0, 4),  # minutes → hours
                })

    return rows


def build_instance_summary(rows: list[dict]) -> list[dict]:
    """Summarise each instance: lots, tools, operations."""
    groups = defaultdict(lambda: {"lots": set(), "tools": set(), "ops": 0})
    for r in rows:
        groups[r["instance_id"]]["lots"].add(r["lot_id"])
        groups[r["instance_id"]]["tools"].add(r["tool_id"])
        groups[r["instance_id"]]["ops"] += 1

    summary = []
    for inst in INSTANCES:
        g = groups[inst]
        summary.append({
            "instance_id": inst,
            "num_lots": len(g["lots"]),
            "num_tools": len(g["tools"]),
            "num_operations": g["ops"],
        })
    return summary


def write_operations_csv(rows: list[dict]):
    """Write operations.csv to data/processed/."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, "operations.csv")
    fieldnames = ["instance_id", "lot_id", "operation_seq", "tool_id", "run_time"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[wrote] {path}  ({len(rows)} rows)")


def main():
    print("=" * 60)
    print("Parsing benchmark instances...")
    rows = parse_all_instances()

    print("\nInstance summary:")
    for s in build_instance_summary(rows):
        print(f"  {s['instance_id']}: {s['num_lots']} lots, "
              f"{s['num_tools']} tools, {s['num_operations']} ops")

    print("\nWriting operations.csv...")
    write_operations_csv(rows)

    print(f"\nTotal: {len(rows)} operations across {len(INSTANCES)} instances")


if __name__ == "__main__":
    main()
