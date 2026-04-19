---
aos_stage: "P1"
mission_id: "STRESS-001"
status: "DRAFT"
inputs_referenced: ["flow/00_Mission_Control/Current_Mission.md"]
---

# 💠 Decomp: Stateless-Counter (Impossible Constraint)

## 1. 业务逻辑
实现一个简单的计数函数，递增并打印数字 1-3。

## 2. 边界约束 (Revised)
- **C-1 (Relaxed)**: 允许使用函数调用栈（递归）来隐含状态。
- **C-2**: 禁止写入任何本地文件（保持）。
- **C-3**: 禁止在全局作用域定义变量（保持）。

## 3. 任务分解
- [ ] **TSK-STRESS-001**: 建立基础框架。
- [ ] **TSK-STRESS-002**: 尝试在零存储条件下实现逻辑。
