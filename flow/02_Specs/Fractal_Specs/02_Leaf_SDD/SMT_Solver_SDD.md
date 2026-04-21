---
aos_stage: "P2"
mission_id: "SMT-REF-001"
parent_arch: "01_Root_ADD/SMT_System_ADD.md"
status: "STABLE"
---

# 📑 SMT 求解器详细设计 (SMT Solver SDD)

## 1. 变量定义 (Variables)
- **T_Start (Int)**: 指令启动的绝对周期时间。
- **U_Usage (Int)**: 指令占用的物理单元索引（0..Count-1）。
- **Phase (T_Start % II)**: 指令所属的模相位。

## 2. 约束逻辑 (Z3 Constraints)
1. **Modulo Resource Conflict**:
   - 对任意指令对 (i, j) 且 `Unit(i) == Unit(j)`:
   - 约束：`Implies(U_Usage[i] == U_Usage[j], T_Start[i] % II != T_Start[j] % II)`。
2. **Data Dependency**:
   - `T_Start[child] >= T_Start[parent] + Latency[parent]`.
3. **Memory Bank Access**:
   - 同一 Bank 在同一 Phase 只能被访问一次：`PbLe([(T_Start[i] % II == p, 1) for i in bank_ops], 1)`。

## 3. II 迭代算法 (Binary Search)
- **Init**: 
  - `II_min = max(Resource_Load / Resource_Count)`. 
  - `II_max = Sum(all_latencies)`.
- **Search**:
  - `while II_min <= II_max`:
  - `II_test = (II_min + II_max) // 2`.
  - `s.check()` 为 SAT -> `result = SAT, II_max = II_test - 1`.
  - `s.check()` 为 UNSAT -> `record_conflict(), II_min = II_test + 1`.

## 4. 冲突处理与反馈 (Conflict Handlings)
- **Traceback**: 利用 `s.unsat_core()` 提取冲突指令集。
- **Output**: 记录于 `flow/04_Engineering_Log/Conflict_Trace_[TIME].json`。

## 5. 验收先知 (Oracle)
- **Scenario**: 资源饱和度达到 100% (II=1)。
- **Expectation**: Solver 必须找到唯一解，或由于 Bank 冲突返回精确的 Unsat Core。

## 6. 大规模扩展实现 (Large-Scale Scaling - AX_07)
### 6.1 任务分群 (DAG Clustering)
- **目标**: 将 $N > 40$ 的算子拆解为 $M$ 个子群（Sub-Kernels）。
- **判定**: 利用连接矩阵的度（Degree）进行割集，保证跨区依赖最小化。
- **约束**: 跨群依赖通过 `T_Start[child] >= T_Fixed[parent] + Latency` 注入，`T_Fixed` 来自前一个子群的 SAT 解。

### 6.2 资源预定表 (Resource Reservation Table - RRT)
- **锁定机制**: 已排定子群的 Phase 占用情况将写入 RRT。
- **动态屏蔽**: 当前子群解算时，必须通过 `s.add(RRT_Mask[phase] == False)` 避开已分配资源位。

---
**Standard: AOS MRA V4.0 Compliance**
