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

### C4: RT-OVR Port Tying (端口强绑定约束)
`rtovr` 的输入端口编号必须与其对应的 Crossbar 输入端口索引对齐。在 SMT 建模中，必须建立映射关系：
- `rtovr_index` -> `tied_to_input_port_index`

### C5: Loop Engine Controls (循环引擎控制)
最终生成的调度序列必须能映射到硬件控制器属性：
- `addr_inc`: 每轮递归的地址增量。
- `initiation_interval_dely`: 模周期间隔周期。

## 2. 验收标准 (Acceptance Criteria - 100/100 Mandatory)

- **[AC-MOD-01]**: 周期与资源约束验证（含 fpadd/fpmul 1x1 限制）。
- **[AC-MOD-02]**: 验证 `ur_read/write` 在同 Bank 冲突下的调度拦截。
- **[AC-MOD-03]**: 100% 测试覆盖率。
- **[AC-MOD-04]**: **[针对 RT-OVR]** 验证生成的指令流中，`rtovr` 的配置能够正确反映输入端口的绑定索引。
- **[AC-MOD-05]**: **[针对 Loop Engine]** 验证调度器输出的 `initiation_interval_dely` 等于求解出的最小 II。

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
