# 📑 AOS Spec: Compiler Robustness & Regression (V1.0)

## 1. 变量识别准则 (Variable Integrity)
- **系数识别**: 只有形如 `A[0-9]+` 的变量名才会被识别为受保护的 Horner 系数并分配至 Bank 1/2。
- **普通变量**: 诸如 `A`, `B`, `X` 等单字符或非数字后缀变量名，必须被安全地分配至默认 Bank 0，严禁触发解析异常。

## 2. 回归合格标准
- 指标: 所有算子必须达到 theoretical $II_{min}$。
- 指标: `Add10_PseudoCode.txt` 报表内容必须通过反向验证。

| 字段 | 逻辑意义 |
| :--- | :--- |
| **ALLOC_ROBUST** | 证明分配器已具备解析保护逻辑 |
| **REGRESSION_PASS** | 证明所有库算子已通过全量回归 |

---
**Status: APPROVED** | **AOS V3.5-RIGOR**
