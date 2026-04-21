---
aos_stage: "P2"
mission_id: "SMT-REF-004"
parent_arch: "01_Root_ADD/SMT_System_ADD.md"
status: "STABLE"
---

# 📑 物理时序审计详细设计 (Physical Auditor SDD)

## 1. 标准输出：时序追踪文件 (Timing Trace Standard)
编译器必须同步产出 `Timing_Trace.json`。格式如下：
```json
{
  "cycle_0": {"units": {"FPADD": ["INST_A", "loop_cnt=0"], "FPMUL": "IDLE"}},
  "cycle_1": {"units": {"FPADD": ["INST_A", "loop_cnt=1"], "FPMUL": "IDLE"}},
  ...
}
```
该文件必须保留 100% 展开后的物理痕迹。

## 2. 反向审计算法 (Reverse Audit Algorithm)
物理审计模块必须是一个**无状态 (Stateless)** 的独立程序：
- **Input**: `Binary_HEX` + `Hardware_Manifest`。
- **Process**:
  1. **Disassembly**: 解析 41-bit Header，提取 VLD, DLY, LOOPS, INC。
  2. **Path Selection (RTOVR Strobe)**: 解析 `RTOVR` 选通位。验证“短路路径”是否在数据到达的精确时钟周期内有效。
  3. **Data Continuity (Bypass Check)**: 允许计算结果不经过 `UR_WRITE` 写入 Bank，但必须证明该结果被下游 `RTOVR` 选通并消费，否则判定为“无效死代码 (Dead Code)”。
  4. **Verification**: 
     - 检查同一时刻是否有两个逻辑占用同一个物理单元。
     - 检查 INC 是否越界。
- **Goal**: 如果审计报告与编译器的 Trace 不一致，立即判定编译失败（Adversarial Proof）。

## 3. 验收先知 (Oracle)
- **输入**: 一个被恶意修改了某个 Bit 的故障 HEX。
- **预期**: Auditor 必须精准定位并报错：`ERROR: Resource Collision at Cycle X, Unit Y`。

---
**Standard: AOS Adversarial Physical Auditing V4.0**
