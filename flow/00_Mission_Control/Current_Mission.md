---
project_name: "SMT-Scheduler-Modulo"
creation_date: 2026-04-19
status: "IDEATION"
aos_stage: "P0"
mission_id: "SMT-MODULO-001"

# --- 💠 AOS Adaptive DNA [NEW] ---
rigor_level: "CRITICAL"      # 启用安全审计与物理约束强制对齐
complexity: "HIGH"          # 触发分块处理与深度上下文加载
verification: "FORMAL"      # 强制执行 SMT 符号验证
sync_mode: "SUBMODULE-HUB"  # 强制执行双重 Git 提交流程
---

# 🚩 使命目标 (Mission Objective)

> 目标：构建支持纵向流水线 (Modulo Scheduling) 的高保真 SMT 指令调度器。

## 初始愿景 (Vision)
- **V1 (Correctness)**: 100% 遵守硬件物理约束（Latencies, Resource, Bank, Crossbar）。
- **V2 (Efficiency)**: 实现最优的 II (Initiation Interval) 寻找算法。
- **V3 (Decoupling)**: 调度算法与硬件规格描述 (Hardware Manifest) 完全解耦。

## 非功能性需求
- **Performance**: 支持 1000 条指令量级的 SMT 求解在 10s 内完成。
- **Verification**: 实现 100% 功能覆盖率与代码覆盖率。

## 🔐 真理指纹库
- DNA-Fingerprint: MADD_Spec|82668b7e445d1fec8ffa826fc6cd06b46a0f2584a9fd83db2a24d5b315e37adb (AOS Truth Fingerprints)
- DNA-Fingerprint: Hardware_Manifest|ab3d6dc6eb129a578a9d6dd9d8ecd8cda329c08085c6888eb69e07973e65d986
- DNA-Fingerprint: AOS_Rules|f2486e45fad833ddd9efc03c5b8aeb41beca6bf1763f4251b47362f5ba7eac04
- DNA-Fingerprint: SMT_Scheduler_Detailed_Specs|5eb980392082a2772b6e7e84ef5e9e797a0a31772c26418b572dbc252b5f5e2a

## 📅 AOS 阶段性路线图 (V-Model)
1. **P1 (Ideation)**: 算法可行性分析与 Z3 建模。
2. **P2 (Specs)**: 固化硬件清单与时序规格。
3. **P3 (Develop)**: 实现求解器核心逻辑。
4. **P4 (Verify)**: 全量 Benchmark 验证。

## 🎯 当前正在执行的任务 (Active Tasks)
- [x] **Task-001**: 构建基础流水线环境并验证 Paging 加载机制 [COMPLETED]
- [x] **Task-002**: 核心 SMT 建模（Modulo & Bank Constraints） [COMPLETED]
