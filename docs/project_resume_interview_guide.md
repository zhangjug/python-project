# Fab Capacity Simulation 项目简历与面试讲解指南

本文档用于回答三个问题：

1. 当前版本是否已经可以完成项目。
2. 这个项目如何展示在简历上。
3. 面试时如果被问到项目细节，应该如何解释业务逻辑、代码步骤和 Python 语法。

项目名：

```text
Fab Capacity Simulation & Dispatching Optimization
```

中文名：

```text
晶圆厂产能仿真与派工规则优化
```

## 1. 当前版本检查结论

### 1.1 可以完成项目吗？

结论：**可以。当前版本已经具备简历项目的主体完成度，可以作为 portfolio 项目展示。**

当前版本已经完成：

- 使用公开 Job Shop Scheduling benchmark 数据。
- 使用 `abz5`、`abz6`、`abz7`、`abz8`、`abz9` 五个实例。
- 解析出 80 个 lot、1,100 道 operation。
- 实现 Python 离散事件仿真。
- 实现 FIFO、SPT、EDD、CR 四种派工规则。
- 计算 makespan、cycle time、queue time、on-time rate、tool utilization、bottleneck 等指标。
- 运行 baseline 和 3 个 capacity scenario。
- 生成 CSV 结果表和 6 类图表。
- README 已包含项目背景、数据来源、业务假设、结果和建议。
- notebook 已有执行输出，可用于展示分析过程。

当前版本输出检查：

| Output | Current Status | Expected |
|---|---:|---:|
| `data/processed/operations.csv` | 1,100 rows | 1,100 rows |
| `data/processed/simulation_events.csv` | 4,400 rows | 4,400 rows |
| `data/processed/simulation_summary.csv` | 4 rows | 4 rows |
| `data/processed/scenario_summary.csv` | 16 rows | 16 rows |
| `outputs/figures/*.png` | 已生成 FIFO 图表和对比图 | 至少 6 张图 |
| notebooks | 已有执行输出 | 可展示 |

因此，从“能不能作为简历项目”角度看，答案是：

```text
可以。当前项目已经能讲清楚业务问题、数据来源、模型逻辑、代码实现、结果和改进建议。
```

### 1.2 当前状态

以上问题已全部修复：

1. ✅ `python` 命令可用，依赖通过 `requirements.txt` 管理。
2. ✅ 项目已初始化 Git 仓库并推送到 GitHub。
3. ✅ `simulator.py` 的瓶颈计算已修正，结果可稳定复现。
4. ✅ 新增 `tests/test_reproducibility.py`，支持 `unittest discover` 和 `pytest`。
5. ✅ MIT License 已添加。
## 2. 推荐最终完成标准

如果你要把它作为正式简历项目，建议最终达到：

```text
python src/parser.py
python run_all.py
```

两条命令可以完整跑通，并重新生成：

- `operations.csv`
- `simulation_events.csv`
- `simulation_summary.csv`
- `scenario_summary.csv`
- `outputs/figures/*.png`

如果当前机器没有 Python，需要先安装 Python 并配置环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/parser.py
python run_all.py
```

如果 `python` 命令不可用，可以安装 Python 后勾选：

```text
Add python.exe to PATH
```

## 3. 简历上怎么展示

### 3.1 项目标题

英文简历推荐标题：

```text
Fab Capacity Simulation & Dispatching Optimization | Python, Discrete-Event Simulation, Scheduling
```

中文简历推荐标题：

```text
晶圆厂产能仿真与派工规则优化 | Python, 离散事件仿真, 生产调度
```

### 3.2 英文简历 bullet

推荐版本：

```text
- Built a Python-based discrete-event simulation model for a fab-like job-shop system using 5 public benchmark instances, covering 80 lots and 1,100 operations.
- Implemented FIFO, SPT, EDD, and Critical Ratio dispatching rules and evaluated makespan, cycle time, queue time, tool utilization, and on-time delivery performance.
- Identified bottleneck tools using utilization, queue time, and WIP-based scoring, and tested +10%, +20%, and parallel-tool capacity scenarios; the parallel-tool scenario reduced FIFO average cycle time by 9.4% and queue time by 10.9%.
```

更短的一行版本：

```text
Developed a Python discrete-event simulation for fab-like production scheduling; compared FIFO/SPT/EDD/CR rules across 80 lots and 1,100 operations, identified bottlenecks, and evaluated capacity expansion scenarios.
```

### 3.3 中文简历 bullet

推荐版本：

```text
- 基于公开 Job Shop Scheduling benchmark 构建类晶圆厂产能仿真模型，覆盖 80 个 lot 和 1,100 道工序。
- 使用 Python 实现 FIFO、SPT、EDD、Critical Ratio 等派工规则，对 makespan、周期时间、排队时间、设备利用率和准时率进行评估。
- 结合设备利用率、平均排队时间和 WIP 数量识别瓶颈设备，并测试瓶颈产能 +10%、+20% 和新增并行设备场景；并行设备场景下 FIFO 平均周期时间降低 9.4%，排队时间降低 10.9%。
```

### 3.4 简历里不要过度声称

不要写：

```text
Optimized real fab production scheduling.
```

因为这个项目不是实际 fab MES 数据。

建议写：

```text
Built a fab-like simulation model using public benchmark data.
```

不要写：

```text
EDD improved on-time delivery.
```

因为当前 synthetic due date 比较宽松，所有规则 on-time rate 都是 100%。

建议写：

```text
Evaluated on-time delivery under synthetic due-date assumptions.
```

## 4. 面试时 60 秒讲法

可以这样说：

```text
这个项目是一个类晶圆厂产能仿真和派工规则优化项目。我使用公开的 job-shop scheduling benchmark，把 job 映射成 lot，把 machine 映射成 tool，把 operation 映射成 process step。然后用 Python 搭建了一个离散事件仿真模型，模拟每个 lot 按固定 route 经过不同 tool 加工的过程。

