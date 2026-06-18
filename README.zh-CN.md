# Agent Context Handoff (跨 Agent 上下文交接)

[English](README.md) | [简体中文](README.zh-CN.md)

一个通用的、不绑定工具的 CLI 工具与系统提示词方案。它可以自动对项目状态进行打包和敏感信息脱敏，实现不同 Coding Agent（Cursor、Claude Code、Cline、Roo Code 等）之间的无缝任务交接。

---

## 📂 目录结构

```
.agent_handoff/              # 自动生成的交接目录
├── packaged-context.xml     # 统一打包的 XML 上下文（推荐接手入口）
├── code-map.md              # 项目静态地图（架构入口与 Mermaid 依赖拓扑）
├── README.md               # 目录文件职责说明
├── project.md              # 项目技术栈与构建指南说明
├── current-task.md         # 任务清单与进度状态 (支持增量保留，避免覆盖)
├── agent-handoff.md        # 主交接核心说明文档与业务流路径锚点
├── changed-files.md        # Git 状态与代码变更统计
├── decisions.md            # 技术与架构决策记录
├── known-issues.md         # 已知坑点与环境约束
├── validation.md           # 自动化测试与手动验证步骤
└── next-agent-prompt.md    # 专为接手 Agent 编写的 Prompt 引导语
```
*注：该工具还会自动在工程根目录的 `AGENTS.md` 中追加索引入口。*

---

## 🚀 安装部署

**前置要求**：Python 3.6+ (带有 `pip` 模块)，安装有 Git。

| 安装方式 | 执行命令 | 适用场景 |
|---|---|---|
| **线上直接安装** | `pip install git+https://github.com/wangerpan/agent-context-handoff.git` | 快捷使用 |
| **本地开发安装** | `git clone <repo> && pip install -e .` | 需要修改本工具代码 |
| **手动拷贝安装** | 直接下载 `agent_context_handoff` 目录至目标工程 | 无 pip 依赖环境 |
| **Agent 自动安装** | 对 Agent 输入：*“帮我克隆并安装 git+https://github.com/wangerpan/agent-context-handoff.git”* | 免动手安装 |

*卸载命令：`pip uninstall agent-context-handoff`*

---

## 💻 使用方法

### 方法 A：命令行 CLI 自动生成（推荐）
在目标工程根目录下执行：
```bash
# 生成英文版，启用平台与依赖扫描、运行 pytest 测试并打包 XML
agent-context-handoff --lang en --scan --test "pytest" --pack

# 生成中文版（并指定目录）
agent-context-handoff --lang zh --dir /path/to/project --scan --test "pytest" --pack
```
* CLI 工具会自动统计 Git 变更，**智能提取并保留原有的任务清单与目标**，并对敏感信息（API Key、Token、邮箱、内网 IP 等）进行自动脱敏过滤，替换为 `<REDACTED_SECRET>`。
* `--scan` 会扫描工程中平台专属的 API 引用（如 `chrome.*`），解析第三方包依赖，并生成静态架构索引 `code-map.md`。
* `--test` 会自动在当前项目运行指定的测试指令，并将执行输出（stdout/stderr）和结果写入 `validation.md`。
* `--pack` 会将当前语言的所有 `.agent_handoff` 交接文档打包进单一的 XML 文件（`.agent_handoff/packaged-context.xml` 或 `.zh-CN.xml`），从而提高后续接手 Agent 的 Token 吸收率与速度。

### 方法 B：Agent 系统规则集成
1. 复制项目中的 [SKILL.zh-CN.md](agent_context_handoff/SKILL.zh-CN.md) 或 [SKILL.md](agent_context_handoff/SKILL.md)。
2. 将内容整合进 Agent 的规则文件（如 `.cursorrules`、`.clinerules` 或 System Prompts）。
3. 对话中通过输入触发词唤醒 Agent：`context-handoff`、`准备切换 Agent`、`压缩上下文`、`导出交接文档`。

---

## 📄 开源协议
采用 MIT 许可证，详情请参阅 [LICENSE](LICENSE)。
