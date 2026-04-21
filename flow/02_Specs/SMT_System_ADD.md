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
任何子系统设计 (SDD) 必须 100% 遵守以下公理，否则物理不可合成：

- `AX_01`: **Modulo Collision Freedom**: 同一 (Cycle % II) 资源占用只能为 1 (1-Unit, 1-Slot)。
- `AX_02`: **Register Integrity**: 同一寄存器在写入到下一次写入之间，生命周期不得重叠 (Anti-Overwrite)。
- `AX_03`: **Global I/O Quota**: 全局并发上限限制。单周期最大 4R (Read) / 4W (Write) VLIW 原子包。
- `AX_04`: **Bank Mutex (1R1W)**: 物理 Bank 在同一周期内，读写互斥。支持多路 Read (广播) 或单路 Write。
- `AX_05`: **Bank Concurrency**: 支持跨 Bank 并发。调度器必须通过 SMT 约束自动规避同一 Bank 的 R/W 冲突。
- `AX_06`: **Pipeline Resonance (Anti-Harmonic)**: 规避 $L \pmod{II} = 0$ 产生的周期性谐振。必须通过“读写分离”策略分散 Bank 压力。
- `AX_07`: **Latency Physics**: 指令延迟固定。FPMUL=3, FPADD=2, UR_READ=1, UR_WRITE=1。数据就绪前禁止发射后续依赖指令。
- `AX_08`: **Deterministic Header**: 41-bit `HEADER` 段必须包含 `VLD`, `DLY`, `LOOPS`, `INC` 四大元数据，实现软硬件边界对齐。
- `AX_09`: **Generality (Scale Invariant)**: 支持硬件循环宏，通过 `Vector Body + Header` 实现从标量到大规模向量（如 80 输入）的压缩。
- `AX_10`: **Unit Instance Localization**: 拥有多实例（Count > 1）的硬件单元，其在 VLIW 指令流中的物理位置偏移量需根据 `u_idx` 计算。
- `AX_11`: **Routing Determinism**: 所有运算负载必须映射至 Manifest 定义的物理端口 (如 FPMUL->rtovr_3)。调度器必须显式控制 Routing 单元的状态。
- `AX_12`: **Instruction Polymorphism**: 128-bit 指令包在不同 EMBED 下具有不同语义。EMBED=0 为标准 SMC 指令，EMBED>0 为嵌套循环元数据。
| 算法项目 | 配置 | II (V4.0) | 物理饱和度 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| **三阶霍纳 (80输入)** | Bank 0(R)/7(W) | **4** | 100% | 物理极限 (Solved $20 \pmod 5$ Conflict) |
| **菱形依赖 (Diamond)** | 跨 Bank 分散 | **2** | 95% | 复杂度 $O(N)$ 稳定 |
| **深串行链 (Chain)** | 向量化 Body | **1** | 100% | 流水线流水化成功 |

## 4. 标准化反馈接口 (Recursive Feedback)
- **SDD 反馈路径**: 若 SDD 层在详细设计中发现 II 物理不可解，必须回传 `ERR_PHYSICAL_LIMIT` 信号，强制 ADD 重新评估单位延迟或硬件资源映射。

---
**Root Authority: AOS V4.0 Stable Version**
**[MD5: COMPILER_STABLE_HEAD_2026]**

