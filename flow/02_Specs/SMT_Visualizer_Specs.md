---
aos_stage: "P2"
mission_id: "SMT-MODULO-001"
status: "FROZEN"
inputs_referenced: ["flow/01_Ideation_Threads/SMT_Modulo_Decomp_v2.md", "app/smt_modulo_core.py"]
---

# 💠 Spec: SMT Configurator & Visualization (Milestone C)

## 1. 硬件配置映射 (Hardware Mapping)
调度器输出必须包含以下核心控制字段：
- **initiation_interval_dely**: 等于求解出的最小 II。
- **loop_count**: 目标迭代次数。
- **addr_inc**: 内存指令相对于 base 指针的偏移。
- **embed_bundle**: 包含每拍指令发射掩码的二进制或 Hex 序列。

## 2. 流水线 Gantt 图定义
可视化工具必须输出两种视图：
1. **Single-Iteration View**: 展示单次循环内指令的时序关系。
2. **Modulo-Overlapped View**: 展示在流水线进入 Steady-State（稳态）后，同一物理周期内不同迭代阶段的指令重叠情况。

## 3. 验收标准 (Acceptance Criteria - 100/100)
- **[AC-VIS-01]**: 验证生成的 `dely` 字段与 SMT Solver 输出的 `ii` 完全一致。
- **[AC-VIS-02]**: Gantt 图必须能够清晰标识出每条指令所在的 **Stage**（由 $T_i // II$ 决定）。
- **[AC-VIS-03]**: 100% 代码覆盖率审计。

## 4. 需求溯源
- TSK-MOD-006 -> AC-VIS-01, 02
- TSK-MOD-007 -> AC-VIS-02
