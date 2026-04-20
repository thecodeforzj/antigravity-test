# 📑 AOS Spec: Bit-Perfect Reverse Verification (V1.2)

## 1. 头部字段强制顺序
必须严格遵循：`VLD -> JUMP -> EMBED -> EMBED_END -> LOOPS -> COND -> DLY -> INC -> INC_EMBED`。

## 2. 反向验证断言
- **BIT_MATCH**: 文本字段数值必须与 JSON 逻辑值 100% 对应。
- **ID_CAUSALITY**: 解析出来的 Unit_ID 必须能回溯至 DSL ID。

| 字段 | 物理作用 |
| :--- | :--- |
| **REVERSE_VALID** | 证明文本报表具备反向还原 JSON 的能力 |

---
**Status: APPROVED** | **AOS V3.5-RIGOR**
