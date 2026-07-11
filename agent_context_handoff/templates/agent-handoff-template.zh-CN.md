# Agent 工程上下文交接文档

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
- **生成时间 (Timestamp)**: {timestamp}
- **Git Commit SHA**: {git_commit_sha}
- **会话 / 追踪 ID (Session ID)**: {session_id}

---

## 1. 当前任务
{current_task_brief}

## 信息可信度分层
- **已验证事实**：由当前代码、Git 状态、命令或测试输出直接支持。
- **历史上下文**：可能已经过期的既有结论，使用前必须复核。
- **假设**：用于推进排查的工作假设，不得表述为已确认行为。
- **未验证待办**：尚未完成或仍需验证的工作。

## 2. 当前状态 (运行时状态 - 无相关性项目可跳过)
- **活动 Agent 分类**:
  - 内置 (Built-in) 模块: {built_in_agents_count} (请使用描述性断言，避免死记硬编码数字)
  - 动态 (Understand-Anything) 模块: {understand_anything_count}
- **MCP 服务器连接状态**:
  - 在线服务: {online_mcps}
  - 离线服务 (如 headroom): {offline_mcps} (注意：Agent 不应尝试调用离线服务)
- **Managed 后台 Screen 状态**:
  - 活动 screen 数量: {active_screens}
  - *前置启动说明*：在执行 `screen -r` 进行会话恢复之前，必须先通过 `/config` 或 `/cli` 发送 POST 请求触发初始化拉起。

## 3. 工程背景与技术栈
{project_context}
- **技术栈**: {tech_stack}

## 4. 相关模块与文件 (物理行数审计)
| 文件路径 | 作用 / 职责 | 物理行数 | 当前状态 |
|---|---|---|---|
{relevant_files}

## 5. 核心业务数据流路径与代码跳转 (Task-Specific Flowchart & Jump Table)
```mermaid
graph TD
{mermaid_business_flow}
```

| 步骤 | 节点类型 | 代码跳转锚点 (Click-to-Jump) | 数据转换与职责作用 |
|---|---|---|---|
{business_flow_steps}

## 6. 跨平台迁移依赖审计 (无相关性项目可跳过)
| 专属 API / 配置文件 | 引用次数 | 所在文件位置 | 目标平台替代技术方案 |
|---|:---:|---|---|
{platform_dependencies}

## 7. 本轮进度与已完成/未完成清单 (强制状态前缀规范)
*前缀规则：`✅ 已完成` (代码已存在), `🔄 进行中` (部分代码存在), `📋 规划中` (零代码仅讨论), `⚠️ 受阻` (开发阻塞)*

- **本轮已完成**:
{completed_work}

- **尚未完成内容**:
{remaining_work}

## 8. 已废弃代码（v1 遗留 / 孤立类）
{obsolete_code}

## 9. 当前错误 / 阻塞点
{current_errors}

## 10. 已确认结论与核心逻辑摘要
{confirmed_decisions}

## 11. 下一轮焦点 (Focus for Next Session)
{next_session_focus}

## 12. 已知问题与环境约束
{known_issues_summary}

## 13. 验证命令
```bash
{validation_commands}
```

## 14. 给接手 Agent 的项目特定硬约束
### 📚 必须阅读的文件
1. `.agent_handoff/project.zh-CN.md` — 项目核心设计与评分公式。
2. `.agent_handoff/decisions.zh-CN.md` — 关键架构决策背景。
3. `.agent_handoff/code-map.zh-CN.md` — 项目代码地图与物理调用图谱。

### 🚫 绝对不允许修改的内容
- 列出工程内高度敏感、绝对不可擅自修改的核心逻辑或配置文件。

### ⚠️ 代码设计陷阱与注意事项
- 列出具体的耦合陷阱（例如：“修改 A 接口结构会破坏 B 转换，请注意保持结构兼容”）。
