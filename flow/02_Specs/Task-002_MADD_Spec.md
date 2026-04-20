---
type: "Loop-Kernel-Spec"
task_id: "SMT-MODULO-002"
formula: "out[i] = a[i] * c + b[i]"
mode: "Modulo_Scheduling_Kernel"
ii_target: 1
---

# 📑 Task-002: 乘加循环内核 (MADD Loop Kernel)

## 1. 内核语义 (Kernel Semantics)
单次循环迭代 (Iteration $i$) 包含：
- **OP_MUL**: $tmp = a[i] * c$. (FU: `fpmul`, Latency: 4)
- **OP_ADD**: $out[i] = tmp + b[i]$. (FU: `fpadd`, Latency: 4)

## 2. 流水线目标 (Pipeline Goal)
- **Initiation Interval (II)**: 目标 II = 1。
- **并发度**: 在稳定状态下，流水线中应同时存在 8 个活跃指令（4 个 MULs 和 4 个 ADDs 在不同相位）。

## 3. 物理线索 (Physical Trace)
- **Cycle 0**: 启动 Iteration 0 的 MUL。
- **Cycle 1**: 启动 Iteration 1 的 MUL。
- ...
- **Cycle 4**: Iteration 0 的 MUL 结束 -> 启动 Iteration 0 的 ADD。
- **Cycle 5**: Iteration 1 的 MUL 结束 -> 启动 Iteration 1 的 ADD。

## 4. 验证红线
- 严禁出现单元碰撞 (Unit Collision)。
- 严禁出现数据写后读 (RAW) 冲突。
