# 📑 AOS Spec: Governance Hard-Gating (V1.0)

## 1. 治理闸口逻辑定义 (Governance Bitfields)

虽然这是元治理任务，但我们依然将其逻辑抽象为“虚拟位域”以供审计：

| 字段 | 位宽 | 逻辑定义 |
| :--- | :--- | :--- |
| **GATE_ENABLE** | 1 bit | 1=强制开启 Sync 前的审计核验。 |
| **COV_SCAN** | 1 bit | 1=启用针对 Spec 定义字段的自动匹配扫描。 |
| **CERT_SIGN** | 1 bit | 1=100% 覆盖后生成带 Hash 校验的数字证书。 |
| **SYNC_LOCK** | 1 bit | 1=没有证书时物理封锁 `git commit`。 |

## 2. 物理溯源要求 (Standardized Traceability)
- 任何 TSK 必须在 `[ARTIFACT_INDEX]` 中包含关联的 Spec 全路径。
- `aos_check.py` 必须在执行 Sync 前被子进程调用。
- 证书内容必须包含 `spec_hash` 以防止规约漂移。

---
**Status: PROPOSED** | **AOS V3.5-GOVERN**
