# Methodology — Fab Capacity Simulation

## 1. Simulation Approach

This project uses a **discrete-event simulation (DES)** with next-event time advance to model a fab-like production system. Unlike continuous or system-dynamics models, DES captures the discrete nature of lot movement, tool allocation, and queue formation at individual workstations.

### Algorithm

```
1. Load all operations (lot routes) and lot release times.
2. Initialise:
   - lot_ready[lot_id]  ← release time
   - tool_available[tool_id] ← 0
   - next_op_idx[lot_id] ← 0
3. Loop:
   a. For each tool, collect all operations whose lot is ready and
      whose previous operation is done.
   b. For each tool with waiting operations, apply the dispatching
      rule to select one operation.
   c. Compute start_time = max(lot_ready, tool_available).
   d. Compute end_time = start_time + run_time.
   e. Record queue_time = start_time - lot_ready.
   f. Update lot_ready and tool_available.
   g. If no operation was scheduled, advance time to the next
      tool-available or lot-ready event.
   h. Stop when all operations are processed.
```

### Time Representation

All timestamps are converted to **fractional hours** from the earliest lot release time (epoch). This avoids timezone and calendar complexity while maintaining sub-hour precision.

## 2. Dispatching Rules

### FIFO (First-In-First-Out)
The simplest rule. Operations are processed in the order they become available at each tool. Productions systems often use FIFO as a baseline because it is fair, predictable, and easy to implement.

### SPT (Shortest Processing Time)
Selects the operation with the minimum run time. SPT is known to minimise average flow time in single-machine systems (Smith's rule). In multi-machine job shops, it tends to reduce average cycle time but may starve long operations, increasing their lateness.

### EDD (Earliest Due Date)
Selects the lot with the earliest due date. This rule directly targets on-time delivery performance. However, if due dates are not aligned with actual workload, EDD can increase overall cycle time.

### CR (Critical Ratio)
CR = (due_date − current_time) / remaining_processing_time. A CR < 1 means the lot is behind schedule; smaller CR indicates higher urgency. This rule dynamically re-prioritises lots as time progresses, balancing urgency and remaining work.

## 3. Performance Metrics

### Time-Based Metrics

- **Makespan**: Max(end_time) − min(release_time). Measures total production span.
- **Cycle Time**: finish_time − release_time per lot. Average and median reported.
- **Queue Time**: start_time − queue_start_time per operation. Summed per lot.
- **Queue Ratio**: queue_time / (queue_time + run_time). Indicates waste proportion.

### Delivery Metrics

- **On-Time Rate**: % of lots with finish_time ≤ due_date.
- **Lateness**: max(0, finish_time − due_date).

### Resource Metrics

The model reports two complementary bottleneck views:

- **Highest-Utilisation Tool** (`bottleneck_tool`): the tool with the highest busy-time ratio (Σ run_time / makespan). This is the traditional capacity-utilisation bottleneck.

- **Composite Bottleneck Tool** (`composite_bottleneck_tool`): the tool with the highest weighted bottleneck score combining utilisation (weight 0.4), average queue time (0.4), and WIP count (0.2), each min-max normalised across tools. This composite score captures both resource load and waiting impact, making it more representative of real fab bottlenecks where queue accumulation is as important as raw utilisation.

Capacity scenarios target the **composite bottleneck tool** because it better reflects where waiting time and congestion are concentrated.

## 4. Capacity Scenario Design

Capacity scenarios are evaluated by modifying the simulation parameters:

### Processing Time Reduction
A `speedup_factor` (e.g., 0.9 for +10% capacity) is applied to the bottleneck tool's run_time. This models process improvement, preventive maintenance reduction, or recipe optimisation.

### Parallel Tool Addition
A virtual second tool (`{tool_id}_EXTRA`) is added with identical capability. Operations can be dispatched to either the original or the extra tool. This models capital investment in additional equipment.

### Comparison Method
Each scenario runs the same set of dispatching rules (FIFO, SPT, EDD, CR). Improvement is measured as percentage change from baseline:
- Negative change in makespan/cycle_time/queue_time = improvement.
- Positive change in on-time rate = improvement.

## 5. Limitations

1. **No stochastic variability**: Processing times are deterministic from the benchmark. Real fabs have process variation.
2. **No tool downtime**: Random failures, preventive maintenance, and setup times are not modelled.
3. **No batching**: Some fab operations process multiple wafers simultaneously.
4. **No rework**: Defective lots are not re-introduced into the line.
5. **Simulated due dates**: Due dates are synthetically generated and may not reflect real customer commitments.
6. **Simplified tool grouping**: Real tool qualification and dedication rules are more complex.

Despite these limitations, the model captures the core IE trade-offs in production logistics: utilisation vs. cycle time vs. on-time delivery.

## 6. References

- Adams, J., Balas, E., & Zawack, D. (1988). The shifting bottleneck procedure for job shop scheduling. *Management Science*, 34(3), 391–401.
- Pinedo, M. L. (2016). *Scheduling: Theory, Algorithms, and Systems* (5th ed.). Springer.
- Hopp, W. J., & Spearman, M. L. (2011). *Factory Physics* (3rd ed.). Waveland Press.
