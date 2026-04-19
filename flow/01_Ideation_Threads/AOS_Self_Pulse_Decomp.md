# 💠 Decomp: AOS-Self-Pulse (Status Tool)

## 1. 核心功能描述
一个轻量级的 Python 脚本，读取 `flow/` 目录结构，统计各阶段文件数量，并输出一个 Markdown 格式的仪表盘。

## 2. 任务矩阵 (Task DAG)
- [ ] **TSK-STAT-001**: 定义目录扫描逻辑 (Stage Directory Mapping)。
- [ ] **TSK-STAT-002**: 格式化输出模板 (Markdown Table Generator)。
- [ ] **TSK-STAT-003**: 链路验证 (Integration Test)。

## 3. 技术选型
- **Engine**: Python 3
- **Input**: `os.path` walk
- **Output**: `stdout` (Markdown format)
