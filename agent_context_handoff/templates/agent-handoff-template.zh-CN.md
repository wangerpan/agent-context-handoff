# Agent 工程上下文交接文档

## 1. 当前任务
{current_task_brief}

## 2. 工程背景
{project_context}

## 3. 技术栈
{tech_stack}

## 4. 相关模块与文件
| 文件路径 | 作用 / 职责 | 当前状态 |
|---|---|---|
{relevant_files}

## 5. 本轮已完成内容
{completed_work}

## 6. 尚未完成内容
{remaining_work}

## 7. 当前错误 / 阻塞点
{current_errors}

## 8. 已确认结论
{confirmed_decisions}

## 9. 待确认事项
{pending_items}

## 10. 已排除方案
| 备选方案 | 排除原因 |
|---|---|
{rejected_alternatives}

## 11. 风险点
{risks}

## 12. 下一步建议
{next_step_suggestions}

## 13. 验证命令
```bash
{validation_commands}
```

## 14. 给接手 Agent 的要求
- 在修改任何代码之前，优先阅读根目录下的 `AGENTS.md` 和 `.ai-context/` 目录中的所有上下文文件。
- 在开始工作前，必须先在对话中复述你对当前任务、已完成进度和下一步计划的理解。
- 遵循现有的代码风格和规范，除非有明确指示，否则避免大范围的代码重构。
- 任务修改或完成后，更新 `.ai-context/current-task.zh-CN.md`。
