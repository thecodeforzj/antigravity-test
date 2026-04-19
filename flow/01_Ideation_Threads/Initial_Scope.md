# 💠 Initial Scope: Antigravity Workflow Core

## 1. 目标分解 (Goal Breakdown)
- **Phase 0 (System Boot)**: 完成 `.antigravity_rules` 与 `Workflow_*` 模板的本地化与对齐。 (CURRENT)
- **Phase 1 (State Machine Integration)**: 打通 ClickUp API，实现任务自动注册与状态同步。
- **Phase 2 (Knowledge Loop)**: 实现从 `Engineering_Log` 到 `Global_Brain` 的自动化提纯 (Distill) 模块。
- **Phase 3 (Pilot Project)**: 以 "SMT Scheduler" 为首个试点项目验证全流程。

## 2. 初始技术选型 (Initial Tech Stack)
- **Knowledge Base**: Obsidian (Markdown + Templater)
- **Logic Engine**: Javascript / Python (Antigravity Executor)
- **State Machine**: ClickUp API
- **Version Control**: Git (Native integration)

## 3. 潜在风险 (Potential Risks)
- **Context Drift**: 任务过大导致 context window 溢出，需要严格的 P0-P4 阶段解耦。
- **API Token Security**: ClickUp Token 的安全存储问题。
- **Knowledge Fragmentation**: 跨项目知识如果没有标准化提纯，会导致 `Global_Brain` 变为信息垃圾场。
