# Project Completion Improvement Plan

本文档用于整理 Fab Capacity Simulation & Dispatching Optimization 项目的后续修改步骤。目标是把当前项目从约 80%-85% 完成度提升到 90%+ 的简历可展示版本。

## 1. 当前完成度结论

当前项目已经具备核心功能：

- 已有 README、项目规划文档和 methodology 文档。
- 已解析 `abz5-abz9` 五个 benchmark 实例。
- `operations.csv` 包含 1,100 条 operation 和 80 个 lot。
- 已实现解析、仿真、派工规则、指标计算和图表生成模块。
- 已实现 FIFO、SPT、EDD、CR 四种核心派工规则。
- 已输出 baseline simulation summary、capacity scenario summary 和多张图表。

但项目还存在几个影响展示质量的问题：

- 当前运行环境没有完全打通，`run_all.py` 无法在现有 Python 环境中完整生成图表。
- README 部分结论与实际仿真结果不一致。
- bottleneck 定义存在两个口径。
- notebook 有代码结构，但尚未保存执行输出。
- 项目还没有形成完全一键复现的交付状态。

## 2. 修改目标

最终应达到以下状态：

1. 能通过固定命令完整重跑数据解析、仿真、场景分析和图表生成。
2. README 中的结果结论与 `simulation_summary.csv` 和 `scenario_summary.csv` 一致。
3. bottleneck 口径统一，避免面试讲解时出现冲突。
4. notebook 执行后保存输出，可直接作为分析展示材料。
5. 所有核心输出文件和图表可复现。

## 3. 第一步：修复运行环境

当前问题：

- 终端中的 `python` 命令不可用。
- 内置 Python 缺少 `matplotlib`，导致 `run_all.py` 在生成图表阶段失败。

建议使用本机 Python 创建虚拟环境：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

建议将 `requirements.txt` 补充为：

```txt
pandas>=1.3.0
matplotlib>=3.4.0
jupyter>=1.0.0
nbconvert>=7.0.0
ipykernel>=6.0.0
```

环境配置完成后，运行：

```powershell
python run_all.py
```

验收标准：

- 脚本可以跑完整个 baseline、capacity scenario 和 chart generation。
- `outputs/figures/` 下图表能重新生成。

## 4. 第二步：修正 README 与实际结果不一致的问题

需要修改文件：

```text
README.md
```

### 4.1 修正数据目录说明

当前 README 中写的是：

```text
data/jsp/adams/
```

但实际项目使用的是：

```text
data/raw/
```

建议将数据目录说明改为：

```md
- **Data Directory**: `data/raw/`
```

### 4.2 修正 Results and Findings

当前 baseline 结果为：

| Rule | Makespan | Avg Cycle Time | Avg Queue Time | On-Time Rate | Bottleneck Tool |
|---|---:|---:|---:|---:|---|
| FIFO | 82.25h | 54.89h | 47.36h | 100.0% | T01 |
| SPT | 118.02h | 60.54h | 53.02h | 100.0% | T01 |
| EDD | 119.52h | 66.78h | 59.26h | 100.0% | T01 |
| CR | 83.87h | 62.98h | 55.46h | 100.0% | T01 |

因此 README 中不应继续写：

```text
SPT reduces average cycle time compared to FIFO.
EDD improves due-date performance.
```

建议改为：

```md
In this benchmark setting, FIFO achieved the lowest makespan and average cycle time, while CR produced a similar makespan but higher average cycle time. SPT and EDD did not outperform FIFO under the current synthetic release and due-date assumptions.
```

由于当前所有规则的 on-time rate 都是 100%，建议补充：

```md
Because synthetic due dates are relatively loose, all dispatching rules reached 100% on-time rate. Future versions should tighten due-date assumptions to better evaluate EDD and CR.
```

### 4.3 修正 Recommendations

当前数据并不能证明 EDD 或 CR 改善准时率，因此建议将 recommendation 改成更谨慎的表达：

```md
- Use FIFO as the current baseline rule because it achieved the lowest makespan and average cycle time in this benchmark configuration.
- Use CR as an alternative urgency-aware rule when due-date pressure becomes tighter.
- Tighten synthetic due-date assumptions in future experiments to better compare EDD and CR.
- Prioritise capacity improvement on the composite bottleneck tool before adding capacity to non-bottleneck tools.
```

## 5. 第三步：统一 bottleneck 定义

当前项目存在两个 bottleneck 口径：

- `simulator.py` 的 summary 使用最高 utilization，结果为 `T01`。
- `run_all.py` 使用 composite bottleneck ranking，结果为 `T07`。

建议统一为 composite bottleneck score，因为 methodology 中已经定义：

```text
Bottleneck Score = utilization 0.4 + queue time 0.4 + WIP 0.2
```

推荐修改方式：

1. 保留 `T01` 作为 `highest_utilization_tool`。
2. 将 composite ranking 第一名 `T07` 作为 `composite_bottleneck_tool`。
3. README 和 methodology 中明确两个概念的区别。

推荐表达：

```md
The model reports two bottleneck-related views:

- **Highest Utilization Tool**: the tool with the highest busy-time ratio.
- **Composite Bottleneck Tool**: the tool with the highest weighted score based on utilization, average queue time, and WIP count.

Capacity scenarios use the composite bottleneck tool because it better reflects both resource load and waiting impact.
```

