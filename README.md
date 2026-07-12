# Fab Capacity Simulation & Dispatching Optimization

> A Python-based fab capacity simulation model using public job-shop scheduling benchmark data. Compares FIFO, SPT, EDD, and Critical Ratio dispatching rules, evaluates makespan, cycle time, queue time, tool utilization, and on-time rate, and conducts bottleneck capacity scenario analysis.

## 1. Business Background

This project simulates a fab-like production system where wafer lots follow fixed process routes across multiple tools. The goal is to compare dispatching rules and capacity scenarios to reduce cycle time, improve on-time delivery, and identify bottleneck tools.

**Business assumptions:**

1. Each lot must follow a fixed route (sequence of operations).
2. Each operation can only be processed on its designated tool.
3. Each tool processes one operation at a time.
4. Lots may wait in queue before a tool, accumulating queue time.
5. No equipment failures, rework, batching, or other complex fab rules (see Limitations).

## 2. Data Source

- **Benchmark Repository**: [Job Shop Scheduling Benchmark: Environments and Instances](https://github.com/ai-for-decision-making-tue/Job_Shop_Scheduling_Benchmark_Environments_and_Instances)
- **Data Directory**: `data/raw/`
- **Paper Reference**: [Job Shop Scheduling Benchmark: Environments and Instances](https://arxiv.org/abs/2308.12794)
- **Instances Used**: `abz5`, `abz6`, `abz7`, `abz8`, `abz9`

| Instance | Jobs | Machines | Operations |
|----------|------|----------|------------|
| abz5     | 10   | 10       | 100        |
| abz6     | 10   | 10       | 100        |
| abz7     | 20   | 15       | 300        |
| abz8     | 20   | 15       | 300        |
| abz9     | 20   | 15       | 300        |

> This project builds a fab-like capacity simulation from public job-shop scheduling benchmark instances. It is not based on real fab MES data.

## 3. Fab-like Data Mapping

| Benchmark Concept | Fab-like Scenario  | Description                       |
|-------------------|--------------------|-----------------------------------|
| job               | lot / wafer lot    | A batch of wafers to be processed |
| operation         | process step       | One step in the wafer route       |
| machine           | tool               | Equipment capable of processing   |
| processing time   | run time           | Equipment processing duration     |
| operation sequence| route sequence     | Process route order               |
| dispatching rule  | lot dispatch policy| How to prioritise waiting lots    |
| makespan          | total completion time | All lots finished              |
| flow time         | cycle time         | Release to finish                 |

## 4. Project Structure

```
fab-capacity-simulation-python/
  README.md
  data/
    raw/                  # Original benchmark instances (abz5–abz9)
    processed/            # Parsed CSV data
      operations.csv
      dim_lot.csv
      dim_tool.csv
      fact_schedule_event_fifo_baseline.csv
      fact_capacity_calendar.csv
  src/
    parser.py             # Parse raw JSP data into operations.csv
    simulator.py          # Discrete-event simulation engine
    dispatch_rules.py     # FIFO, SPT, EDD, CR, LRPT dispatching rules
    metrics.py            # KPI calculation and comparison
    visualization.py      # Charts and figures
  notebooks/
    01_data_exploration.ipynb
    02_dispatching_simulation.ipynb
    03_capacity_scenario_analysis.ipynb
  outputs/figures/        # Generated charts
  docs/
    methodology.md
```

## 5. Getting Started

### Prerequisites

- Python 3.8+
- pip

```bash
pip install -r requirements.txt
```

### Step 1: Parse Benchmark Data

```bash
python src/parser.py
```

Reads raw instances from `data/raw/` and generates `data/processed/operations.csv`.

### Step 2: Run Full Pipeline

```bash
python run_all.py
```

Runs baseline simulation (4 rules), 3 capacity scenarios, generates all charts, and saves output CSV files.

### Reproducibility Check

Run the full pipeline:

```bash
python src/parser.py
python run_all.py
```

Expected outputs:

| File | Expected Rows |
|------|--------------:|
| `data/processed/operations.csv` | 1,100 |
| `data/processed/simulation_events.csv` | 4,400 |
| `data/processed/simulation_summary.csv` | 4 |
| `data/processed/scenario_summary.csv` | 16 |

Chart files in `outputs/figures/`:

- `gantt_fifo.png`
- `rule_comparison.png`
- `utilization_heatmap_fifo.png`
- `bottleneck_ranking.png`
- `queue_distribution_fifo.png`
- `scenario_improvement_waterfall.png`

### Step 3: Explore Notebooks

```bash
jupyter notebook notebooks/
```

- `01_data_exploration.ipynb` — Explore parsed data structure
- `02_dispatching_simulation.ipynb` — Run simulations, compare rules, generate charts
- `03_capacity_scenario_analysis.ipynb` — Bottleneck capacity scenarios

## 6. Dispatching Rules

| Rule | Logic | IE Interpretation |
|------|-------|-------------------|
| **FIFO** | First-in-first-out: earliest queue entry first | Stable, fair, easy to explain |
| **SPT** | Shortest processing time first | Reduces average flow time |
| **EDD** | Earliest due date first | Improves on-time delivery |
| **CR** | Critical Ratio = (due − now) / remaining work  | Prioritises at-risk lots |
| **LRPT** | Longest remaining processing time first | Optional: balances load |

## 7. Performance Metrics

| Metric | Description |
|--------|-------------|
| makespan | Total time to complete all lots |
| avg_cycle_time | Average lot cycle time (release → finish) |
| median_cycle_time | Median lot cycle time |
| avg_queue_time | Average waiting time per operation |
| queue_time_ratio | Queue time / total cycle time |
| max_lateness | Maximum lateness beyond due date |
| on_time_rate | % of lots completed on or before due date |
| avg_tool_utilization | Average tool utilisation |
| bottleneck_tool | Tool with highest bottleneck score |
| bottleneck_utilization | Utilisation of the bottleneck tool |

## 8. Capacity Scenarios

| Scenario | Description |
|----------|-------------|
| baseline | Original tool capacity |
| bottleneck +10% | Bottleneck tool processing time reduced by 10% |
| bottleneck +20% | Bottleneck tool processing time reduced by 20% |
| extra parallel tool | One additional identical tool at the bottleneck station |

## 9. Results and Findings

Analysis of 80 lots and 1,100 operations across 5 benchmark instances.

### Baseline Rule Comparison (FIFO simulation)

| Rule | Makespan | Avg Cycle Time | Avg Queue Time | Queue Ratio | On-Time Rate | Utilisation |
|------|----------|---------------|----------------|-------------|-------------|-------------|
| FIFO | 82.25 h | 54.89 h | 47.36 h | 85.9% | 100.0% | 48.8% |
| SPT | 118.02 h | 60.54 h | 53.02 h | 86.6% | 100.0% | 34.0% |
| EDD | 119.52 h | 66.78 h | 59.26 h | 87.5% | 100.0% | 33.6% |
| CR | 83.87 h | 62.98 h | 55.46 h | 87.8% | 100.0% | 47.8% |

### Key Findings

- **FIFO achieved the lowest makespan and average cycle time** in this benchmark configuration, outperforming SPT and EDD under the current synthetic release schedule and due-date assumptions.
- **CR produced a similar makespan to FIFO** (83.87 h vs 82.25 h) but with higher average cycle time — it is the best alternative when urgency-awareness is needed.
- **SPT and EDD did not outperform FIFO** on any metric for this specific instance set. This is expected in fixed-route job shops where purely local decisions can create downstream congestion.
- **All rules reached 100% on-time rate** because synthetic due dates (~14 days) are relatively loose compared to actual cycle times (~3–5 days). Future versions should tighten due-date assumptions to better evaluate EDD and CR.

### Bottleneck & Capacity

- **Composite bottleneck tool T07** ranked highest on the weighted score (utilisation 0.4 + queue time 0.4 + WIP 0.2).
- **Highest-utilisation tool T01** reached 60.5% utilisation under FIFO — less than typical real-fab bottlenecks but still the primary constraint in this dataset.
- Bottleneck capacity expansion reduces queue time more effectively than changing dispatching rules alone.
- Adding a parallel tool at the bottleneck station provided the largest improvement: **−9.4% cycle time, −10.9% queue time** for FIFO.

### Queue Time Dominance

- Waiting time contributed **85%+ of average cycle time** across all rules.
- Early-stage operations accumulated more queue time due to lot release batching and resource contention at shared tools.

## 10. Recommendations

- Use **FIFO** as the baseline dispatching rule — it achieved the lowest makespan and average cycle time in this benchmark configuration.
- Use **CR** as an alternative urgency-aware rule when due-date pressure becomes tighter, since its makespan is close to FIFO.
- Tighten **synthetic due-date assumptions** in future experiments to better differentiate EDD and CR performance.
- Prioritise **extra capacity investment on the composite bottleneck tool** (T07) before adding capacity to non-bottleneck tools.
- Combine **dispatching rules with capacity planning** — rule changes alone cannot overcome severe capacity constraints.

## 11. Limitations and Next Steps

- Benchmark data does not include real fab constraints: batching, rework, preventive maintenance, recipe qualification, tool dedication, or random downtime.
- Due dates and priorities are simulated (from the companion SQL data mart project).
- The project focuses on production logistics decision support rather than exact fab scheduling deployment.

**Potential extensions:**

- Add setup-time optimisation and family-based scheduling.
- Implement a linear programming module for optimal capacity allocation (`scipy.optimize.linprog` / `PuLP`).
- Extend to Flexible Job Shop Scheduling (FJSP) instances.
- Build a Streamlit interactive dashboard for what-if scenario testing.

## 12. Resume Bullet

**English:**

> Developed a Python-based fab capacity simulation model using public job-shop scheduling benchmark data; compared FIFO, SPT, EDD, and Critical Ratio dispatching rules, evaluated makespan, cycle time, queue time, tool utilization, and on-time rate, and conducted bottleneck capacity scenario analysis.

**中文：**

> 基于公开 Job Shop Scheduling benchmark 构建类晶圆厂产能仿真模型，使用 Python 比较 FIFO、SPT、EDD、Critical Ratio 等派工规则，并从 makespan、周期时间、排队时间、设备利用率和准时率角度评估产能改善方案。

## 13. Tech Stack

| Layer | Technology |
|-------|------------|
| Simulation Engine | Python (standard library + dataclasses) |
| Data Processing | pandas, csv |
| Visualization | matplotlib |
| Notebooks | Jupyter |
| Version Control | Git |

## 14. Relationship to the SQL Data Mart Project

This project is the **Python simulation counterpart** to the [Fab Production Logistics KPI Data Mart](../SQL/fab-production-logistics-sql/) SQL project:

| Project | Focus | Skills |
|---------|-------|--------|
| SQL Data Mart | KPI monitoring, dashboard, capacity audit | SQL, data modeling, dashboard |
| Python Simulation | Dispatching rules, capacity scenarios, optimization | Python, simulation, IE decision support |

Together they demonstrate: *"Logistics Engineering candidate with hands-on experience in SQL-based manufacturing KPI systems and Python-based capacity simulation for fab-like production environments."*
