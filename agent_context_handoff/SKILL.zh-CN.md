# SKILL: Agent 上下文交接 (Agent Context Handoff)

[English](SKILL.md) | [简体中文](SKILL.zh-CN.md)

## 描述
创建一个通用的、跨 Agent 的工程上下文交接规范包。

---

## 🎯 触发词
当用户输入以下任何内容时触发此 Skill：
- `执行 context-handoff` / `执行 agent-handoff` / `交接`
- `压缩上下文` / `导出上下文` / `准备切换 Agent` / `给其他 Agent 接手`
- `生成交接文档` / `生成工程上下文包`

---

## 📋 核心指令

触发后，您必须将当前工作区的状态编译为项目根目录下 `.ai-context/` 目录中的结构化上下文包。输出内容必须保持 **Agent 中立**，不要假设下一个工具的具体身份。

### 1. 维护的目录结构
确保目标工程具有以下目录结构。如果文件不存在，则创建；如果存在，基于当前进度更新其内容。

```
TargetProject/
├── AGENTS.md
└── .ai-context/
    ├── README.md
    ├── project.md
    ├── current-task.md
    ├── agent-handoff.md
    ├── changed-files.md
    ├── decisions.md
    ├── known-issues.md
    ├── validation.md
    └── next-agent-prompt.md
```

### 2. Git 状态收集
如果当前环境能访问 Git，请运行以下命令辅助生成变更文件列表及验证摘要：
- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- `git log --oneline -5`

> [!WARNING]
> 禁止将大段完整原始 git diff 写入交接文件，仅写入变更摘要。

### 3. 敏感数据脱敏
您必须对生成的内容进行敏感信息扫描和脱敏。将敏感值统一替换为占位符：
- Access Token / API Key / Secrets -> `<REDACTED_SECRET>`
- 密码 -> `<REDACTED_PASSWORD>`
- 私钥 -> `<REDACTED_PRIVATE_KEY>`
- 生产环境数据库连接 -> `<REDACTED_PROD_DB>`
- 真实手机号 / 真实邮箱 -> `<REDACTED_PHONE>` / `<REDACTED_EMAIL>`
- 内部网络敏感地址 -> `<REDACTED_INTERNAL_HOST>`
- 会话 Cookie -> `<REDACTED_COOKIE>`

### 4. 更新 AGENTS.md 索引
如果目标项目根目录下不存在 `AGENTS.md` 则创建。如果已存在但没有 AI Context Handoff 章节，则追加该章节，使其索引到 `.ai-context/agent-handoff.md` 和 `.ai-context/README.md`。`AGENTS.md` 只做入口索引，保持精简。

---

## 📝 交付文档要求

### agent-handoff.md
必须包含以下章节：
1. **当前任务**：当前步骤的简要目标。
2. **工程背景**：项目的核心背景。
3. **技术栈**：开发语言和关键框架。
4. **相关模块与文件**：使用 Markdown 表格列出涉及文件、作用和当前状态。
5. **本轮已完成内容**：已实现内容的列表。
6. **尚未完成内容**：尚未实现的待办列表。
7. **当前错误 / 阻塞点**：当前遇到的问题或报错。
8. **已确认结论**：已做出的最终架构或业务决策。
9. **待确认事项**：未决的问题或待确认项。
10. **已排除方案**：被排除的方案及其原因（表格格式）。
11. **风险点**：需要接手 Agent 注意的坑点或风险。
12. **下一步建议**：建议的后续实施动作。
13. **验证命令**：用于执行测试或运行的命令块。
14. **给接手 Agent 的要求**：
    - 必须先阅读 `AGENTS.md` 和 `.ai-context/` 目录下的上下文文件。
    - 必须在修改代码前先复述对任务的理解。
    - 除非明确要求，不要进行大范围的代码重构。
    - 沿用项目原有的代码风格和规范。

### next-agent-prompt.md
生成一个 Prompt 代码块，便于用户直接复制给下一个接手的 AI Agent。该 Prompt 将引导新 Agent 优先阅读上下文文档并确认理解，再开始编写代码。
