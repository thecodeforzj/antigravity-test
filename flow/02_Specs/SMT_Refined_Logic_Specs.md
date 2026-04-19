---
aos_stage: "P2"
mission_id: "SMT-REFINE-001"
status: "FROZEN"
task_refs: ["TSK-REF-001", "TSK-REF-002", "TSK-REF-003", "TSK-REF-004"]
---

# 💠 Spec: SMT Refined Hardware Logic (Zero-Buffer/No-FIFO)

## 1. 寄存器覆盖约束 (Overwrite Constraint)
由于硬件单元输出寄存器无 FIFO，数据生命周期必须受到严格限制：
- **生命周期定义**: 指令 $I_p$ 的结果在 $T_{ready} = T_{start\_p} + Lat_p$ 产生。
- **强制消费原则**: 若该物理单元在 $T_{next}$ 执行下一条指令，则 $I_p$ 的结果必须在 $[T_{ready}, T_{next} + Lat - 1]$ 之间被取走。
- **全流水线特例**: 若单元为全流水（$II=1$），则数据可用窗口仅为 **1 拍**。

## 2. 选通脉冲对齐 (rtovr Alignment)
- **Pulse-Edge Coupling**: 选通脉冲 `rtovr` 必须在数据到达端口的**同一拍**发生。
- **约束公式**: $T_{rtovr} = T_{producer} + Lat_{producer}$。
- **Consumer Start**: 指令 $I_{consumer}$ 在选通后的下一拍开始。即 $T_{consumer} = T_{rtovr} + 1$。

## 3. 结果对齐验证指标 (100/100 ACs)
- **[AC-REF-01]**: 验证 `ur_read_0` 在 $T=0, 1, 2$ 连续工作时，对应的 `rtovr` 必须在 $T=1, 2, 3$ 准时出现，否则报解失败。
- **[AC-REF-02]**: 禁用任何形式的数据在 Crossbar 上的长期停留。
- **[AC-REF-03]**: 可视化图表必须 100% 还原物理单元索引。

## 4. 溯源追踪
- TSK-REF-004 -> Sec 1 (Overwrite)
- TSK-REF-001 -> Sec 2 (Alignment)
