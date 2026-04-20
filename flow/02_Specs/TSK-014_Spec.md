# 📑 AOS Spec: Verilog-Truth Spatial Nesting (V1.4)

## 1. SETUP-EXECUTE 物理分层
- **Setup Tiers (EMBED: N..1)**:
  - 属性: `LOOPS = 1`。
  - 核心逻辑: 这些指令必须作为 Inner Payload 的前序指令发射，且不计入 $II$ 带宽占用。
- **Payload Execution (EMBED: 0)**:
  - 属性: `LOOPS = N`, `EMBED_END = MASK`。
  - 核心逻辑: 执行内层流水。

## 2. 掩码对齐 (INC_EMBED)
- `INC_EMBED` 位域应根据嵌套深度（如 6-bit）进行偏移计算，确保当内层结束时能准确跳变至目标外层。

| 字段 | 物理逻辑 |
| :--- | :--- |
| **STAGGERED_SETUP** | 验证 Setup 指令先于 Payload |
| **ZERO_OCCUPANCY** | 验证 Setup 不占用模调度相位 |

---
**Status: APPROVED** | **AOS V3.5-RIGOR**
