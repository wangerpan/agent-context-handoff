# Agent 工程上下文交接文档

[English](agent-handoff.md) | [简体中文](agent-handoff.zh-CN.md)

## 📌 交接元数据 (Metadata)
- **生成时间 (Timestamp)**: 2026-06-09 11:50:31
- **Git Commit SHA**: e30ecba924ae2d19d11f74c9e84edcb810826a35
- **会话 / 追踪 ID (Session ID)**: N/A

---

## 1. 当前任务
开发/生成 agent-context-handoff Skill

## 2. 当前状态 (运行时状态 - Current State)
- **活动 Agent 分类**:
  - 内置 (Built-in) 模块: 17个 (内置) (请使用描述性断言，避免死记硬编码数字)
  - 动态 (Understand-Anything) 模块: 9个 (理解类)
- **MCP 服务器连接状态**:
  - 在线服务: 暂无
  - 离线服务 (如 headroom): headroom [OFFLINE] / [离线] (注意：Agent 不应尝试调用离线服务)
- **Managed 后台 Screen 状态**:
  - 活动 screen 数量: 暂无
  - *前置启动说明*：在执行 `screen -r` 进行会话恢复之前，必须先通过 `/config` 或 `/cli` 发送 POST 请求触发初始化拉起。

## 3. 工程背景
自动压缩/打包当前 Coding Agent 上下文

## 4. 技术栈
Python / Shell / Markdown

## 5. 相关模块与文件
| 文件路径 | 作用 / 职责 | 当前状态 |
|---|---|---|
| agent_context_handoff/SKILL.md | Modified in this session | Changed |
| agent_context_handoff/SKILL.zh-CN.md | Modified in this session | Changed |
| agent_context_handoff/cli.py | Modified in this session | Changed |
| agent_context_handoff/templates/agent-handoff-template.md | Modified in this session | Changed |
| agent_context_handoff/templates/agent-handoff-template.zh-CN.md | Modified in this session | Changed |
| agent_context_handoff/templates/known-issues-template.md | Modified in this session | Changed |
| agent_context_handoff/templates/known-issues-template.zh-CN.md | Modified in this session | Changed |
| agent_context_handoff/templates/validation-template.md | Modified in this session | Changed |
| agent_context_handoff/templates/validation-template.zh-CN.md | Modified in this session | Changed |

## 6. 本轮已完成内容
- 初始化仓库
- 创建模板
- 实现 CLI

## 7. 尚未完成内容
- 本地验证
- 发布到 GitHub

## 8. 当前错误 / 阻塞点
无

## 9. 已确认结论与核心逻辑摘要
- 标准化 '.ai-context/' 目录结构

## 10. 下一轮焦点 (Focus for Next Session)
动态状态与依赖标记优化测试

## 11. 已知问题与环境约束
- headroom: [离线] 
- 无活动阻塞项

## 12. 验证命令
```bash
python3 -m agent_context_handoff.cli --lang zh
```

## 13. 给接手 Agent 的要求
- 在修改任何代码之前，优先阅读根目录下的 `AGENTS.md` 和 `.ai-context/` 目录中的所有上下文文件。
- 在开始工作前，必须先在对话中复述你对当前任务、已完成进度和下一步计划的理解。
- 遵循现有的代码风格和规范，除非有明确指示，否则避免大范围的代码重构。
- 任务修改或完成后，更新 `.ai-context/current-task.md`。