## 6. 第四步：修正图表默认规则

需要修改文件：

```text
src/visualization.py
```

当前 `generate_all_charts()` 中使用排序后的第一个 rule，因此可能默认选择 `CR`，导致输出：

```text
gantt_cr.png
queue_distribution_cr.png
utilization_heatmap_cr.png
```

建议默认优先使用 FIFO：

```python
rule_names = sorted(set(s.get("rule_name", "FIFO") for s in summaries))
primary_rule = "FIFO" if "FIFO" in rule_names else rule_names[0]
```

然后将以下调用改为使用 `primary_rule`：

```python
plot_gantt(events, rule_name=primary_rule)
plot_utilization_heatmap(events, rule_name=primary_rule)
plot_queue_distribution(events, rule_name=primary_rule)
```

验收标准：

- 默认生成 FIFO baseline 图表。
- 输出文件名与 README 中的 baseline 叙述一致。

## 7. 第五步：增强 run_all.py 的一键复现能力

需要修改文件：

```text
run_all.py
```

当前 `run_all.py` 已能生成 `scenario_summary.csv`，但建议同时保存：

```text
data/processed/simulation_events.csv
data/processed/simulation_summary.csv
data/processed/scenario_summary.csv
```

建议在 baseline 跑完后加入：

```python
# Save baseline events
events_path = os.path.join(PROJECT, "data", "processed", "simulation_events.csv")
flat_events = []
for ev_list in base_ev.values():
    flat_events.extend(ev_list)

with open(events_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=flat_events[0].keys())
    w.writeheader()
    w.writerows(flat_events)

# Save baseline summary
summary_path = os.path.join(PROJECT, "data", "processed", "simulation_summary.csv")
with open(summary_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=base_sum[0].keys())
    w.writeheader()
    w.writerows(base_sum)
```

验收标准：

- 运行 `python run_all.py` 后，三个核心 processed 文件都能重新生成。
- `simulation_events.csv` 应有 4,400 行。
- `simulation_summary.csv` 应有 4 行。
- `scenario_summary.csv` 应有 16 行。

## 8. 第六步：执行并保存 notebooks 输出

当前三个 notebook 有分析结构，但没有执行输出。建议全部执行并保存。

运行：

```powershell
jupyter nbconvert --to notebook --execute notebooks\01_data_exploration.ipynb --inplace
jupyter nbconvert --to notebook --execute notebooks\02_dispatching_simulation.ipynb --inplace
jupyter nbconvert --to notebook --execute notebooks\03_capacity_scenario_analysis.ipynb --inplace
```

验收标准：

- notebook 中可以看到表格结果。
- notebook 中可以看到图表输出。
- 打开 notebook 时不是只有代码和 markdown。

## 9. 第七步：增加 README 复现检查清单

建议在 README 中增加：

```md
## Reproducibility Check

Run the full pipeline:

```bash
python src/parser.py
python run_all.py
```

Expected outputs:

- `data/processed/operations.csv`
- `data/processed/simulation_events.csv`
- `data/processed/simulation_summary.csv`
- `data/processed/scenario_summary.csv`
- `outputs/figures/*.png`
```

这样 README 会更像完整作品，而不是只描述项目内容。

## 10. 最终验收命令

完成以上修改后，依次运行：

```powershell
python src/parser.py
python src/simulator.py --rules FIFO SPT EDD CR --scenario baseline
python run_all.py
```

然后检查：

```powershell
(Import-Csv data\processed\operations.csv).Count
(Import-Csv data\processed\simulation_events.csv).Count
(Import-Csv data\processed\simulation_summary.csv).Count
(Import-Csv data\processed\scenario_summary.csv).Count
Get-ChildItem outputs\figures
```

期望结果：

| File | Expected Rows |
|---|---:|
| `operations.csv` | 1,100 |
| `simulation_events.csv` | 4,400 |
| `simulation_summary.csv` | 4 |
| `scenario_summary.csv` | 16 |

图表目录中至少应包含：

- `gantt_fifo.png`
- `rule_comparison.png`
- `utilization_heatmap_fifo.png`
- `bottleneck_ranking.png`
- `queue_distribution_fifo.png`
- `scenario_improvement_waterfall.png`

## 11. 建议优先级

如果时间有限，优先级如下：

| Priority | Task | Reason |
|---|---|---|
| P0 | 修复 Python 环境和依赖 | 否则无法一键复现 |
| P0 | 修正 README 结果结论 | 避免文档与数据冲突 |
| P1 | 统一 bottleneck 定义 | 避免面试讲解混乱 |
| P1 | 修正默认图表规则为 FIFO | 保持 baseline 展示一致 |
| P1 | 增强 `run_all.py` 输出 | 提升项目工程完整度 |
| P2 | 执行并保存 notebooks | 提升展示效果 |
| P2 | 增加 README 复现清单 | 提升作品专业度 |

## 12. 完成后的项目状态

完成以上修改后，项目可以定位为：

> A reproducible Python-based fab capacity simulation project that parses public job-shop benchmark data, runs multiple dispatching rules, evaluates manufacturing KPIs, identifies bottlenecks, tests capacity scenarios, and generates analysis-ready tables and figures.

简历项目完成度可提升到 90%+。
