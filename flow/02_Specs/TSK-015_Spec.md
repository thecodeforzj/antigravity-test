# 📑 AOS Spec: Workspace Normalization & Cleanup (V1.0)

## 1. 产出物归一原则
所有具有物理意义的文件（DSL, Spec, Task Card）必须属于某一个原子任务的 `[ARTIFACT_INDEX]` 名单。

## 2. 漂移检测基准
- **ZERO_DRIFT**: 指标为 `git status` 输出为空。
- **ORPHAN_ADOPTION**: 指标为所有曾出现在 IDE 中的改动都已在 Git 历史中找到对应任务关联。

| 字段 | 逻辑意义 |
| :--- | :--- |
| **NORMALIZED** | 证明工作区已完成历史遗留物补丁式归档 |

---
**Status: APPROVED** | **AOS V3.5-RIGOR**
