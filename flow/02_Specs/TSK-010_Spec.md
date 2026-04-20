# 📑 AOS Spec: Single-Instruction Vector Compression (V1.0)

## 1. 硬件级循环折叠 (Hardware Loop Folding)

本规约定义了如何将 `a[0-9]*c + b[0-9]` 压缩至单条微指令逻辑空间内。

| 字段 | 逻辑映射 | 物理作用 |
| :--- | :--- | :--- |
| **MACRO_VMA** | 宏向量 FMA | 编译器输出一条“宏指令”，硬件内部通过微码状态机循环 10 次。 |
| **DLY_ALIGNED** | 时延对齐 | 利用 `DLY` 字段补偿 MUL 单元的 4 周期时序，无需显式 DLY 指令。 |
| **AUTO_INC** | 自动步进 | 利用 `INC` 和 `INC_EMBED` 在 10 次迭代中自动寻址 `a[i]` 和 `b[i]`。 |

## 2. 调度约束 (Scheduling Constraints)
- **$II=1$**: 宏指令在 SMC 发射队列中占用的有效 slot 必须为 1。
- **Physical Dependency**: `R_A -> MUL`, `R_B -> ADD`, `MUL -> ADD` 所有的时序偏移全部由 `DLY` 位域承载。

---
**Status: ACTIVE** | **AOS V3.5-GOVERN**
