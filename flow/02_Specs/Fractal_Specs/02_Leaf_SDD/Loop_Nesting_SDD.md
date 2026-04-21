---
aos_stage: "P2"
mission_id: "SMT-REF-003"
parent_arch: "01_Root_ADD/SMT_System_ADD.md"
status: "STABLE"
---

# 📑 嵌套循环与指令压缩详细设计 (Loop & Compression SDD) - V4.4 并行脉冲版

## 1. 物理步进逻辑 (Shared INC)
（保持 V4.3 共享 INC 逻辑不变...）

## 2. 并行脉冲压缩 (Parallel Pulse Compression)
基于 `AX_04`，当指令包包含多个活跃单元时，压缩必须遵循以下逻辑：

- **VLIW 发射**: 包内所有 `vld=1` 的单元在 $T_{start}$ 时刻同时触发。
- **DLY (Launch Interval)**:
  - 角色：它不是单纯的等待，而是 **管道推进节拍**。
  - 公式：$Delay\_Line\_Move(i) \Leftrightarrow Cycle\_Count \% DLY == 0$。
- **LOOPS 与 DLY 的协同**:
  - 若 `LOOPS=19, DLY=1`：连续 20 拍，每一拍都平行发射所有的 `vld=1` 单元。
  - 若 `LOOPS=19, DLY=4`：每隔 4 拍，平行发射一次。

## 3. 验收先知 (Oracle)
- **输入**: 同时执行 `add(a[0-19])` 和 `mul(b[0-19])`。
- **预期**: 
  - **合并解**: 产生 **1条** VLIW 指令，其中 FPADD 和 FPMUL 的 `vld` 均为 1。
  - **字段控制**: `LOOPS=19, DLY=1, INC=1`。
  - **物理含义**: 硬件每一拍都同时执行一次 ADD 和一次 MUL。

---
**Verified by Antigravity AI (Parallelism Refinement: 2026-04-21)**
