# 💠 Remediation Thread: Hardware Trait Alignment

## 1. 问题背景 (Context of the Crisis)
- **发现时间**: 2026-04-18
- **当前状态**: P2 Specs 阶段紧急挂起
- **核心偏差**: 硬件不是简单的指令发射，而是 **硬件循环/软件流水式 (Software Pipelining)**。
- **示例场景**: 计算三阶 Horner 展开的 10 个输入 `sin(arr[0-9])`。

## 2. 旧模型分析 (Legacy Model Flaws)
- *基于此前 `Hardware_Manifest.json` 的假设*:
    - 简单的顺序/并行发射模型，每个指令有固定发放时间 $T_i$。
- *灾难性点*: 
    - 忽略了硬件存在的 `embed`, `loop`, `inc`, `dely` 自动循环特性。
    - 旧模型无法描述“在同一周期执行不同迭代的指令”这一流水特性。

## 3. 新方案推演 (The New Modulo Model)
- **核心原语**: 增加 `Hardware_Loop_Engine` 描述。
- **参数支持**:
    - `loop_count`: 迭代次数 (Example: 10).
    - `inc`: 地址自增步长。
    - `II (Initiation Interval)`: 由硬件字段 `dely` 控制的迭代间隔。
- **调度目标**: 寻找最小的 II，使得在 Modulo 回绕下无资源冲突。

## 4. 决策结论 (Final Consensus)
- [ ] 调度器需支持 Modulo Scheduling 约束建模。
- [ ] 输出格式需适配硬件的 `{embed, loop, inc, dely}` 配置字段。
