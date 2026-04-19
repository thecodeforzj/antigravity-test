---
aos_stage: "P1"
mission_id: "SMT-MODULO-001"
status: "DRAFT"
inputs_referenced: ["flow/00_Mission_Control/Current_Mission.md"]
---

# 💠 SMT Modulo Scheduler: 深度拆解 (P1)

## 1. 需求溯源矩阵 (RTM)

| 原始愿景 (Vision) | 任务 ID | 任务描述 | 验证标准 (MECE Check) |
| :--- | :--- | :--- | :--- |
| **V1 (Correctness)** | **TSK-MOD-001** | 周期约束建模 (Latency & Resource) | 覆盖所有的 FPAdd, FPMul 延迟。 |
| **V1 (Correctness)** | **TSK-MOD-002** | 模周期 Banks 冲突建模 (Bank Matrix) | 确保 Modulo Cycle 下无冲突。 |
| **V2 (Efficiency)** | **TSK-MOD-003** | 指令顺序依赖建模 (RAW/WAR/WAW) | 支持跨迭代依赖 (Cross-iter dep)。 |
| **V2 (Efficiency)** | **TSK-MOD-004** | II (Initiation Interval) 寻找算法 | 自动搜索最小有效 II。 |
| **V3 (Decoupling)** | **TSK-MOD-005** | 硬件规格描述文件适配器 | 动态载入 hardware_spec.json。 |

## 2. 限界上下文 (Bounded Contexts)
我们将整个系统拆解为以下解耦模块，防止重构灾难：
1. **Solver Interface**: 负责与 SMT (Z3) 交互，屏蔽具体求解逻辑。
2. **Hardware Logic**: 专门处理物理约束（Latency/Resource/Bank）。
3. **Graph Engine**: 处理指令流的拓扑排序与依赖关系。
4. **Modulo Packager**: 负责最终结果的模转换与可视化。

## 3. 完备性审计 (MECE Check)
- [x] **正常流**: 包含所有算子调度。
- [x] **异常流**: 包含 II 无法求解时的报错逻辑。
- [x] **性能边界**: 验证大规模 DSL 解析性能。
- [x] **非目标**: 不处理运行时动态分发逻辑 (OutOfOrder)，仅限静态调度。
