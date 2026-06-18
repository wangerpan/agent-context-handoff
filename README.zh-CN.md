# Agent Context Handoff

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个不绑定具体 Agent 的 Skill 和 Python CLI，用于在不同 Agent 或会话之间交接尚未完成的工程任务，同时保留已经验证的上下文。

## 生成内容

CLI 会在 `AGENTS.md` 中维护精简入口，并在 `.ai-context/` 下生成项目、当前任务、主交接、Git 变更、决策、已知问题、验证结果和接手提示词等文档。

中文输出使用 `.zh-CN.md` 后缀。默认执行只刷新机器生成的 Git 快照，保留已经由人工或 Agent 编写的持久上下文。

## 安装与运行

要求 Python 3.9 或更高版本。

```bash
python3 -m pip install .
ai-context-handoff --dir /path/to/project --lang zh
```

只有明确希望重新生成持久文档时才使用：

```bash
ai-context-handoff --dir /path/to/project --lang zh --force
```

Git 快照包含 staged、unstaged 和 untracked 路径，并支持从仓库子目录或 Git worktree 中运行。

## 安装 Skill

```bash
cp -R skills/agent-context-handoff ~/.agents/skills/
```

标准 Skill 会要求 Agent 先通过 CLI 做确定性采集，再检查真实工作区、当前对话和验证输出，最后用已确认事实完善持久文档。

## 安全边界

CLI 会对常见密钥、URL 密码、Bearer Token、Cookie、JWT、私钥、邮箱、手机号和内网地址进行脱敏。

正则脱敏只能降低意外泄漏风险，不能证明输出绝对安全。跨信任边界分享前必须复核最终交接包；交接文档中不要写入完整原始 Git diff。

## 开发验证

```bash
python3 -m unittest discover -s tests -v
python3 -m pip wheel . --no-deps --no-build-isolation
```

## 许可证

[MIT](LICENSE)
