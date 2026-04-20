# 📑 AOS Spec: Vector-FMA Stress & PseudoCodeGen (V1.1)

## 1. 算子拓扑 (Vector-FMA Topology)

本规约定义了 `Y[i] = A[i] * C + B[i]` 在 `aiacc_smt_engine_v2` 上的全流水物理路径。

| 字段 | 逻辑映射 | 对齐要求 |
| :--- | :--- | :--- |
| **VECTOR_LEN** | 向量长度 = 10 | 必须使用 `LOOPS=9` 字段进行硬件级折叠。 |
| **FMA_CHIAIN** | MUL -> ADD 级联 | 验证 `FPMUL` (Lat=4) 与 `FPADD` (Lat=1) 之间的影子寄存器 (DLY) 补偿。 |
| **SCALAR_REUSE** | 标量 C 复用 | 模拟标量 `C` 只读取一次并参与 10 次乘法。 |
| **PSEUDO_GEN** | 伪指令生成 | 对每个单元产出包含位 field 的指令描述。 |

## 2. 硬件单元参数 (Real-HW Trace)
- **FPMUL**: Latency=4, Capacity=1.
- **FPADD**: Latency=1, Capacity=1.
- **UR_READ**: Read Port=4, Banks=8.

---
**Status: PROPOSED** | **AOS V3.5-RIGOR**
