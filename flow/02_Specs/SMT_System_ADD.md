# 🏗️ SMT 编译器系统架构设计 (ADD)

## 0. 状态溯源 (Traceability)
- **Status**: FROZEN (Base Version)
- **Target**: Industrial Modulo Scheduler
- **Input**: `flow/02_Specs/Hardware_Manifest.json`
- **Downstream SDDs**: [SMT_Solver_SDD, Inst_Packer_SDD, Physical_Audit_SDD]

## 1. 逻辑拓扑与模块职责
系统由三个核心模块构成，通过标准的 JSON 协议进行解耦通信：

1. **Modulo Solver (中枢)**: 
   - 职责: 负责 Z3 约束建模、II 迭代、生成调度方案。
   - 输入: DSL 依赖图 + Hardware Manifest。
2. **Instruction Packer (编码器)**:
   - 职责: 将调度方案压缩并映射为物理 128-bit 指令流。
   - 输入: Solver 产出的 (Time, Unit, Slot) 表。
3. **Boundary Auditor (守卫者)**:
   - 职责: 独立的逆向物理校验。
   - 输入: 生成的 Binary 文件。

## 2. 全局物理公理 (Axioms)
任何子设计 (SDD) 必须 100% 遵守以下公理，否则架构无效：
- `AX_01`: ** modulo_collision_freedom**: 同一 (Cycle % II) 资源占用只能为 1。
- `AX_02`: ** register_integrity**: 每个寄存器的写入到下一次写入之间，生命周期不得重叠。

## 3. 标准化反馈接口 (Recursive Feedback)
- **SDD 反馈路径**: 若 SDD 层在详细设计中发现 II 物理不可解，必须回传 `ERR_PHYSICAL_LIMIT` 信号，强制 ADD 重新评估单位延迟或硬件资源映射。

---
**Root Authority: AOS V4.0 Compiler Hub**
