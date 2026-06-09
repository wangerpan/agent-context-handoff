# Agent Context Handoff Skill (Agent 上下文交接工具)

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个通用的、不绑定特定工具的跨 Agent 工程上下文交接 Skill 及 CLI 工具。它可以将当前工程的开发上下文压缩为规范的 Markdown 文件，从而让不同的 Coding Agent（如 Cursor、Antigravity、Claude Code、Cline、Roo Code、Continue 等）能够无缝交接任务。

---

## 🌟 概述

在使用 Coding Agent 开发项目时，从一个 Agent 切换到另一个 Agent（或开启新会话）往往会导致上下文丢失。本项目实现了一套标准化的 **Context Handoff Skill**，用以打包：
- 当前任务状态和目标
- 最近的代码变更与摘要（通过 git status/diff）
- 关键的技术与业务决策
- 已知问题与阻塞点
- 验证步骤和命令
- 专为接手 Agent 编写的 Prompt，确保其先阅读上下文理解任务后再修改代码

---

## 📂 项目目录结构

```
agent-context-handoff/
├── SKILL.md                 # 英文 Skill 指令说明书
├── SKILL.zh-CN.md           # 中文 Skill 指令说明书
└── templates/               # 标准上下文模板目录
    ├── agent-handoff-template.md (.zh-CN.md)
    ├── current-task-template.md (.zh-CN.md)
    ├── changed-files-template.md (.zh-CN.md)
    ├── decisions-template.md (.zh-CN.md)
    ├── known-issues-template.md (.zh-CN.md)
    ├── validation-template.md (.zh-CN.md)
    ├── next-agent-prompt-template.md (.zh-CN.md)
    └── agents-section-template.md (.zh-CN.md)
```

在目标工程中自动生成的目录结构：
```
TargetProject/
├── AGENTS.md                # 统一入口索引文件
└── .ai-context/             # 存放交接上下文的文件夹（可被 git 忽略或提交共享）
    ├── README.md            # 说明上下文目录用途和使用流程
    ├── project.md           # 项目背景、技术栈与构建命令
    ├── current-task.md      # 当前任务状态摘要
    ├── agent-handoff.md     # 主交接文档
    ├── changed-files.md     # Git 状态和 diff 变更摘要
    ├── decisions.md         # 关键决策记录
    ├── known-issues.md      # 历史坑点与环境约束
    ├── validation.md        # 验证命令与结果
    └── next-agent-prompt.md # 给接手机器的 Prompt
```

---

## 🚀 如何使用

### 1. 使用命令行 CLI 工具自动化生成

你可以使用 Python CLI 工具，基于当前项目的 Git 状态和模板自动在目标工程生成 `.ai-context` 文件。

#### 安装方法
```bash
# 克隆仓库
git clone https://github.com/wangerpan/agent-context-handoff.git
cd agent-context-handoff

# 以可编辑模式本地安装
pip install -e .
```

#### 运行命令
在你的目标工程根目录下运行：
```bash
# 生成英文版（默认）
ai-context-handoff --lang en

# 生成中文版
ai-context-handoff --lang zh
```
该工具会自动：
- 解析 `git status`、`git diff` 及最近的提交日志。
- 对敏感信息（Token、API Key、密码等）进行正则扫描脱敏，并替换为 `<REDACTED_SECRET>`。
- 创建或更新 `.ai-context/` 下的所有文件。
- 如果 `AGENTS.md` 中没有 Handoff 入口章节，则会自动追加。

### 2. Manual / Agent 提示词 Skill 使用方法

如果你想让 AI Agent 自身直接编写并压缩交接文档：
1. 复制 `agent_context_handoff/SKILL.md`（或 `SKILL.zh-CN.md`）中的内容。
2. 将其添加到你的 Agent 系统提示词或规则中（例如 `.cursorrules`, `.clinerules`）。
3. 触发 Skill：在对话中对 Agent 发送触发词即可：
   - *“执行 context-handoff”* / *“执行 agent-handoff”*
   - *“压缩上下文”* / *“导出上下文”* / *“准备切换 Agent”* / *“给其他 Agent 接手”*

---

## 🔒 安全与敏感信息脱敏规则

CLI 和 Agent 指令中严格禁止写入敏感信息。所有匹配以下模式的敏感凭据都将被红线过滤：
- API Key / Access Token
- 密码 / 私钥
- 生产环境数据库连接串
- SSH 私钥、Cookie 以及 Session 会话标识

---

## 📄 开源协议

本项目采用 MIT 许可证，详情请参阅 [LICENSE](LICENSE)。