模型中每个 tool 同一时间只能加工一道 operation，如果多个 lot 同时等待同一个 tool，就通过派工规则决定谁先加工。我实现了 FIFO、SPT、EDD 和 Critical Ratio 四种规则，并比较 makespan、平均周期时间、排队时间、设备利用率和准时率。

在当前数据设置下，FIFO 的 makespan 和平均 cycle time 最低，CR 的 makespan 接近 FIFO，但更适合未来 due date 更紧的场景。之后我用利用率、排队时间和 WIP 的综合评分识别瓶颈设备，并测试了瓶颈设备提速 10%、20% 和新增并行设备的场景。结果显示新增并行瓶颈设备对 FIFO 的平均周期时间和排队时间改善最大。
```

## 5. 项目结构怎么讲

面试官如果让你介绍 repo，可以按这个顺序：

```text
README.md
```

说明项目背景、数据来源、业务假设、结果和建议。

```text
data/raw/
```

存放原始 benchmark 数据。

```text
data/processed/
```

存放解析后的 operation table、仿真事件表和 summary 表。

```text
src/parser.py
```

负责把原始 JSP 数据解析成 operation-level CSV。

```text
src/dispatch_rules.py
```

定义 FIFO、SPT、EDD、CR、LRPT 派工规则。

```text
src/simulator.py
```

核心离散事件仿真引擎。

```text
src/metrics.py
```

计算 KPI、瓶颈排名和场景改善比例。

```text
src/visualization.py
```

生成 Gantt chart、rule comparison、utilization heatmap、bottleneck ranking、queue distribution、scenario improvement chart。

```text
run_all.py
```

一键运行 baseline、capacity scenarios、保存 CSV 和生成图表。

```text
notebooks/
```

用于展示探索分析、派工规则比较和产能场景分析。

## 6. 每一步大概用了什么代码

这一节是面试重点。你不需要逐字背代码，但要知道每一步在 Python 里是怎么实现的。

## 6.1 Step 1 - 读取原始 benchmark 数据

对应文件：

```text
src/parser.py
```

核心逻辑：

```python
with open(path) as f:
    lines = [line.strip() for line in f if line.strip()]
```

语法解释：

- `with open(path) as f`：打开文件，读取结束后自动关闭。
- `line.strip()`：去掉每行前后的空格和换行符。
- `[... for line in f if line.strip()]`：列表推导式，只保留非空行。

原始 JSP 文件格式类似：

```text
10 10
4 88 8 68 6 94 ...
```

第一行表示：

```text
num_jobs num_machines
```

后面的每一行表示一个 job 的 route：

```text
machine_id processing_time machine_id processing_time ...
```

代码中这样解析第一行：

```python
header = lines[0].split()
num_jobs = int(header[0])
num_machines = int(header[1])
```

语法解释：

- `split()`：按空格切分字符串。
- `int()`：把字符串转成整数。

解析 route：

```python
tokens = list(map(int, line.split()))
ops = [(tokens[i], tokens[i + 1]) for i in range(0, len(tokens), 2)]
```

语法解释：

- `map(int, line.split())`：把每个字符串 token 转成整数。
- `range(0, len(tokens), 2)`：每次跳 2 个位置，因为数据是 machine/time 成对出现。
- `(tokens[i], tokens[i + 1])`：组成 `(machine_id, run_time)` tuple。

面试解释：

```text
我先把原始 job-shop 文件读进来，然后按照 machine_id 和 processing_time 成对解析。每个 job 的一行 route 被转换成多个 operation，每个 operation 包含 lot_id、operation_seq、tool_id 和 run_time。
```

## 6.2 Step 2 - 转换成 fab-like operation table

对应代码：

```python
for job_idx, op_list in enumerate(routes):
    lot_counter += 1
    lot_id = f"L{lot_counter:04d}"
    for op_seq, (machine_id, run_time_min) in enumerate(op_list, start=1):
        rows.append({
            "instance_id": instance_id,
            "lot_id": lot_id,
            "operation_seq": op_seq,
            "tool_id": f"T{machine_id:02d}",
            "run_time": round(run_time_min / 60.0, 4),
        })
