---
aos_stage: "P2"
mission_id: "SMT-REF-002"
parent_arch: "01_Root_ADD/SMT_System_ADD.md"
status: "STABLE"
---

# 📑 指令编码器详细设计 (Instruction Packer SDD) - V4.2 高位包头版

## 1. 物理包对齐规则 (Layout: High-to-Low)
本设计确立了 **Header 在高、Payload 在低** 的硬件存储协议。

### 1.1 包头字段 (Header @ High Bits)
包头占据全报文的**最前（最高） 41 个比特位**。

| Range (Relative to MSB) | Field | Width | Logic |
| :--- | :--- | :--- | :--- |
| bit [MSB] | VLD | 1 | 有效位 |
| bit [MSB-1] | JUMP | 1 | 跳转位 |
| bit [MSB-2:MSB-4] | EMBED | 3 | 嵌套层级 |
| bit [MSB-5:MSB-10] | EMBED_END | 6 | 循环结束掩码 |
| bit [MSB-11:MSB-15] | DLY | 5 | 延迟计数 |
| bit [MSB-16:MSB-21] | INC_EMBED | 6 | 增量控制位 |
| bit [MSB-22:MSB-29] | LOOPS | 8 | 循环计数 (e.g., 20 for 80-inputs) |
| bit [MSB-30:MSB-35] | INC | 6 | 模间隔 (Mapped to II) |
| bit [MSB-36:MSB-40] | OTHERS | 5 | COND/RESERVED |

## 2. 物理映射逻辑 (Mapping Logic)
1. **$II \to INC$**: 报头中的 `INC` 字段必须与 SMT 最优解 $II$ 保持 1:1 同步。
2. **$Input\_Batch \to LOOPS$**: 针对 80 路输入分发的 20 个向量批次，填入 `LOOPS = 20`（或根据 0-indexed 协议）。

### 1.2 变长单元载荷 (Payload @ Following bits)
- **起始位**: `MSB - 41`。
- **填充方向**: 从高位到低位顺序填充。
- **内容来源**: `Hardware_Manifest.json` 中各个 `fields` 的位定义。

## 2. 编码与拼接逻辑
1. **Header 初始化**: 填充 41-bit `uint64_t` 或位向量。
2. **Payload 递归拼装**:
   - 对 Unit 中的每个 Field，按照 Manifest 定义的 `bits` 进行位移，并使用 `OR` 算子拼入指令流。
3. **补齐 (Padding)**: 若整体包有最终对齐要求（如 128-bit），则在低位补 0。

## 3. 验收先知 (Oracle)
- **Input**: `LOGIC` 单元指令。
- **Expected**: 生成的 32 位 Hex（假定 128-bit 对齐）中，最高位的 10.25 个字符（41 bits）必须准确解析出包头控制信号。

---
**Verified by Antigravity AI (Protocol Realignment: 2026-04-21)**
