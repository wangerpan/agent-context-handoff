# Agent 工程上下文交接文档

[English](agent-handoff.md) | [简体中文](agent-handoff.zh-CN.md)

## ⚡ 接手 Agent 推荐阅读优先级

| 优先级 | 章节 | 原因 |
|:---:|---|---|
| 1 | **4. 相关模块与文件** | 快速建立物理代码结构认知 |
| 2 | **10. 已确认结论与核心逻辑摘要** | 理解系统架构设计意图与决策背景 |
| 3 | **13. 验证命令** | 跑通现有测试，确认开发环境就绪 |
| 4 | **12. 已知问题与环境约束** | 规避历史坑点与盲目重试离线服务 |
| 5 | **1. 当前任务 & 11. 下一轮焦点** | 明确接手后应该从哪里开始着手 |

---

## 📌 交接元数据 (Metadata)
- **生成时间 (Timestamp)**: 2026-06-09 13:17:06
- **Git Commit SHA**: 7771fc696acf4f1f16b7aa3025c7b73df4c87c0d
- **会话 / 追踪 ID (Session ID)**: N/A

---

## 1. 当前任务
开发/生成 agent-context-handoff Skill

## 2. 当前状态 (运行时状态 - 无相关性项目可跳过)
- **活动 Agent 分类**:
  - 内置 (Built-in) 模块: 17个 (内置) (请使用描述性断言，避免死记硬编码数字)
  - 动态 (Understand-Anything) 模块: 9个 (理解类)
- **MCP 服务器连接状态**:
  - 在线服务: 暂无
  - 离线服务 (如 headroom): headroom [OFFLINE] / [离线] (注意：Agent 不应尝试调用离线服务)
- **Managed 后台 Screen 状态**:
  - 活动 screen 数量: 暂无
  - *前置启动说明*：在执行 `screen -r` 进行会话恢复之前，必须先通过 `/config` 或 `/cli` 发送 POST 请求触发初始化拉起。

## 3. 工程背景与技术栈
自动压缩/打包当前 Coding Agent 上下文
- **技术栈**: Python / Shell / Markdown

## 4. 相关模块与文件 (物理行数审计)
| 文件路径 | 作用 / 职责 | 物理行数 | 当前状态 |
|---|---|---|---|
| .ai-context/agent-handoff.md | Modified in this session | 113 | Changed |
| .ai-context/changed-files.md | Modified in this session | 56 | Changed |
| .ai-context/current-task.md | Modified in this session | 22 | Changed |
| .ai-context/validation.md | Modified in this session | 20 | Changed |
| .clinerules | Modified in this session | 73 | Changed |
| .cursorrules | Modified in this session | 73 | Changed |
| README.md | Modified in this session | 66 | Changed |
| README.zh-CN.md | Modified in this session | 66 | Changed |
| agent_context_handoff/SKILL.md | Modified in this session | 102 | Changed |
| agent_context_handoff/SKILL.zh-CN.md | Modified in this session | 88 | Changed |
| agent_context_handoff/cli.py | Modified in this session | 576 | Changed |
| .gitignore | Modified in this session | 110 | Changed |
| agent-context-handoff-skill-plan.docx | Modified in this session | 341 | Changed |

## 5. 核心私有方法与数据流
| 方法名称 | 调用场景 / 触发 | 职责 / 数据组装作用 |
|---|---|---|
| 方法名 | 调用/触发场景 | 作用与数据转换职责 (待 Agent 补充) |

## 6. 跨平台迁移依赖审计 (无相关性项目可跳过)
| 专属 API / 配置文件 | 引用次数 | 所在文件位置 | 目标平台替代技术方案 |
|---|:---:|---|---|
| 平台 API: `chrome.storage` | 1 | N/A | [在此描述替代技术方案] |
| 平台 API: `chrome.runtime` | 1 | N/A | [在此描述替代技术方案] |
| 平台 API: `localStorage` | 1 | N/A | [在此描述替代技术方案] |
| 平台 API: `process.env` | 1 | N/A | [在此描述替代技术方案] |
| 平台 API: `window.` | 1 | N/A | [在此描述替代技术方案] |
| 平台 API: `document.` | 1 | N/A | [在此描述替代技术方案] |
| 外部依赖: `setuptools` | 1 | N/A | 第三方库依赖 |

## 7. 本轮进度与已完成/未完成清单 (强制状态前缀规范)
*前缀规则：`✅ 已完成` (代码已存在), `🔄 进行中` (部分代码存在), `📋 规划中` (零代码仅讨论), `⚠️ 受阻` (开发阻塞)*

- **本轮已完成**:
- 初始化仓库
- 创建模板
- 实现 CLI

- **尚未完成内容**:
- 本地验证
- 发布到 GitHub

## 8. 已废弃代码（v1 遗留 / 孤立类）
- 无活动废弃类 (若有 DTO 无外部调用，请在此列出以引导清理)

## 9. 当前错误 / 阻塞点
无

## 10. 已确认结论与核心逻辑摘要
- 标准化 '.ai-context/' 目录结构

## 11. 下一轮焦点 (Focus for Next Session)
无特定关注焦点。

## 12. 已知问题与环境约束
- headroom: [离线] 
- 无活动阻塞项

## 13. 验证命令
```bash
python3 -m agent_context_handoff.cli --lang zh
```

## 14. 给接手 Agent 的项目特定硬约束
### 📚 必须阅读的文件
1. `.ai-context/project.zh-CN.md` — 项目核心设计与评分公式。
2. `.ai-context/decisions.zh-CN.md` — 关键架构决策背景。

### 🚫 绝对不允许修改的内容
- 列出工程内高度敏感、绝对不可擅自修改的核心逻辑或配置文件。

### ⚠️ 代码设计陷阱与注意事项
- 列出具体的耦合陷阱（例如：“修改 A 接口结构会破坏 B 转换，请注意保持结构兼容”）。
