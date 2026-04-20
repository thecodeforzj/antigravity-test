# 📑 AOS Spec: Real Hardware DNA Alignment (V1.0)

## 1. 外部基准映射定义 (Alignment Fields)

本规约定义了 AOS 系统与外部 `aiacc_smt_engine_v2/hw_specs` 路径的物理同步契约：

| 字段 | 逻辑映射 | 对齐要求 |
| :--- | :--- | :--- |
| **GLOBAL_CFG** | `global_spec.yaml` -> `params` | 必须包含 `UR_BANK_NUM` 与 `EMBED_MAX_LEVEL`。 |
| **UNIT_LATENCY** | `units/*.yaml` -> `latency` | 必须从外部 YAML 实时同步，严禁硬编码。 |
| **ISA_BITMAP** | `isa_format.yaml` -> `instruction_format` | AOS 压缩引擎必须与外部位图定义保持 100% 同构。 |

---
**Status: SEALED** | **Custodian: AOS Truth Guardian**
