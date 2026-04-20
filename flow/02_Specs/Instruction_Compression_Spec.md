# 📑 AOS Spec: Instruction Compression & Nested Loops (V1.0)

## 1. 共有字段物理定义 (Common Bitfields)

| 字段 | 位宽 (拟) | 说明 |
| :--- | :--- | :--- |
| **VLD** | 1 bit | 有效位。0=NOP (保持上一拍信号，vld=0给SMC)。 |
| **JUMP** | 1 bit | 1=跳转指令。互斥：不支持 LOOPS, DLY。必须处理 COND。 |
| **EMBED** | 3 bits | 0-6: 嵌套层级（0=最内层）。7: 无效。 |
| **EMBED_END**| 6 bits | 仅当 EMBED=0 有效。位掩码标识 EMBED=1~6 层循环结束。 |
| **LOOPS** | BITS_LOOPS | 执行 N+1 次。 |
| **COND** | BITS_COND | 等待 INST_RDY_IN 的对应槽位就绪。 |
| **DLY** | BITS_DLY | 发射到延迟线，移位到末端生效。 |
| **INC** | BITS_INC | 指令内地址/寄存器自增量（带符号数）。 |
| **INC_EMBED**| 6 bits | 仅当 EMBED=0 有效。控制 i=1~6 层 INC 是否在 EMBED=0 叠加。 |

## 2. 计算叠加逻辑 (Scaling & Accumulation)

当 `EMBED=0` 且 `EN_INC=1` 时，发出的最终数值计算公式如下：
$$Value = BASE + \sum_{i=1}^{6} (INC_i \times LOOP\_CNT_i \times INC\_EMBED[i-1])$$

*   **BASE**: `CODE[INC_HIGH:INC_LOW]` 定义的基础值。
*   **INCi**: 第 $i$ 层嵌套定义的增量。
*   **LOOP_CNTi**: 第 $i$ 层当前的计数值。

## 3. CODE 字段多模态语义 (CODE Polymorphism)

### 3.1 模式 A: 标准 SMC 指令
当 `EMBED=0` 且非特殊模式时。

### 3.2 模式 B: JUMP 扩展
当 `JUMP=1` 时：
- `CODE[LSB+42]`: 有无符号标识。
- `CODE[LSB+41:40]`: 跳转条件 (00: >, 01: ==, 10: <, 11: End-of-Queue)。
- `CODE[LSB+39:8]`: 期望数据。
- `CODE[LSB+7:0]`: 跳转偏移量（有符号）。

### 3.3 模式 C: 嵌套循环元数据
当 `EMBED!=0` 且 `CODE[BITS_CODE-1]=1`：
- **000 (激活列)**: 包含 LF_PAD, RT_PAD, MIN, MAX。INC 代表列 Stride。
- **001 (激活行)**: 包含 UP_PAD, DN_PAD, MIN, MAX。INC 代表行 Stride。
- **010/011 (权重列/行)**: 包含 Dilation 信息。
- **100 (精度与 Padding)**:
    - 精度: 2/4/8/16 bit。
    - 模式: Constant, Reflection, Replication, Circular。

---
**Status: PROPOSED** | **Origin: User_Request_2026-04-20**
