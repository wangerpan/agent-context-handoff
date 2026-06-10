# 技术决策记录

[English](decisions.md) | [简体中文](decisions.zh-CN.md)

## 架构和业务逻辑决策记录

### [YYYY-MM-DD] 初始化架构决策
- **决策背景**: 需要确定跨 Agent 交接的规范形式
- **具体决策**: 选择使用标准 Markdown 模板并放在 .ai-context/ 目录下
- **带来的影响**: 所有支持 Markdown 读取的 AI Agent 都可以无感阅读该上下文
- **决策状态**: 已批准 (如：已批准 / 提案中)
