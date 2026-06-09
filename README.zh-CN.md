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

## 🚀 安装与部署

### 1. 线上直接安装
你可以直接从 GitHub 在线安装此 CLI 工具：
```bash
python3 -m pip install git+https://github.com/wangerpan/agent-context-handoff.git
```

### 2. 本地开发安装（可编辑模式）
```bash
# 克隆仓库
git clone https://github.com/wangerpan/agent-context-handoff.git
cd agent-context-handoff

# 以可编辑模式本地安装
python3 -m pip install -e .
```

### 3. 手动拷贝安装（无 pip 依赖）
如果你无法使用 pip 或希望零依赖运行：
1. 下载本项目中的 `agent_context_handoff` 源码文件夹。
2. 将其直接复制到你的目标工程根目录下。
3. 运行 python 模块命令直接执行：
   ```bash
   python3 -m agent_context_handoff.cli --lang zh
   ```

### 4. Agent 辅助自动安装
如果你当前正在和 Coding Agent（如 Cline, Cursor, Antigravity, Claude Code 等）对话，可以直接发送以下指令让 Agent 帮您安装：
> *“帮我克隆并安装 agent-context-handoff 这个包，仓库地址为 https://github.com/wangerpan/agent-context-handoff.git”*
Agent 将会自动克隆、执行本地安装并进行验证。

### 🗑️ 卸载方法
如需移除此工具和命令，只需运行：
```bash
python3 -m pip uninstall agent-context-handoff
```

---

## 💻 使用方法

### 方法 A: 使用命令行 CLI 自动生成（推荐）

在你的目标工程根目录下运行：
```bash
# 生成英文版（默认）
ai-context-handoff --lang en

# 生成中文版
ai-context-handoff --lang zh

# 手动指定生成目标目录
ai-context-handoff --lang zh --dir /path/to/your/project
```

#### CLI 参数说明：
* `--lang`: 指定文档输出语言（`en` 或 `zh`）。
* `--dir`: 指定生成 `.ai-context/` 的目标工作区目录（默认为当前目录 `.`）。

CLI 工具会自动执行以下操作：
- **Git 状态捕获**：解析 `git status`、`git diff` 及最近提交日志。
- **任务状态增量保留**：如果 `.ai-context/current-task.md` 已存在，工具会自动提取并保留已手动修改的“任务目标”和“任务清单”，避免直接覆盖覆盖。
- **敏感信息深度脱敏**：扫描文本、状态和日志，自动对 Token、密码、密钥、敏感邮箱以及内网 IP 范围进行正则过滤脱敏，并替换为 `<REDACTED_SECRET>` 占位符。
- **索引自动追加**：创建或更新 `AGENTS.md`，追加上下文目录入口。

### 方法 B: 提示词指令集成（Manual/Agent Skill）
如果你倾向于让 Agent 自身通过对话分析并自动压缩生成上下文：
1. 复制 `agent_context_handoff/SKILL.zh-CN.md` (或 `SKILL.md`) 中的指令内容。
2. 将其粘贴集成到您的 Agent 规则文件（如 `.cursorrules`、`.clinerules` 或系统 Prompts）中。
3. 通过输入触发词唤醒 Agent 执行：
   - *“执行 context-handoff”* / *“准备切换 Agent”* / *“压缩上下文”* / *“导出交接文档”*
4. （可选）您也可以直接在对话中指令 Agent 运行 CLI 来预填充框架：
   > *“直接运行 ai-context-handoff，然后根据我们当前的开发状态细化更新 current-task.md 和 agent-handoff.md”*

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
