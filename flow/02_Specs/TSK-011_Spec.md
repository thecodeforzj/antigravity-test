# 📑 AOS Spec: Production Formula Compiler (V3.10)

## 1. 物理资源池化规则
- 所有多项式系数 (A0..An) 必须映射至 **Bank 1** 以隔离变量流。
- 变量 X 锁定在 **Bank 0**。

## 2. 算子物理映射
- `ast.Sub` 映射至 `fpadd` 且 `ADD_OR_SUB` 字段必须有效。

| 字段 | 物理含义 |
| :--- | :--- |
| **BANK_ISOLATION** | 证明系数与变量不在同一物理端口 |
| **DLY_CASCADE** | 证明级联 DLY 递归逻辑正确 |

---
**Status: APPROVED** | **AOS V3.5-RIGOR**
