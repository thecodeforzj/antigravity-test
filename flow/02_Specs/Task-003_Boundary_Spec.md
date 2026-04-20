# 📑 AOS Spec: Task Boundary Governance (Three Dimensions)

## 📌 1. 物理维度: 因果哈希链 (Cryptographic Causal Chain)
*   **原则**: 每一个受控工件必须具备“父本基因”。
*   **实现**: 
    - 凡是 `Parent-Task-ID` 相同的工件，必须在 `Result.json` 中聚合。
    - **哈希失效触发**: 如果 `source_spec_hash` 发生变动，所有下游 `Result.json` 必须被标记为 `STALE (无效)`。
    - **审计要求**: 审计脚本必须能够重溯从“输入哈希”到“输出逻辑”的完整变换过程。

## 📌 2. 逻辑维度: 工件追踪矩阵 (Artifact Traceability Matrix)
*   **原则**: 任何工件都不是孤立的，它们属于某个确定的“逻辑边界”。
*   **实现**: 
    - **Lace-up Map**: 每个任务卡片必须包含一份 `Inventory` 清单，明确列出该任务对全库文件的“污染/修改”边界。
    - **所有权隔离**: 严禁两个不相关的 Task 同时修改同一个物理文件的同一个区域。
    - **边界自描述**: 受控文件内部必须声明其所服务的任务编号。

## 📌 3. 时间维度: 因果序逻辑 (Consistency of Temporal Sequence)
*   **原则**: 工程学中的修改必须顺应因果流动的方向。
*   **实现**: 
    - **T-Clock 校验**: `Spec.mtime < Code.mtime < Result.mtime < Audit.mtime`。
    - **逆序熔断**: 任何逆时间序的修改（如先写结果再补规格书）将导致任务在 [AUDITED] 阶段被物理拒绝。

---

## 🏆 验收标准
- `aos_check.py` 升级至 V3.0，支持以上三个维度的静态/动态扫描。
