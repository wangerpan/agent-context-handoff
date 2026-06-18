# Agent 上下文交接

这是 `skills/agent-context-handoff/SKILL.md` 的中文说明；标准 Skill 入口以带 YAML frontmatter 的英文文件为准。

## 执行流程

1. Git 可用时通过 `git rev-parse --show-toplevel` 定位项目根目录。
2. 执行 `ai-context-handoff --dir <项目> --lang zh` 初始化文档并刷新 Git 快照。除非用户明确要求替换人工文档，否则不要使用 `--force`。
3. 检查当前对话、工作区、相关源码、Git 状态和测试输出。
4. 只把已经验证的事实写入持久文档；不得虚构已完成工作、决策、命令、错误或验证结果。
5. 写入前删除密钥、Cookie、私钥、生产连接串、个人联系方式和敏感内部地址。
6. 确认文件路径、阻塞点、下一步和验证命令能被接手 Agent 直接执行。

## 安全边界

- 普通刷新不得覆盖已有人工上下文。
- 正则脱敏只是纵深防御，最终交接包仍需人工或 Agent 复核。
- `AGENTS.md` 只保留入口索引，详细状态放在 `.ai-context/`。
