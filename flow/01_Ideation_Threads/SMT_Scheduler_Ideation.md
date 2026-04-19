# 💠 Ideation: SMT Compiler Scheduling Algorithm

## 1. 目标分解 (Goal Breakdown)
- **Phase P1 (Hardware Modeling)**: 将用户提供的硬件单元、延迟、端口依赖与 Bank 冲突抽象为规范化的 JSON Manifest。
- **Phase P2 (SMT Constraint Mapping)**: 
    - 约束 A: 数据依赖 (Dependency Constraints) - 必须在前序指令写回后读取。
    - 约束 B: 资源冲突 (Structural Hazards) - 加法器/乘法器个数限制。
    - 约束 C: Bank 冲突 (Memory Hazards) - 相同周期禁止 R/W 同一 Bank。
    - 约束 D: 端口选通 (Routing Constraints) - `rtovr` 的脉冲式选通映射。
- **Phase P3 (Solver Development)**: 开发基于 Python-Z3 的核心调度引擎，通过最小化 `max(completion_time)` 实现最优排序。
- **Phase P4 (Verification)**: 生成可视化指令流水线图，验证硬件规则 100% 遵从。

## 2. 初始技术选型 (Initial Tech Stack)
- **Solver**: `z3-solver` (Python)
- **Logic**: 基于 Integer Linear Programming (ILP) 的 SMT 编码。
- **Hardware Abstraction**: `Hardware_Manifest.json`

## 3. 潜在风险 (Potential Risks)
- **Complexity**: 多指令长 Latency 会导致 SMT 解空间急剧增加，需要引入启发式切片。
- **Bank Conflict Detection**: `ur_read` 和 `ur_write` 的地址动态解析在编译期是关键（需假设已知地址或进行符号化处理）。
- **Port Mapping**: `rtovr` 与输入端口的强绑定关系需要精确的索引映射逻辑。
