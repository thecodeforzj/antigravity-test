---
aos_stage: "P1"
mission_id: "SMT-SCHEDULER-01"
status: "DRAFT"
inputs_referenced: ["flow/00_Mission_Control/Current_Mission.md"]
---
# 💠 Mission Decomposition: SMT-Scheduler-Modulo (AAA Standard)

## 1. 核心目标 (Core Mission)
实现支持 Modulo Scheduling 的 SMT 调度器，支持硬件流水循环配置输出。

## 2. 任务矩阵 (Task DAG)

### Milestone A: 约束建模内核 [CORE]
- [ ] **TSK-001**: 实现 `Modulo_Resource_Constraint` 逻辑。
    - *AC*: 在 $II=N$ 时，检查 $\forall \tau \in [0, N-1]$ 的资源占用总和。
- [ ] **TSK-002**: 实现 `Modulo_Dependency_RAW` 逻辑（支持跨迭代依赖）。
    - *AC*: 支持 $T_j + k \times II \ge T_i + L_i$ 的参数化表示。
- [ ] **TSK-003**: 构建 `Modulo_Bank_Conflict_Matrix`。
    - *AC*: 即使是不同迭代的指令，落在同一个 Modulo Cycle 时也必须访问不同 Bank。

### Milestone B: 硬件指令 DSL [DSL]
- [ ] **TSK-004**: 定义 Horner 展开的抽象指令流 (Read, Mul, Add, Write)。
- [ ] **TSK-005**: 编写 `DSL_Parser`，将抽象指令转化为 Z3 变量。

### Milestone C: 配置器与可视化 [CONFIG]
- [ ] **TSK-006**: 实现从 Solver 结果到 `{embed, loop, inc, dely}` 的转换算法。
- [ ] **TSK-007**: 输出 Gantt Chart 分解图（展示单次迭代与流水线重叠态）。

## 3. 自我反思 (Agent Self-Critique)
- **Q**: `rtovr` 的脉冲逻辑在 Modulo Scheduling 中如何处理？
- **A**: `rtovr` 需被视为一个独占的 Modulo 资源，且必须与消费者指令保持固定的相对偏移（$T-1$）。
