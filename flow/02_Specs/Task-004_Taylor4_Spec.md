# 📑 AOS Spec: Task-004 Taylor 4th Order Implementation

## 1. 物理目标 (Physical Targets)
- **Initiation Interval (II)**: Target = 4 (基于单计算单元约束)。
- **Throughput**: 0.25 ops/cycle。
- **Pipeline Depth**: 预计关键路径深度 ~12 cycles。

## 2. 资源饱和度分析 (PFC)
- **MUL Utilization**: 4 ops / II=4 = 100%
- **ADD Utilization**: 4 ops / II=4 = 100%
- **Load Utilization**: 6 loads / II=4 = 150% (存在瓶颈！需要至少 2 个 Load 端口)。

## 3. 验证准则
- 必须通过 `final_truth_scanner.py` 的严格因果序检查。
- 必须生成带有 DNA 指纹的 `Taylor4_Result.json`。
