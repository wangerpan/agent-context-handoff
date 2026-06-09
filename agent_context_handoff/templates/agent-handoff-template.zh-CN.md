# Agent 工程上下文交接文档

[English](agent-handoff.md) | [简体中文](agent-handoff.zh-CN.md)

## 📌 交接元数据 (Metadata)
- **生成时间 (Timestamp)**: {timestamp}
- **Git Commit SHA**: {git_commit_sha}
- **会话 / 追踪 ID (Session ID)**: {session_id}

---

## 1. 当前任务
{current_task_brief}

## 2. 当前状态 (运行时状态 - Current State)
- **活动 Agent 分类**:
  - 内置 (Built-in) 模块: {built_in_agents_count} (请使用描述性断言，避免死记硬编码数字)
  - 动态 (Understand-Anything) 模块: {understand_anything_count}
- **MCP 服务器连接状态**:
  - 在线服务: {online_mcps}
  - 离线服务 (如 headroom): {offline_mcps} (注意：Agent 不应尝试调用离线服务)
- **Managed 后台 Screen 状态**:
  - 活动 screen 数量: {active_screens}
  - *前置启动说明*：在执行 `screen -r` 进行会话恢复之前，必须先通过 `/config` 或 `/cli` 发送 POST 请求触发初始化拉起。

## 3. 工程背景
{project_context}

## 4. 技术栈
{tech_stack}

## 5. 相关模块与文件
| 文件路径 | 作用 / 职责 | 当前状态 |
|---|---|---|
{relevant_files}

## 6. 本轮已完成内容
{completed_work}

## 7. 尚未完成内容
{remaining_work}

## 8. 当前错误 / 阻塞点
{current_errors}

## 9. 已确认结论与核心逻辑摘要
{confirmed_decisions}

## 10. 下一轮焦点 (Focus for Next Session)
{next_session_focus}

## 11. 已知问题与环境约束
{known_issues_summary}

## 12. 验证命令
```bash
{validation_commands}
```

## 13. 给接手 Agent 的要求
- 在修改任何代码之前，优先阅读根目录下的 `AGENTS.md` 和 `.ai-context/` 目录中的所有上下文文件。
- 在开始工作前，必须先在对话中复述你对当前任务、已完成进度和下一步计划的理解。
- 遵循现有的代码风格和规范，除非有明确指示，否则避免大范围的代码重构。
- 任务修改或完成后，更新 `.ai-context/current-task.md`。
