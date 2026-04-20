---
project_name: "SMT-Scheduler-Modulo"
creation_date: 2026-04-19
status: "DEVELOPMENT"
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
- **V1 (Correctness)**: 100% 遵守硬件物理约束。
- **V2 (Efficiency)**: 实现最优的 II 寻找算法。
- **V3 (Decoupling)**: 调度算法与硬件规格说明完全解耦。

## 🔐 真理指纹库
- DNA-Fingerprint: MADD_Spec|82668b7e445d1fec8ffa826fc6cd06b46a0f2584a9fd83db2a24d5b315e37adb
- DNA-Fingerprint: Taylor4_Logic|Verified (II=4)
- DNA-Fingerprint: Operator_Deployment_SOP|V1.0
- DNA-Fingerprint: AOS_Rules|f2486e45fad833ddd9efc03c5b8aeb41beca6bf1763f4251b47362f5ba7eac04
- DNA-Fingerprint: Hardware_Manifest|f6f65cc55251dbc99cef9046f67dff8440528a18071fcaec25d899868179608c

## 📅 AOS 阶段性路线图 (V-Model)
1. **P1 (Ideation)**: 算法可行性分析与 Z3 建模。
2. **P2 (Specs)**: 固化硬件清单与时序规格。
3. **P3 (Develop)**: 实现求解器核心逻辑。
4. **P4 (Verify)**: 全量 Benchmark 验证。

## 🎯 当前正在执行的任务 (Active Tasks)
- [x] **Task-001**: 构建基础流水线环境并验证 Paging 加载机制 [COMPLETED]
- [x] **Task-002**: 核心 SMT 建模（Modulo & Bank Constraints） [COMPLETED]
- [x] **Task-003**: 建立工业边界控制协议 (SMT/Hard-Rigor) [COMPLETED]
- [x] **Task-004**: 泰勒 4 阶流水线验证 (回归原生流程) [COMPLETED]
- [x] **Task-005**: 仓库代码与文档深度清理 (Sanitization) [COMPLETED]
- [ ] **Task-006**: 硬件指令压缩与多层嵌套循环建模 (Compression) [RESUMED]
- [x] **Task-007**: 体系化流程硬化与三权分立脚本互锁 (Governance) [COMPLETED]
- [x] **Task-008**: 真实硬件规格 (aiacc_smt_engine_v2) 物理对齐 [COMPLETED]
- [ ] **Task-009**: torch.add 10输入的压缩高压测试与伪指令生成 [ACTIVE]
