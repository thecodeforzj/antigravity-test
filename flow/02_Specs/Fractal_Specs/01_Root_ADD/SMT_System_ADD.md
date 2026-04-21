# 🏗️ SMT 编译器系统架构设计 (ADD V4.0)

## 0. 状态溯源 (Traceability)
- **Layer**: ROOT_ARCH
- **Status**: FROZEN
- **Leaf_Nodes**: 
  - `02_Leaf_SDD/SMT_Solver_SDD.md`
  - `02_Leaf_SDD/Inst_Packer_SDD.md`
- **Input**: `flow/02_Specs/Hardware_Manifest.json`

## 1. 逻辑拓扑与模块职责
1. **Modulo Solver (中枢)**: 负责约束并行性求解。
2. **Instruction Packer (编码器)**: 负责物理比特位压缩。
3. **Boundary Auditor (守卫者)**: 物理校验。

## 2. 全局物理公理 (Axioms)
- `AX_01`: ** modulo_collision_freedom** (Cycle % II 唯一性)
- `AX_02`: ** register_integrity** (非重叠生命周期)
- `AX_03`: ** shared_inc_boundary**: 单条 VLIW 报文内的所有单元必须共享同物理 INC 步进，不支持异构步进合并。
- `AX_04`: ** parallel_pulsing**: 所有硬件单元在单条指令下是 100% 并行的。`DLY` 是该并行包的“发射步长”，它决定了流水线的深度与节奏。
- `AX_05`: ** atomic_linkage_occupancy**: 
  - **局部公理**: 单个 Bank 每拍仅支持 1 次存取。
  - **全局公理**: 全系统每拍支持最大 4 路并行 `UR_READ` 和 4 路并行 `UR_WRITE`。
- `AX_06`: ** bank_pinning_constraint**: 允许算子显式锁定特定 Bank ID（如常数库 Bank 7）。编译器必须在满足依赖链的前提下，解决该 Bank 的端口竞态。
- `AX_07`: ** hierarchical_complexity_scaling**: 当输入 $N \ge 20$ 时，启用分群解算，弃用单平面搜索。
- `AX_08`: ** header_phase_synchronization**: 偏移值映射至 Header 的 `INC/DLY` 字段，实现相位填空。
- `AX_09`: ** hardware_loop_saturation**: 
  - 对于大规模输入（如 80 路），通过 **“向量宽度分发（80/4=20）”** 转化为硬件循环。
  - SMT 仅负责解算原子 Loop Body 指令集。
  - Header 字段（`LOOP_COUNT=20`, `INC=3`）负责实现多批次数据的饱和式滚动喷发（Vector Pulsing）。

---
**Location: flow/02_Specs/Fractal_Specs/01_Root_ADD/SMT_System_ADD.md**
