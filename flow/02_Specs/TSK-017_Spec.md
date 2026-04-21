# 📑 AOS Spec: Tailored Regression Execution (V1.1)

## 1. 命令行交互逻辑
- **全量执行**: `python3 scripts/aos_full_regression.py` 应保持传统行为，执行所有算子。
- **单项点名**: `python3 scripts/aos_full_regression.py <ID>`。
  - `ID` 必须匹配 `TEST_CASES` 中的标识符（不区分大小写）。
  - 若 `ID` 不存在，必须抛出 `TargetNotFound` 异常并列出可用项。

## 2. 物理隔离验证
- 执行子集测试时，生成的 `REGRESSION_DSL.json` 必须对应当前点名算子，严禁受到上一次运行残留的影响。

| 字段 | 交互表现 |
| :--- | :--- |
| **SELECTIVE_CTRL** | 证明脚本已具备子集过滤能力 |

---
**Status: APPROVED** | **AOS V3.5-RIGOR**
