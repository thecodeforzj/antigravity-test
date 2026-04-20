# [Task-001] AOS 核心流程验证规格说明书

## 1. 物理目的 (Physical Intent)
本规格书旨在固化 AOS 2.3 系统的自引导路径验证，验证原子化任务与物理输出之间的严格映射关系。

## 2. 核心约束 (Core Constraints)
- **输入引用**: `flow/03_Active_Sprints/Task-001_Verify.md`。
- **输出锚点**:
    - 代码文件路径: `ROOT/hello_ai_native.py`。
    - 运行输出内容: `Antigravity Pipeline Verified`。
- **关联 Task ID**: `[Task-001]`

## 3. 验收标准 (Acceptance Criteria)
1. **代码一致性**: `hello_ai_native.py` 的 MD5 校验必须反映其打印内容。
2. **审计对齐**: `scripts/aos_check.py` 必须在执行后将其标记为 `HEALTHY`。
3. **因果对齐**: 本文档必须早于代码实现文件创建。

---
*Status: Crystallized*
*AOS-Rigor: CRITICAL*
