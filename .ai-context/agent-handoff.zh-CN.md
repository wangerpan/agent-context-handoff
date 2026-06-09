# Agent 工程上下文交接文档

[English](agent-handoff.md) | [简体中文](agent-handoff.zh-CN.md)

## 1. 当前任务
开发/生成 agent-context-handoff Skill

## 2. 工程背景
自动压缩/打包当前 Coding Agent 上下文

## 3. 技术栈
Python / Shell / Markdown

## 4. 相关模块与文件
| 文件路径 | 作用 / 职责 | 当前状态 |
|---|---|---|
| N/A | N/A | N/A |

## 5. 本轮已完成内容
- 完成跨 Agent 上下文交接 Skill 项目（包含自动化 CLI 与 10 个中英文模板）的开发。
- 代码成功发布至公开的 GitHub 仓库：https://github.com/wangerpan/agent-context-handoff。
- 对 README.md 和 README.zh-CN.md 进行了精简与去重（梳理臃肿文字，转换为清晰的 Markdown 表格）。
- 用户已在 OpenCode 客户端中完成了该工具的安装与验证（成功测试了左侧聊天框 composer bar 底部的 Agent 列表弹出、键盘导航选择和同步功能，共有 17 个可用 agents，直接点击切换即可）。
- 本地执行 `python3 -m agent_context_handoff.cli --lang zh` 完成了本项目的交接上下文生成，并更新了 `AGENTS.md` 索引。

## 6. 尚未完成内容
无

## 7. 当前错误 / 阻塞点
无

## 8. 已确认结论
- 全套交接文档与 CLI 使用 Python 3 + Git 构建。
- 双语 Markdown 文件（README、SKILL、.ai-context 下所有文件）均支持中英文互链切换。
- `current-task.md` 具备增量分析，不会覆盖自定义清单。

## 9. 待确认事项
无

## 10. 已排除方案
| 备选方案 | 排除原因 |
|---|---|
| 无 | 无 |

## 11. 风险点
无

## 12. 下一步建议
交接已就绪。接手机器人直接阅读 `.ai-context/` 下的文件，了解项目全貌，然后向用户确认接手。

## 13. 验证命令
```bash
python3 -m agent_context_handoff.cli --lang zh
```

## 14. 给接手 Agent 的要求
- 在修改任何代码之前，优先阅读根目录下的 `AGENTS.md` 和 `.ai-context/` 目录中的所有上下文文件。
- 在开始工作前，必须先在对话中复述你对当前任务、已完成进度和下一步计划的理解。
- 遵循现有的代码风格和规范，除非有明确指示，否则避免大范围的代码重构。
- 任务修改或完成后，更新 `.ai-context/current-task.md`。