```

语法解释：

- `enumerate(routes)`：同时拿到序号和元素。
- `enumerate(op_list, start=1)`：operation sequence 从 1 开始。
- `f"L{lot_counter:04d}"`：格式化字符串，例如 `L0001`。
- `f"T{machine_id:02d}"`：格式化 tool id，例如 `T04`。
- `rows.append({...})`：向 list 中添加一行 dict。
- `round(run_time_min / 60.0, 4)`：把分钟转成小时，并保留 4 位小数。

面试解释：

```text
这里完成了从 benchmark 到 fab 语义的映射：job 变成 lot，machine 变成 tool，processing time 变成 run time，job route 变成 lot 的 process route。
```

## 6.3 Step 3 - 写出 operations.csv

对应代码：

```python
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
```

语法解释：

- `csv.DictWriter`：把 dict list 写成 CSV。
- `fieldnames`：指定 CSV 列名顺序。
- `writeheader()`：写表头。
- `writerows(rows)`：一次写入多行。

面试解释：

```text
我把解析后的 operation-level 数据写成 CSV，后续仿真模块直接读取这个标准化表，而不是每次都读原始 benchmark。
```

## 6.4 Step 4 - 读取 processed 数据

对应文件：

```text
src/simulator.py
```

对应代码：

```python
with open(csv_path, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        r["operation_seq"] = int(r["operation_seq"])
        r["run_time"] = float(r["run_time"])
        rows.append(r)
```

语法解释：

- `csv.DictReader(f)`：把 CSV 每一行读成 dict。
- CSV 读出来默认都是字符串，所以要用 `int()` 和 `float()` 转换数值字段。

面试解释：

```text
仿真时我先读入 operations.csv，并把 operation_seq 转成整数，把 run_time 转成 float，因为这些字段后续要排序和做时间计算。
```

## 6.5 Step 5 - 按 lot 分组并排序 route

对应代码：

```python
lot_ops = defaultdict(list)
for op in operations:
    lot_ops[op["lot_id"]].append(deepcopy(op))
for ops in lot_ops.values():
    ops.sort(key=lambda x: x["operation_seq"])
```

语法解释：

- `defaultdict(list)`：如果 key 不存在，自动创建一个空 list。
- `deepcopy(op)`：复制 operation，避免修改原始数据。
- `sort(key=lambda x: x["operation_seq"])`：按 operation sequence 排序。
- `lambda x: x["operation_seq"]`：匿名函数，告诉 `sort` 用哪个字段排序。

面试解释：

```text
每个 lot 必须按照固定 route 加工，所以我先把 operation 按 lot_id 分组，再按 operation_seq 排序，保证仿真中每个 lot 只能按顺序进入下一道工序。
```

## 6.6 Step 6 - 初始化仿真状态

对应代码：

```python
tool_available = defaultdict(float)
lot_ready = {}
for lot_id in lot_ops:
    lot_ready[lot_id] = lot_info[lot_id]["release_ts_hours"]

next_op_idx = {lot_id: 0 for lot_id in lot_ops}
```

语法解释：

- `tool_available[tool_id]`：记录每台 tool 下一次可用时间。
- `lot_ready[lot_id]`：记录每个 lot 上一道工序完成后何时可进入下一道。
- `next_op_idx`：记录每个 lot 当前要加工第几道 operation。
- `{lot_id: 0 for lot_id in lot_ops}`：字典推导式。

面试解释：

```text
离散事件仿真核心是维护状态。这里我维护了 tool 状态、lot 状态和每个 lot 的下一道工序索引。每调度一次 operation，就更新这些状态。
```

## 6.7 Step 7 - 收集每台 tool 当前可加工的 operation

对应代码逻辑：

```python
tool_queues = defaultdict(list)

for lot_id, ops in lot_ops.items():
    idx = next_op_idx[lot_id]
    if idx >= len(ops):
        continue

    op = ops[idx]
    tool_id = op["tool_id"]
    op_ready_time = max(lot_ready[lot_id], 0)

    tool_queues[tool_id].append({
        "lot_id": lot_id,
        "tool_id": tool_id,
        "operation_seq": op["operation_seq"],
        "run_time": run_time,
        "queue_start_time": op_ready_time,
        "lot_ready_time": lot_ready[lot_id],
    })
```

语法解释：

- `.items()`：同时遍历 dict 的 key 和 value。
- `continue`：跳过当前循环。
- `max(lot_ready[lot_id], 0)`：确保 ready time 不小于 0。
- `tool_queues[tool_id].append(...)`：把当前可等待的 operation 放进对应 tool 队列。

面试解释：

```text
每一轮仿真，我会看每个 lot 当前下一道 operation 是什么。如果它的上一道已经完成，就把它加入目标 tool 的等待队列。这样每台 tool 都会有一个 ready queue。
```

## 6.8 Step 8 - 派工规则如何实现

对应文件：

```text
src/dispatch_rules.py
```

### FIFO

```python
return min(ready_queue, key=lambda op: op["queue_start_time"])
```

含义：

```text
谁最早进入队列，谁先加工。
```

语法：

- `min(list, key=...)`：按某个字段取最小值对应的元素。
- `lambda op: op["queue_start_time"]`：用 queue_start_time 作为比较标准。

### SPT

```python
return min(ready_queue, key=lambda op: op["run_time"])
```

含义：

```text
加工时间最短的 operation 先加工。
```

### EDD

```python
return min(ready_queue, key=lambda op: lot_info[op["lot_id"]]["due_ts_hours"])
```

含义：

```text
交期最早的 lot 先加工。
```

### CR

```python
def _critical_ratio(op):
    due = lot_info[op["lot_id"]]["due_ts_hours"]
    remaining = lot_info[op["lot_id"]]["total_remaining_run_time"]
    slack = due - current_time
    return slack / remaining

return min(ready_queue, key=_critical_ratio)
```

含义：

```text
Critical Ratio = 剩余时间 / 剩余加工时间。
值越小，说明越紧急。
```

面试解释：

```text
我把每种 dispatching rule 都写成一个函数，输入是当前 tool 的 ready queue、当前时间和 lot 信息，输出是被选中的 operation。这样 simulator 不需要关心规则细节，只需要通过规则名字从 RULES 字典里取函数。
```

## 6.9 Step 9 - 用函数注册表选择派工规则

对应代码：

```python
RULES = {
    "FIFO": fifo,
    "SPT":  spt,
    "EDD":  edd,
    "CR":   cr,
    "LRPT": lrpt,
}
```

仿真中调用：

```python
rule_fn = RULES.get(rule_name, RULES["FIFO"])
selected = rule_fn(queue, current_time, lot_info)
```

语法解释：

- 字典的 value 可以是函数。
- `RULES.get(rule_name, RULES["FIFO"])`：如果找不到规则名，就默认用 FIFO。
- `rule_fn(...)`：调用被选中的函数。

面试解释：

```text
这个设计让派工规则可扩展。如果后面要加 Bottleneck-first 或 weighted priority，只要新写一个函数并放进 RULES 字典，不需要重写 simulator。
```

## 6.10 Step 10 - 计算 start_time、end_time、queue_time

对应代码：

```python
start_time = max(selected["lot_ready_time"], tool_available.get(tool_id, 0.0))
end_time = start_time + selected["run_time"]
queue_time = start_time - selected["queue_start_time"]
```

公式解释：

```text
start_time = max(lot 上一道工序完成时间, tool 可用时间)
end_time = start_time + run_time
queue_time = start_time - queue_start_time
```

语法解释：

- `dict.get(key, default)`：如果 key 不存在，返回默认值。
- `max(a, b)`：两个条件都满足后才能开始加工。

面试解释：

```text
operation 的开始时间由两个条件决定：lot 本身要 ready，tool 也要 available。所以 start_time 是两者的最大值。
```

## 6.11 Step 11 - 更新状态并记录 event log

对应代码：

```python
events.append({
    "scenario_id": scenario_id,
    "rule_name": rule_name,
    "lot_id": lot_id,
    "operation_seq": selected["operation_seq"],
    "tool_id": selected["tool_id"],
    "queue_start_time": round(selected["queue_start_time"], 4),
    "start_time": round(start_time, 4),
    "end_time": round(end_time, 4),
    "queue_time": round(queue_time, 4),
    "run_time": round(selected["run_time"], 4),
})

tool_available[tool_id] = end_time
lot_ready[lot_id] = end_time
next_op_idx[lot_id] += 1
```

语法解释：

- `events.append({...})`：记录每一道工序的仿真事件。
- `round(value, 4)`：控制小数位。
- `+= 1`：当前 lot 进入下一道 operation。

面试解释：

```text
每完成一次 dispatch，我都会写一条 event log，记录它在哪个 tool 上、什么时候进队列、什么时候开始、什么时候结束、等了多久。之后所有 KPI 都从 event log 汇总出来。
```

## 6.12 Step 12 - 计算 KPI

对应文件：

```text
src/simulator.py
src/metrics.py
```

### Makespan

```python
makespan = max(ev["end_time"] for ev in events)
```

含义：

```text
所有 operation 完成的最终时间。
```

### Cycle Time

```python
cycle_h = finish_h - release_h
```

含义：

```text
lot 从 release 到最终完成的总时间。
```

### Queue Time

```python
total_queue = sum(ev["queue_time"] for ev in evs)
```

含义：

```text
lot 在所有 operation 前等待时间之和。
```

### On-Time Rate

```python
on_time = 1 if finish_h <= due_h else 0
on_time_rate = on_time_count / n * 100
```

语法解释：

- `1 if condition else 0`：Python 三元表达式。

### Tool Utilization

```python
tool_usage[ev["tool_id"]] += ev["run_time"]
tool_utils[tid] = tool_usage[tid] / makespan
```

含义：

```text
tool busy time / total simulation time
```

面试解释：

```text
我没有直接在仿真过程中手工算所有指标，而是先生成 event log，再从 event log 按 lot 和 tool 汇总。这种方式更像真实生产系统，MES 也通常先记录 event，再做 KPI aggregation。
```

## 6.13 Step 13 - 瓶颈识别

对应文件：

```text
src/metrics.py
```

核心思路：

```text
bottleneck_score = utilization_norm * 0.4 + queue_time_norm * 0.4 + wip_norm * 0.2
```

对应代码：

```python
score = u_norm[i] * 0.4 + q_norm[i] * 0.4 + w_norm[i] * 0.2
```

为什么不用单纯 utilization：

```text
真实生产瓶颈不只看设备忙不忙，还要看这个设备前面是不是积压了很多 lot，以及平均等待时间是不是很高。utilization 高但没有排队，不一定是最需要改善的位置。
```

当前项目有两个瓶颈视角：

| Field | Meaning | Current Example |
|---|---|---|
| `bottleneck_tool` | 最高利用率 tool | T01 |
| `composite_bottleneck_tool` | 综合 utilization、queue time、WIP 的瓶颈 tool | FIFO baseline 为 T07 |

面试建议说法：

```text
我同时看两个指标：一个是最高利用率 tool，另一个是综合瓶颈分数。产能场景分析优先使用综合瓶颈，因为它更能反映等待时间和拥堵影响。
```

## 6.14 Step 14 - Capacity scenario 怎么实现

对应文件：

```text
src/simulator.py
run_all.py
```

### 场景 1：瓶颈工具 +10% capacity

代码参数：

```python
bottleneck_speedup = {bn_composite: 0.9}
```

含义：

```text
run_time 乘以 0.9，等价于加工时间减少 10%。
```

### 场景 2：瓶颈工具 +20% capacity

```python
bottleneck_speedup = {bn_composite: 0.8}
```

含义：

```text
run_time 乘以 0.8，等价于加工时间减少 20%。
```

### 场景 3：新增并行瓶颈设备

对应代码：

```python
extra_tool_id = f"{extra_tool}_EXTRA"
tool_available[extra_tool_id] = 0.0
```

含义：

```text
为瓶颈 tool 增加一个虚拟平行设备，两台设备可以承担同类 operation。
```

面试解释：

```text
capacity scenario 没有改原始数据，而是在 simulation 参数中控制。如果是 speedup scenario，就减少瓶颈 tool 的 run_time；如果是 parallel tool scenario，就增加一个虚拟 tool，让同一类 operation 可以被原设备或新设备处理。
```

## 6.15 Step 15 - 图表如何生成

对应文件：

```text
src/visualization.py
```

### Gantt chart

使用：

```python
ax.barh(y, duration, left=start)
```

含义：

```text
每个横条表示一道 operation 在某台 tool 上的加工时间。
```

### Rule comparison

使用：

```python
axes[0].bar(rules, makespan)
```

含义：

```text
比较不同派工规则的 makespan、cycle time 和 on-time rate。
```

### Utilization heatmap

使用：

```python
ax.imshow(data, cmap="YlOrRd")
```

含义：

```text
用颜色深浅表示不同 tool 的利用率。
```

### Queue distribution

使用：

```python
ax.hist(queue_times, bins=40)
```

含义：

```text
展示 operation 等待时间分布。
```

### 保存图片

```python
fig.savefig(path, dpi=150)
```

语法解释：

- `savefig()`：把 matplotlib 图保存成 PNG。
- `dpi=150`：控制图片清晰度。

## 6.16 Step 16 - run_all.py 做了什么

对应文件：

```text
run_all.py
```

执行顺序：

1. 读取 `operations.csv` 和 `dim_lot.csv`。
2. 跑 baseline 的 FIFO、SPT、EDD、CR。
3. 根据 FIFO baseline 找 composite bottleneck。
4. 跑 3 个 capacity scenario。
5. 计算 scenario improvement。
6. 保存：
   - `scenario_summary.csv`
   - `simulation_events.csv`
   - `simulation_summary.csv`
7. 生成所有图表。

面试解释：

```text
run_all.py 是项目 pipeline 的入口。它把 parser 后的 processed data 输入 simulator，输出 summary 和图表。这样面试官如果想复现，只需要先运行 parser，再运行 run_all。
```

## 7. 当前结果怎么解释

### 7.1 Baseline rule comparison

当前 baseline 结果：

| Rule | Makespan | Avg Cycle Time | Avg Queue Time | On-Time Rate |
|---|---:|---:|---:|---:|
| FIFO | 82.25 h | 54.89 h | 47.36 h | 100.0% |
| SPT | 118.02 h | 60.54 h | 53.02 h | 100.0% |
| EDD | 119.52 h | 66.78 h | 59.26 h | 100.0% |
| CR | 83.87 h | 62.98 h | 55.46 h | 100.0% |

讲法：

```text
在当前 benchmark 和 release schedule 下，FIFO 反而表现最好。原因是这是多机台固定 route 的 job-shop 系统，局部最优规则比如 SPT 可能会让短工序先走，但不一定减少系统整体拥堵，甚至可能在下游制造排队。
```

### 7.2 为什么所有规则 on-time rate 都是 100%？

讲法：

```text
因为 due date 是 synthetic 的，而且目前设置相对宽松。当前 cycle time 大约是 3 到 5 天，而 due date 大约是 14 天左右，所以所有 lot 都能准时完成。这个结果说明 EDD 和 CR 在当前 due-date 设置下没有被充分区分。下一步我会收紧 due date 或增加 rush order 来测试 due-date driven rule。
```

### 7.3 为什么 FIFO 比 SPT 好？

讲法：

```text
SPT 在单机环境下通常能降低平均 flow time，但在多机 job-shop 里，每个 lot 后面还有不同 route。局部选择最短工序可能导致某些下游 tool 突然拥堵。FIFO 保持了 release 顺序和 route 流动稳定性，所以在这个 benchmark 设置下表现更好。
```

### 7.4 Capacity scenario 结果怎么讲

重点讲：

```text
新增并行瓶颈设备对 FIFO 的改善最大，平均 cycle time 下降 9.4%，queue time 下降 10.9%。这说明在当前系统里，单纯换 dispatch rule 的效果有限，真正的改善来自瓶颈产能扩充。
```

## 8. 面试常见问题和回答

### Q1: 你为什么选择 job-shop benchmark 来模拟 fab？

回答：

```text
真实 fab MES 数据通常不可公开，所以我使用 job-shop scheduling benchmark 作为可复现的数据源。fab 和 job-shop 在抽象层面有相似性：lot 按固定 route 经过多台 tool，每台 tool 同时只能处理有限任务，排队和瓶颈会影响 cycle time。这个映射不能覆盖真实 fab 的所有复杂规则，但足够展示生产调度、产能建模和 bottleneck analysis 的思路。
```

### Q2: 这个项目和真实 fab 有什么差距？

回答：

```text
当前模型没有考虑 batching、rework、tool downtime、preventive maintenance、setup time、recipe qualification 和 stochastic variability。这些是真实 fab 中很重要的因素。我把这些写在 limitation 里，因为这个项目重点是展示 capacity simulation 和 dispatching rule comparison 的核心思路，而不是直接部署到真实 fab。
```

### Q3: 离散事件仿真是什么？

回答：

```text
离散事件仿真是用事件推进系统状态的方法。这个项目中的事件就是 operation start 和 operation end。每次调度一道 operation，我都会更新 tool_available、lot_ready 和 next_op_idx。系统不是每分钟都模拟，而是在 operation 完成、tool 可用、lot ready 这些离散时间点更新。
```

### Q4: 你的仿真状态变量有哪些？

回答：

```text
主要有三个状态变量：tool_available 记录每台设备什么时候可用，lot_ready 记录每个 lot 什么时候可以进入下一道工序，next_op_idx 记录每个 lot 当前加工到第几道 operation。这三个状态决定下一轮哪些 operation 可以进入 ready queue。
```

### Q5: Critical Ratio 是怎么算的？

回答：

```text
Critical Ratio = (due date - current time) / remaining processing time。值越小表示越紧急，如果小于 1，说明按照剩余加工时间估算可能已经有延期风险。代码里我对每个 ready operation 计算它所在 lot 的 CR，然后选择 CR 最小的 operation。
```

### Q6: 你怎么计算 queue time？

回答：

```text
queue_start_time 是 lot 完成上一道工序后可以进入当前 tool 队列的时间。start_time 是它真正开始加工的时间。因此 queue_time = start_time - queue_start_time。
```

### Q7: 你怎么识别 bottleneck？

回答：

```text
我用了两个视角。第一是最高 utilization tool，也就是 busy time / makespan 最大的设备。第二是 composite bottleneck score，把 utilization、average queue time 和 WIP count 标准化后加权，权重是 0.4、0.4、0.2。产能扩充场景使用 composite bottleneck，因为它更能反映等待和拥堵。
```

### Q8: 为什么不直接做最优调度？

回答：

```text
最优 job-shop scheduling 通常是 NP-hard 问题，真实 fab 规模更大，还存在很多约束。这个项目先用 dispatching rule 和 what-if simulation 做决策支持，更贴近生产现场常用的快速评估方式。如果继续扩展，可以加入 MILP、CP-SAT 或 heuristic optimization。
```

### Q9: 你怎么验证模型结果？

回答：

```text
我做了几类验证。第一，检查 operations.csv 的行数是否等于五个 benchmark 实例总 operation 数，也就是 1,100。第二，baseline 跑四种规则，所以 simulation_events.csv 应该有 4,400 行。第三，每个 scenario 和 rule 都要有 summary，baseline 加三个 capacity scenario，一共 4 个 scenario 乘 4 个 rule，所以 scenario_summary.csv 应该有 16 行。第四，我用 Gantt chart 和 utilization heatmap 检查调度结果是否合理。
```

### Q10: 如果面试官问你最想改进什么？

回答：

```text
我会优先做三件事。第一，收紧 due date 或加入 rush lots，让 EDD 和 CR 的差异更明显。第二，加入 stochastic processing time 和 tool downtime，让模型更接近真实 fab。第三，加入 setup time、batching 和 tool qualification，进一步提升模型真实性。
```

## 9. Python 语法速查

### 9.1 函数定义

```python
def run_simulation(operations, lot_data, rule_name="FIFO"):
    ...
    return events, summary
```

解释：

- `def` 定义函数。
- 括号里是参数。
- `rule_name="FIFO"` 是默认参数。
- `return` 返回结果。

### 9.2 类型提示

```python
def run_all_rules(rule_names: list[str] | None = None) -> tuple[dict[str, list[dict]], list[dict]]:
```

解释：

- `list[str]` 表示字符串列表。
- `| None` 表示可以是 None。
- `->` 后面表示函数返回值类型。

面试可以说：

```text
类型提示不影响运行，但可以提高代码可读性，方便别人知道输入输出结构。
```

### 9.3 字典

```python
lot_info[lot_id] = {
    "release_ts_hours": release_h,
    "due_ts_hours": due_h,
    "total_remaining_run_time": total_run,
}
```

解释：

- dict 用 key-value 存储结构化信息。
- 本项目大量使用 dict 表示一行 operation 或一个 lot 的属性。

### 9.4 列表推导式

```python
lines = [line.strip() for line in f if line.strip()]
```

解释：

- 一行代码完成遍历、清洗和过滤。

### 9.5 lambda

```python
ops.sort(key=lambda x: x["operation_seq"])
```

解释：

- `lambda` 是匿名函数。
- 常用于 `sort`、`min`、`max` 的 key。

### 9.6 defaultdict

```python
from collections import defaultdict
lot_ops = defaultdict(list)
```

解释：

- 普通 dict 如果 key 不存在会报错。
- `defaultdict(list)` 遇到新 key 会自动创建空 list。

### 9.7 CSV 读写

读取：

```python
for r in csv.DictReader(f):
    rows.append(r)
```

写入：

```python
writer = csv.DictWriter(f, fieldnames=fieldnames)
writer.writeheader()
writer.writerows(rows)
```

解释：

- `DictReader` 把 CSV 行读成 dict。
- `DictWriter` 把 dict 写成 CSV 行。

### 9.8 f-string

```python
lot_id = f"L{lot_counter:04d}"
tool_id = f"T{machine_id:02d}"
```

解释：

- `04d` 表示整数补零到 4 位，例如 `1 -> 0001`。
- `02d` 表示整数补零到 2 位，例如 `4 -> 04`。

### 9.9 三元表达式

```python
on_time = 1 if finish_h <= due_h else 0
```

解释：

- 条件成立返回 1，否则返回 0。

### 9.10 字典函数注册表

```python
RULES = {
    "FIFO": fifo,
    "SPT": spt,
}
rule_fn = RULES.get(rule_name, RULES["FIFO"])
selected = rule_fn(queue, current_time, lot_info)
```

解释：

- Python 里函数可以作为 dict 的 value。
- 这样可以根据字符串动态选择逻辑。

## 10. 面试展示路线

如果面试时可以展示屏幕，建议按这个顺序：

### 第一步：打开 README

讲：

```text
这是项目背景、数据来源、业务假设和核心结果。
```

重点展示：

- Data Source
- Fab-like Data Mapping
- Dispatching Rules
- Results and Findings
- Recommendations

### 第二步：打开 `outputs/figures`

展示：

- `gantt_fifo.png`
- `rule_comparison.png`
- `utilization_heatmap_fifo.png`
- `bottleneck_ranking.png`
- `queue_distribution_fifo.png`
- `scenario_improvement_waterfall.png`

讲：

```text
这些图分别对应调度过程、规则对比、设备利用率、瓶颈识别、排队时间分布和产能改善。
```

### 第三步：打开 `src/simulator.py`

重点讲：

- `run_simulation()`
- `tool_available`
- `lot_ready`
- `next_op_idx`
- `start_time = max(...)`
- event log

### 第四步：打开 `src/dispatch_rules.py`

重点讲：

- FIFO 用 `queue_start_time`
- SPT 用 `run_time`
- EDD 用 `due_ts_hours`
- CR 用 `(due - current_time) / remaining`
- `RULES` 字典注册表

### 第五步：打开 `run_all.py`

讲：

```text
这个文件是一键 pipeline，负责跑 baseline、capacity scenario、保存结果和生成图表。
```

## 11. 当前版本剩余修正建议

### 11.1 必做：配置可复现 Python 环境

当前环境中：

```text
python --version
py --version
```

不可用。

建议安装 Python 并配置 PATH，然后运行：

```powershell
python -m pip install -r requirements.txt
python src/parser.py
python run_all.py
```

### 11.2 必做：建立真实 Git 仓库

当前目录有 `.git` 文件夹，但 `git status` 仍提示不是 repository。

建议重新初始化：

```powershell
git init
git add .
git commit -m "Complete fab capacity simulation portfolio project"
```

如果要上传 GitHub，再添加 remote。

### 11.3 建议修正：`simulator.py` composite score 索引顺序

当前 `simulator.py` 中 composite bottleneck 的计算建议保持 tool 顺序一致。

建议写法：

```python
tools_sorted = sorted(unique_tools)
util_vals = [tool_utils[t] for t in tools_sorted]
queue_vals = [tool_queue_sum[t] / max(tool_wip_count[t], 1) for t in tools_sorted]
wip_vals = [tool_wip_count[t] for t in tools_sorted]

u_n, q_n, w_n = _norm(util_vals), _norm(queue_vals), _norm(wip_vals)

comp_scores = {}
for i, t in enumerate(tools_sorted):
    comp_scores[t] = u_n[i] * 0.4 + q_n[i] * 0.4 + w_n[i] * 0.2
```

这不会改变项目主线，但能让 summary 字段更严谨。

### 11.4 建议修正：README 中 Git 技术栈

如果暂时不初始化 Git，README 里的 `Version Control | Git` 可以保留为计划项，但最好实际初始化仓库后再展示。

## 12. 最终面试定位

你要把这个项目定位成：

```text
一个生产物流和制造调度方向的 Python 决策支持项目。
```

而不是：

```text
一个完美的真实晶圆厂调度系统。
```

最稳妥的表达：

```text
This is a fab-like capacity simulation project built on public job-shop benchmark data. It demonstrates my ability to translate manufacturing operations into a simulation model, implement dispatching rules, calculate production KPIs, identify bottlenecks, and evaluate capacity improvement scenarios.
```

中文表达：

```text
这个项目不是直接复刻真实 fab，而是用公开 benchmark 构建一个 fab-like 生产系统，用来展示我把制造物流问题转化成 Python 仿真模型、比较派工规则、识别瓶颈并评估产能改善方案的能力。
```

## 13. 你需要记住的 8 个核心点

面试前至少记住这 8 点：

1. 数据来源是公开 job-shop benchmark，不是真实 fab MES。
2. job 映射为 lot，machine 映射为 tool，operation 映射为 process step。
3. 仿真核心状态是 `tool_available`、`lot_ready`、`next_op_idx`。
4. operation 开始时间是 `max(lot_ready_time, tool_available_time)`。
5. FIFO、SPT、EDD、CR 都是通过 `min(..., key=...)` 或自定义 key 函数实现。
6. KPI 都从 event log 汇总出来，不是手工硬编码。
7. 当前结果中 FIFO 表现最好，所有规则 on-time rate 都是 100%，原因是 due date 设置较宽松。
8. 产能场景说明新增并行瓶颈设备比单纯换派工规则更能降低 queue time 和 cycle time。

如果能讲清楚这 8 点，这个项目在面试中就基本站得住。
