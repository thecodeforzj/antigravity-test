---
aos_stage: "P2"
mission_id: "SMT-SPEEDUP-001"
task_refs: ["TSK-REFINE-01", "TSK-REFINE-02"]
status: "FROZEN"
---

# 🚀 Spec: SMT Throughput Optimization (Full Capacity)

## 1. 数据布局策略 (Data Layout)
- 为规避 Bank 模数冲突，指令中的 `bank_id` 必须根据算法的数据流进行 **Striping（条带化）** 分布。
- 目标：将单一 Bank 的平均访问频率压降至 $1/II$ 以下。

## 2. 调度目标对齐 (Performance ACs)
- **[AC-SPEED-01]**：Taylor2 链条在 $II \le 2$ 下必须成功生成合规时序。
- **[AC-SPEED-02]**：验证计算单元的 **Duty Cycle（占空比）** 达到 100%（在 $II=2$ 时，单加法器/单乘法器无空闲）。

## 3. 物理规则维持
- 继续强制执行 **No-FIFO** 瞬时消费。
- 继续强制执行 **Instance-Aware** 1:1 选通。
