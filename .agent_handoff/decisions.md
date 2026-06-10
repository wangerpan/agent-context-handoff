# Engineering Decisions Log

[English](decisions.md) | [简体中文](decisions.zh-CN.md)

## Record of Architecture and Business Logic Decisions

### [YYYY-MM-DD] 初始化架构决策
- **Context**: 需要确定跨 Agent 交接的规范形式
- **Decision**: 选择使用标准 Markdown 模板并放在 .ai-context/ 目录下
- **Consequences**: 所有支持 Markdown 读取的 AI Agent 都可以无感阅读该上下文
- **Status**: Approved (e.g. Approved / Proposed)
