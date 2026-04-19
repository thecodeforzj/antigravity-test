---
aos_stage: "P2"
mission_id: "SMT-MODULO-001"
status: "FROZEN"
inputs_referenced: ["flow/01_Ideation_Threads/SMT_Modulo_Decomp_v2.md"]
---

# 💠 Spec: SMT Instruction DSL & SMT Mapping (Milestone B)

## 1. DSL 架构定义 (Schema)
我们采用 JSON 格式描述指令流，支持显式 ID 和前驱依赖：

```json
[
  { "id": "inst_0", "op": "ur_read", "bank": 1 },
  { "id": "inst_1", "op": "fpmul", "deps": [ ["inst_0", 1] ] }
]
```

- **op**: 必须映射至 `Hardware_Manifest.json` 中的 `unit_name`。
- **deps**: 表示为 `[前驱指令ID, 最小延迟偏移]`。
- **bank**: 仅针对存储操作，指定目标物理 Bank。

## 2. 映射逻辑契约 (Mapping Contract)
- **Parser** 必须能自动识别操作码并关联对应的 `latency` 和 `type`。
- **Cross-Iteration Connection**: DSL 必须能够映射跨迭代执行（Cross-iter dependencies）的语义。

## 3. 验收标准 (Acceptance Criteria - 100/100)
- **[AC-DSL-01]**: 给定一个 Horner 展开序列（Read -> Mul -> Add -> Write），验证解析器生成的任务 DAG 与 SMT 变量完全一致。
- **[AC-DSL-02]**: 验证无效操作码（Illegal Opcode）的拦截与异常提示。
- **[AC-DSL-03]**: 必须支持复杂的“多对一”依赖（一个加法依赖两个乘法输出）。
- **[AC-DSL-04]**: 100% 代码覆盖率审计。

## 4. 溯源映射
- TSK-MOD-004 -> AC-DSL-01
- TSK-MOD-005 -> AC-DSL-02, 03
