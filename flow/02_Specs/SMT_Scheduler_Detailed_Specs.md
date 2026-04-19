# 💠 P2 Specifications: SMT Scheduler Detailed Contract

## 1. 约束模型定义 (SMT Logic Model)

### 1.1 基础变量 (Variables)
对于指令集 $I = \{i_0, i_1, \dots, i_n\}$，定义：
- $T_i$: 指令 $i$ 的发射周期 (Integer).
- $L_i$: 指令 $i$ 的执行延迟 (Constants: fpadd=4, fpmul=4, ur=1).
- $R_i$: 指令 $i$ 使用的硬件资源类型.

### 1.2 核心约束 (Modulo Constraints)
1.  **数据依赖 (RAW)**:
    - 循环内依赖: 如果指令 $j$ 依赖同一迭代中的 $i$，则 $T_j \ge T_i + L_i$。
    - 跨迭代依赖 (Recurrence): 如果指令 $j$ 依赖前 $k$ 次迭代的 $i$，则 $T_j + k \times II \ge T_i + L_i$。
2.  **Modulo 结构冲突 (Modulo Resource Hazards)**:
    - 对于任何资源 $R$，其在周期 $\tau \in [0, II-1]$ 的使用总量不得超过限制。
    - $\forall \tau \in [0, II-1], count(i | i.resource = R \text{ 且 } T_i \pmod{II} = \tau) \le Resource\_Count(R)$。
3.  **Bank 冲突 (Modulo Memory Hazards)**:
    - $\forall \tau \in [0, II-1]$，在 Modulo 周期 $\tau$ 内的所有读写操作访问的 Bank 必须满足硬件并发规则。
4.  **硬件配置映射**:
    - 最终输出必须生成具象的 `{embed, loop, inc, dely}` 字段值，其中 `dely` 映射为求解出的最优 $II$。

## 2. 验收标准 (Acceptance Criteria - AC)

- **AC-1 (Correctness)**: 基于 Modulo $II$ 的资源分布无冲突。
- **AC-2 (Optimality)**: 求解结果必须使 $II$ 最小化。
- **AC-3 (Hardware Tracking)**: $inc$ 字段需正确描述指针在迭代间的位移。

## 3. 标准测试用例 (Benchmark)

```yaml
Instructions:
  - id: instr0, type: ur_read, bank: 0, addr: 0x01
  - id: instr1, type: ur_read, bank: 1, addr: 0x02
  - id: instr2, type: ur_read, bank: 0, addr: 0x03 # Potential conflict if same cycle
  - id: instr3, type: fpadd, inputs: [instr0, instr1]
  - id: instr4, type: fpmul, inputs: [instr2, instr3]
  - id: instr5, type: ur_write, bank: 2, addr: 0x04, source: instr4
```

## 4. 任务分解 (P3 Execution)
1.  [ ] 构建 `app/core/solver.py`: 封装 Z3 求解逻辑。
2.  [ ] 构建 `app/core/hardware.py`: 加载 `Hardware_Manifest.json`。
3.  [ ] 构建 `app/main.py`: 驱动程序及结果可视化。
