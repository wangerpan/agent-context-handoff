# SKILL: Agent 上下文交接 (Agent Context Handoff)

[English](SKILL.md) | [简体中文](SKILL.zh-CN.md)

## 描述
创建一个通用的、不绑定特定工具的跨 Agent 工程上下文交接规范包。

---

## 🎯 触发唤醒词 (Trigger Words)
当用户在对话中发送以下任意触发词时，立即执行此 Skill：
- `执行 context-handoff` / `执行 agent-handoff` / `交接`
- `压缩上下文` / `导出上下文` / `准备切换 Agent` / `给其他 Agent 接手`
- `生成交接文档` / `生成工程上下文包`

---

## 📋 核心指令

触发后，您必须将当前工作区的状态编译为项目根目录下 `.ai-context/` 目录中的结构化上下文包。主交接文件必须写死输出到 **`.ai-context/agent-handoff.zh-CN.md`**（或英文版的 `.ai-context/agent-handoff.md`）。

### 1. 强制性交接结构检查清单
每个生成的交接文档必须包含以下固定章节：
- **追踪信息**：必须包含精确时间戳和当前 Git Commit SHA，以支持会话与版本追溯。
- **核心制品路径**：以 Markdown 表格列出关键变更文件、作用及当前状态。
- **启动/验证命令**：提供可直接复制执行的测试或运行命令块。
- **当前状态**：明确标示当前步骤状态（已完成 / 进行中 / 阻塞）。
- **关键决策摘要**：简要概括重要的技术与业务决策。允许必要的设计与逻辑摘要，但严禁大段复制源码，应使用文件路径与行号进行链接引用。
- **已知限制**：记录历史坑点、环境约束或已知阻塞。
- **下一轮焦点 (Focus for Next Session)**：如有指定，需开辟独立章节承载用户传入的下阶段任务目标。

### 2. CLI 工具协同 (推荐优先执行)
如果当前项目安装了 `agent-context-handoff`，你可以直接在终端中运行以下命令来自动收集 Git 状态、解析变更并对敏感数据进行高级脱敏：
- 中文交接：`ai-context-handoff --lang zh --focus "写明给接手 Agent 的下阶段任务目标"`
- 英文交接：`ai-context-handoff --lang en --focus "Describe the focus for the incoming agent"`

运行完 CLI 后，你只需要手动打开 `.ai-context/` 目录，并根据开发进度细化修改相关文件即可。

### 3. 敏感数据脱敏
您必须对生成的内容进行敏感信息扫描和脱敏。将敏感值统一替换为占位符：
- 密钥/Token -> `<REDACTED_SECRET>`
- 密码 -> `<REDACTED_PASSWORD>`
- 私钥 -> `<REDACTED_PRIVATE_KEY>`
- 数据库连接 -> `<REDACTED_PROD_DB>`
- 手机/邮箱 -> `<REDACTED_PHONE>` / `<REDACTED_EMAIL>`
- 内网 IP -> `<REDACTED_INTERNAL_HOST>`
- 会话 Cookie -> `<REDACTED_COOKIE>`

### 4. 自我验证步骤 (Self-Audit)
在完成交接前，您必须：
1. 对照工作区实际的 `git diff` 和源码逻辑，核对您撰写的交接文档。
2. 确保文档中写的关键条件（如特定配置文件、变量名或逻辑过滤条件）与代码现状一致，纠正任何逻辑偏差。

---

## 📝 交付文档要求

### `.ai-context/agent-handoff.zh-CN.md`
必须遵循以下章节布局：
1. **追踪信息**：生成时间戳、Git Commit SHA。
2. **当前任务**：当前步骤简要目标。
3. **工程背景与技术栈**：项目简介及核心语言/框架。
4. **相关模块与文件**：文件/作用/状态对照表格。
5. **本轮已完成与尚未完成内容**：已实现及未实现的待办列表。
6. **当前错误 / 阻塞点**：当前遇到的问题或报错。
7. **已确认结论**：技术决策记录（附带源码文件引用，如 `[文件名](file:///path/to/file#L123)`）。
8. **下一轮焦点 (Focus for Next Session)**：独立章节，描述下阶段具体任务或用户定义的焦点。
9. **验证命令**：可直接复制运行的测试或执行命令。
10. **给接手 Agent 的要求**。
