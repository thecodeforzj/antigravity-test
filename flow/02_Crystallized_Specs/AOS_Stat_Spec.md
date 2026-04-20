---
status: "FROZEN"
task_id: "AOS-PULSE-01"
---

# 💠 Spec: AOS Status Tool (TSK-STAT)

## 1. 业务逻辑
脚本必须能够识别 `flow/00` 到 `flow/04` 的目录。
对于每个目录，计算 `.md` 文件数量（排除 `README.md`）。

## 2. 验收标准 (Acceptance Criteria)
- [ ] **AC-1**: 运行 `python app/aos_stat.py` 后，控制台输出一个包含 5 个阶段的表格。
- [ ] **AC-2**: 能够正确读取 `flow/00` 的 `project_name` 属性。
- [ ] **AC-3**: 脚本执行时间小于 500ms。

## 3. 边界条件
- 若目录不存在，应显示 "N/A" 而非报错。
