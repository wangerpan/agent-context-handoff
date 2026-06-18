# AI Agents Guide

This file serves as a guide for AI Coding Agents working on this project.

## AI Context Handoff (AI 上下文交接)

该项目在 `.agent_handoff/` 目录下维护了标准化的开发上下文。如果您是接手任务 of AI Coding Agent，请在修改代码前先阅读位于 [.agent_handoff/README.zh-CN.md](file://./.agent_handoff/README.zh-CN.md) 或 [.agent_handoff/README.md](file://./.agent_handoff/README.md) 的文档索引，以了解项目背景、当前任务进度和代码变更。

- **主交接文档**: [.agent_handoff/agent-handoff.zh-CN.md](file://./.agent_handoff/agent-handoff.zh-CN.md) | [.agent_handoff/agent-handoff.md](file://./.agent_handoff/agent-handoff.md)
- **当前任务状态**: [.agent_handoff/current-task.zh-CN.md](file://./.agent_handoff/current-task.zh-CN.md) | [.agent_handoff/current-task.md](file://./.agent_handoff/current-task.md)
- **接手机器人 Prompt**: [.agent_handoff/next-agent-prompt.zh-CN.md](file://./.agent_handoff/next-agent-prompt.zh-CN.md) | [.agent_handoff/next-agent-prompt.md](file://./.agent_handoff/next-agent-prompt.md)

## Version Control Rule (版本控制规则)

每当对项目代码（如 CLI 逻辑、模板等）进行修改并准备提交时，AI Agent 必须自动将版本号的第三位（Patch version）加 1（例如从 `v1.0.1` 升级为 `v1.0.2`），同步更新 `setup.cfg` 和 `agent_context_handoff/__init__.py`，并在提交后创建并推送对应的 Git Tag（如 `v1.0.2`）。

