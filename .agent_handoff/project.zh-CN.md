# 项目概览

[English](project.md) | [简体中文](project.zh-CN.md)

## 项目背景与说明
本项目用于生成通用的、不绑定特定工具的跨 Agent 工程上下文交接 Skill 及 CLI 工具。它可以将当前工程的开发状态压缩并生成规范的 Markdown 文件集，避免切换 Agent 时的上下文丢失。

## 核心技术栈
- Python 3.x
- Markdown / templates

## 目录结构与核心模块说明
- `agent_context_handoff/`: Python 源码包目录。
  - `cli.py`: 主要的命令行执行逻辑与增量分析程序。
  - `SKILL.zh-CN.md` / `SKILL.md`: 提供给 AI Agent 的系统交接 Skill 指令。
  - `templates/`: 各种上下文文档生成的模板目录。
- `setup.py`: 模块包打包及 CLI 快捷入口 `ai-context-handoff` 的注册配置。

## 构建与运行指南
```bash
# 初始化与本地安装
python3 -m pip install -e .

# 直接执行交接命令（生成中文文档）
ai-context-handoff --lang zh
```
