# 作品 2：Fab Capacity Simulation & Dispatching Optimization

## 1. 项目定位

**英文项目名：** Fab Capacity Simulation & Dispatching Optimization  
**中文项目名：** 晶圆厂产能仿真与派工规则优化

这个作品用于展示物流工程的核心能力：生产调度、排队系统、产能约束、瓶颈识别、运筹优化和 Python 数据分析。

它和作品 1 的关系：

- 作品 1 侧重 SQL、KPI 数据集市、dashboard。
- 作品 2 侧重 Python、仿真、调度规则比较、产能改善决策。

两个作品可以使用同一个公开 benchmark 数据源，但分析角度不同。作品 1 回答“如何监控 fab performance”，作品 2 回答“如何改善 fab performance”。

## 2. 数据地址

主数据源：

- GitHub 仓库：[Job Shop Scheduling Benchmark: Environments and Instances](https://github.com/ai-for-decision-making-tue/Job_Shop_Scheduling_Benchmark_Environments_and_Instances)
- 数据目录：[data/jsp](https://github.com/ai-for-decision-making-tue/Job_Shop_Scheduling_Benchmark_Environments_and_Instances/tree/main/data/jsp)
- 推荐起步数据：[data/jsp/adams](https://github.com/ai-for-decision-making-tue/Job_Shop_Scheduling_Benchmark_Environments_and_Instances/tree/main/data/jsp/adams)
- 对应论文：[Job Shop Scheduling Benchmark: Environments and Instances](https://arxiv.org/abs/2308.12794)

建议使用：

- `abz5`
- `abz6`
- `abz7`
- `abz8`
- `abz9`

如果后续想提升难度，可以扩展到更多 JSP 或 FJSP 数据。

## 3. 项目目标

核心业务问题：

> 在一个 fab-like 多工序、多设备生产系统中，不同派工规则会如何影响 makespan、cycle time、queue time、tool utilization、on-time rate 和 bottleneck load？

项目要输出：

1. 一个 Python 仿真程序。
2. 多种派工规则的对比结果。
3. 产能瓶颈识别。
4. 一组可视化图表。
5. 一个改善建议，例如增加瓶颈设备产能、调整派工规则或设置 priority。

## 4. 数据映射逻辑

| Benchmark 概念 | Fab-like 场景概念 | 用途 |
|---|---|---|
| job | lot | 生产批次 |
| operation | process step | 加工步骤 |
| machine | tool | 加工设备 |
| processing time | run time | 加工时长 |
| job route | process route | 工艺路线 |
| dispatching rule | lot release / dispatch policy | 派工策略 |
| makespan | total production completion time | 总完工时间 |
| flow time | cycle time | 周期时间 |

## 5. 推荐项目目录

```text
fab-capacity-simulation-python/
  README.md
  data/
    raw/
      abz5
      abz6
      abz7
      abz8
      abz9
    processed/
      operations.csv
      simulation_results.csv
      scenario_summary.csv
  notebooks/
    01_data_exploration.ipynb
    02_dispatching_simulation.ipynb
    03_capacity_scenario_analysis.ipynb
  src/
    parser.py
    simulator.py
    dispatch_rules.py
    metrics.py
    visualization.py
  outputs/
    figures/
      gantt_fifo.png
      rule_comparison.png
      bottleneck_ranking.png
      utilization_heatmap.png
  docs/
    methodology.md
```

## 6. 最终交付物

建议最终至少完成：

1. README。
2. 原始数据来源说明。
3. Python 数据解析脚本。
4. 离散事件仿真或简化调度仿真脚本。
5. 至少 4 种派工规则比较。
6. 产能场景分析。
7. 4-6 张图表。
8. 一段简历项目描述。

## 7. 创建步骤

### 第 1 步：定义业务场景

预计用时：0.5 天

README 中建议这样定义业务背景：

> This project simulates a fab-like production system where wafer lots follow fixed process routes across multiple tools. The goal is to compare dispatching rules and capacity scenarios to reduce cycle time, improve on-time delivery, and identify bottleneck tools.

业务假设：

1. 每个 lot 必须按照固定 route 加工。
2. 每道 operation 只能在指定 tool 上加工。
3. 每个 tool 同一时间只能加工一个 operation。
4. lot 可以在 tool 前等待，产生 queue time。
5. 不考虑设备故障、返工、批量合批等复杂 fab 规则。

这些假设要写在 README 里。面试时这样讲更严谨。

### 第 2 步：解析 benchmark 数据

预计用时：0.5-1 天

把原始 JSP 数据解析为 operation-level dataframe：

| 字段 | 含义 |
|---|---|
| instance_id | 数据实例 |
| lot_id | lot 编号 |
| operation_seq | 工序顺序 |
| tool_id | 设备编号 |
| run_time | 加工时长 |

示例：

| instance_id | lot_id | operation_seq | tool_id | run_time |
|---|---:|---:|---:|---:|
| abz5 | L001 | 1 | T04 | 88 |
| abz5 | L001 | 2 | T09 | 68 |

建议输出：

```text
data/processed/operations.csv
```

### 第 3 步：建立 baseline FIFO 仿真

预计用时：1 天

先实现最基础的 FIFO 规则，作为 baseline。

仿真逻辑：

1. 初始化所有 lot 的 release time。
2. 初始化所有 tool 的 available time。
3. 对每个可加工 operation，检查：
   - lot 是否完成上一道工序；
   - tool 是否可用。
4. 按 FIFO 选择最早等待的 lot。
5. 计算：
   - queue_start_time
   - start_time
   - end_time
   - queue_time
   - run_time
6. 更新 lot 和 tool 状态。
7. 重复直到所有 lot 完成。

输出 event log：

| 字段 | 含义 |
|---|---|
| scenario_id | 场景 ID |
| rule_name | 派工规则 |
| lot_id | lot 编号 |
| operation_seq | 工序顺序 |
| tool_id | 设备编号 |
| queue_start_time | 进入队列时间 |
| start_time | 开始加工时间 |
| end_time | 结束时间 |
| queue_time | 等待时间 |
| run_time | 加工时间 |

建议输出：

```text
data/processed/event_log_fifo.csv
```

### 第 4 步：实现多种 dispatching rules

预计用时：1-1.5 天

至少实现 4 种规则：

| 规则 | 英文 | 逻辑 | IE 含义 |
|---|---|---|---|
| 先进先出 | FIFO | 最早进入队列的 lot 优先 | 稳定、公平、易解释 |
| 最短加工时间 | SPT | run time 最短的 operation 优先 | 降低平均 flow time |
| 最早交期 | EDD | due date 最早的 lot 优先 | 提高准时率 |
| 关键比率 | CR | `(due date - current time) / remaining processing time` 最小者优先 | 优先处理延误风险 lot |

可选增强：

| 规则 | 英文 | 逻辑 |
|---|---|---|
| 最长剩余加工时间 | LRPT | 剩余加工时间最长的 lot 优先 |
| 瓶颈优先 | Bottleneck-first | 经过瓶颈 tool 的 lot 优先 |
| 加权优先级 | Weighted priority | 综合 due date、priority、remaining time |

建议先做 4 种核心规则，不要一开始做太复杂。

### 第 5 步：定义评价指标

预计用时：0.5 天

每个规则输出一行 scenario summary：

| 指标 | 含义 |
|---|---|
| makespan | 所有 lot 完成所需总时间 |
| avg_cycle_time | 平均周期时间 |
| median_cycle_time | 中位周期时间 |
| avg_queue_time | 平均等待时间 |
| queue_time_ratio | 等待时间 / 周期时间 |
| max_lateness | 最大延迟 |
| on_time_rate | 准时完成比例 |
| avg_tool_utilization | 平均设备利用率 |
| bottleneck_tool | 瓶颈设备 |
| bottleneck_utilization | 瓶颈设备利用率 |

重点不是指标越多越好，而是能讲清楚每个指标的 IE 含义。

### 第 6 步：做 rule comparison

预计用时：0.5-1 天

把 FIFO、SPT、EDD、CR 的结果放进同一张表：

| rule_name | makespan | avg_cycle_time | avg_queue_time | on_time_rate | bottleneck_tool |
|---|---:|---:|---:|---:|---|
| FIFO |  |  |  |  |  |
| SPT |  |  |  |  |  |
| EDD |  |  |  |  |  |
| CR |  |  |  |  |  |

需要回答：

1. 哪个规则 makespan 最低？
2. 哪个规则 average cycle time 最低？
3. 哪个规则 on-time rate 最好？
4. 哪个规则让瓶颈 tool 的负载最集中？
5. 如果业务目标不同，应该选哪个规则？

这部分适合在 README 里写成业务结论。

### 第 7 步：做 capacity scenario analysis

预计用时：1 天

这是作品 2 最贴 JD 的部分。不要只比较规则，还要做产能改善场景。

建议设置 3-4 个场景：

| 场景 | 描述 |
|---|---|
| baseline | 原始设备能力 |
| bottleneck +10% capacity | 瓶颈设备加工时间减少 10%，等价于产能提升 |
| bottleneck +20% capacity | 瓶颈设备加工时间减少 20% |
| add one parallel bottleneck tool | 为瓶颈工站增加一台并行设备 |

每个场景跑同一套 dispatching rules，然后比较：

- makespan 改善比例
- avg cycle time 改善比例
- queue time 改善比例
- on-time rate 改善比例
- bottleneck utilization 变化

建议输出：

```text
data/processed/scenario_summary.csv
```

### 第 8 步：可选加入线性规划模型

预计用时：1-2 天

如果时间允许，可以加一个小型 linear programming / integer programming 模块。不要把它做得过大，重点是展示岗位要求中的 linear programming skill。

推荐问题：

> Given limited additional capacity hours, decide how many hours to allocate to each tool group to minimize total capacity shortage.

决策变量：

```text
x_g = additional capacity hours allocated to tool group g
```

目标函数：

```text
minimize total remaining capacity gap
```

约束：

```text
sum(x_g) <= total_extra_capacity_budget
x_g >= 0
x_g <= max_extra_capacity_per_group
```

输出：

- 哪些 tool group 应优先获得额外产能。
- 预计可以减少多少 capacity gap。
- 对 cycle time / queue time 的改善预估。

工具选择：

- `scipy.optimize.linprog`
- `PuLP`
- `OR-Tools`

如果你只做简历版本，可以把这一步作为 advanced module，不一定第一版完成。

### 第 9 步：制作可视化图表

预计用时：0.5-1 天

至少输出 4 张图：

1. **Gantt chart**
   - 展示 lot 在不同 tool 上的加工时间。
   - 用于解释仿真逻辑。

2. **Dispatching rule comparison bar chart**
   - 比较 makespan、avg cycle time、on-time rate。

3. **Tool utilization heatmap**
   - 展示不同 tool 的负载。
   - 用于识别瓶颈。

4. **Bottleneck ranking chart**
   - 按 utilization、queue time 或 bottleneck score 排名。

可选图表：

- Queue time distribution。
- Cycle time distribution。
- Capacity scenario improvement waterfall chart。
- WIP over time。

建议输出目录：

```text
outputs/figures/
```

### 第 10 步：写 README

预计用时：0.5-1 天

README 推荐结构：

```text
1. Business Background
2. Data Source
3. Fab-like Mapping
4. Simulation Assumptions
5. Dispatching Rules
6. Performance Metrics
7. Capacity Scenario Design
8. Results and Findings
9. Recommendations
10. Limitations and Next Steps
```

Results and Findings 可以写：

- SPT reduced average cycle time compared with FIFO, but did not necessarily improve on-time rate.
- EDD improved due-date performance but sometimes increased average queue time.
- Bottleneck capacity expansion reduced queue time more effectively than changing dispatching rules alone.
- The most constrained tool group drove a large share of total waiting time.

Recommendations 可以写：

- Use EDD or CR when due-date performance is the primary objective.
- Use SPT when average cycle time reduction is the primary objective.
- Prioritize extra capacity investment on the highest-utilization tool group before adding capacity to non-bottleneck tools.

Limitations 要写：

- Benchmark data does not include real fab constraints such as batching, rework, preventive maintenance, recipe qualification, tool dedication, or random downtime.
- Due dates and priorities are simulated.
- The project focuses on production logistics decision support rather than exact fab scheduling deployment.

## 8. 预计总用时

| 阶段 | 预计用时 |
|---|---:|
| 定义业务场景 | 0.5 天 |
| 解析 benchmark 数据 | 0.5-1 天 |
| 建立 FIFO baseline 仿真 | 1 天 |
| 实现多种 dispatching rules | 1-1.5 天 |
| 定义指标与输出 summary | 0.5 天 |
| rule comparison 分析 | 0.5-1 天 |
| capacity scenario analysis | 1 天 |
| 可视化图表 | 0.5-1 天 |
| README + 简历 bullet | 0.5-1 天 |
| 可选 LP 模型 | 1-2 天 |

总计：

- 快速可展示版本：4-5 天
- 简历可用版本：7-10 天
- 带 LP 优化增强版本：10-14 天

## 9. 简历写法

英文版：

> Developed a Python-based fab capacity simulation model using public job-shop scheduling benchmark data; compared FIFO, SPT, EDD, and Critical Ratio dispatching rules, evaluated makespan, cycle time, queue time, tool utilization, and on-time rate, and conducted bottleneck capacity scenario analysis.

中文版：

> 基于公开 Job Shop Scheduling benchmark 构建类晶圆厂产能仿真模型，使用 Python 比较 FIFO、SPT、EDD、Critical Ratio 等派工规则，并从 makespan、周期时间、排队时间、设备利用率和准时率角度评估产能改善方案。

## 10. 面试讲法

建议用 60 秒说明：

> 这个项目是从物流工程和生产调度角度切入的。我把公开 job-shop scheduling benchmark 映射成 fab-like lot flow，每个 lot 按固定 route 经过多台 tool。我先建立 FIFO baseline，然后实现 SPT、EDD 和 Critical Ratio 等派工规则，比较它们对 makespan、cycle time、queue time、tool utilization 和 on-time rate 的影响。之后我做了瓶颈产能场景分析，比如给瓶颈 tool group 增加 10% 或 20% 产能，评估它对排队时间和准时率的改善。这个项目主要体现我能用 Python 和运筹思维做 manufacturing capacity decision support。

## 11. 和作品 1 的组合讲法

这两个作品应该组合呈现：

| 作品 | 重点 | 对应岗位能力 |
|---|---|---|
| Fab Production Logistics KPI Data Mart | SQL、数据集市、KPI、dashboard | performance metrics tracking、reporting、capacity audit |
| Fab Capacity Simulation & Dispatching Optimization | Python、仿真、派工规则、产能场景 | capacity modeling、linear programming、decision tools |

组合后的个人定位：

> Logistics Engineering candidate with hands-on experience in SQL-based manufacturing KPI systems and Python-based capacity simulation for fab-like production environments.

