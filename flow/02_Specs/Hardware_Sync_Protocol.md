---
aos_stage: "P2"
mission_id: "PORT-SYNC-2026"
status: "FROZEN"
---

# 📑 Protocol: Port-Unit Synchronous Consumption

## 1. 物理拓扑假设 (Topology Assumption)
- **读取绑定**：物理单元 `ur_read_i` 的数据输出，**仅且只能** 通过跨栏（Crossbar）的 `rtovr_i` 端口被受体（FPADD/FPMUL）取走 ($i \in [0, 3]$)。
- **写回绑定**：物理单元 `ur_write_i` 的选通，对应 `rtovr_{4+i}` 端口。

## 2. 严谨性物理 AC (Acceptance Criteria)
- **[AC-PHYS-01] 零延迟同步**：所有 `ur_read` 产出的数据，其受体的 `rtovr` 脉冲发射时刻 $T_{pulse}$ 必须 **严格等于** 指令准备就绪时刻 $T_{ready}$。
  - 公式：$T_{pulse} = T_{parent\_read} + 1$。
- **[AC-PHYS-02] 物理实例锁定**：指令被分配到物理实例 `n` 时，其对冲端口索引必须为 `n`。

## 3. 审计准则
- 只有满足 `[AC-PHYS-01]` 和 `[AC-PHYS-02]` 的时序序列才被视为“物理合法”。
