# Agent Context Handoff - 综合优化与整改建议方案

本方案结合了 Codex 的评审反馈与 Antigravity 针对最新代码库（`main` 分支）的深度静态分析，对 `agent-context-handoff` 工具在安全性、健壮性、标准规范以及测试完备度上提出全面的优化与整改意见。

---

## 📋 核心整改项汇总表

| 整改模块 | 具体问题表现 | 风险与影响 | 整改优先级 | 建议实施方案 |
| :--- | :--- | :--- | :--- | :--- |
| **标准 Skill 规范** | `skills/agent-context-handoff/SKILL.md` 中依然将路径写为旧版的 `.ai-context/`。 | 引导 Agent 执行时生成错误目录，破坏 `.agent_handoff/` 的统一隔离命名空间。 | **🔴 高** | 更新 `SKILL.md` 文件中所有硬编码的 `.ai-context/` 为 `.agent_handoff/`。 |
| **二次脱敏安全防御** | XML 打包时直接读取物理文件并组装，若人工编辑过且未脱敏，敏感词可能会泄露至打包文件。 | 人工编辑引入的 API Key 或内部 Host 随 XML 打包泄露。 | **🔴 高** | 在 `package_context` 读取文件内容后，组装前强制调用 `redact_secrets()`。 |
| **防止模版内容虚构** | 首次生成时，`project.md`、`decisions.md` 等文档写入了大量虚构的占位符（如 `headroom` 离线等）。 | 干扰新 Agent 的判断，使其误以为项目存在特定离线服务或历史设计。 | **🟡 中** | 移除非普适性的虚构占位内容，改为纯结构占位或提取真实环境变量。 |
| **命令错误与执行安全** | `--test` 选项使用 `shell=True` 执行；`run_command` 隐藏了非零退出码和 stderr。 | 带来命令注入安全隐患，且无法有效传播测试失败的详细调用链。 | **🟡 中** | 1. 废弃 `shell=True`，使用参数数组执行测试命令。<br>2. 在 `validation.md` 中显式记录 stderr 和退出状态码。 |
| **链接一致性与死链** | 在单语言模式下生成文档时，可能会在 `next-agent-prompt` 等模版中留下失效的双语链接。 | 导致 downstream Agent 在点击时遇到找不到文件的错误。 | **🟡 中** | 在渲染模版时，根据当前的 `--lang` 动态剔除或转换非当前语言的链接。 |
| **自动化测试完备度** | 测试套件缺少对 `--force`、脱敏穿透、非零退出码传播、`--pack` 打包的单元验证。 | 重构或迭代 CLI 时容易引入破坏性变更而不自知。 | **🟢 低** | 在 `tests/test_cli.py` 中补充端到端的参数组合与断言测试。 |
| **代码健壮性与性能** | 1. 未限制扫描文件的最大大小，读取超大文件易 OOM。<br>2. 正则表达式未预编译。<br>3. `os.path` 与 `pathlib` 混用。 | 扫描大项目时运行缓慢或崩溃；代码风格不统一。 | **🟢 低** | 1. 限制扫描的文件大小上限（例如 1MB）。<br>2. 预编译 `SECRET_PATTERNS`。<br>3. 统一重构为 `pathlib.Path`。 |

---

## 🛠️ 关键模块代码修改示意

### 1. XML 打包二次脱敏防御 (XML Packaging Defense in Depth)

```python
# agent_context_handoff/cli.py - package_context() 函数优化
def package_context(ai_context_dir, target_dir, lang):
    # ...
    for entry in files_to_pack:
        file_path = os.path.join(ai_context_dir, entry)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 强化安全防御：组装 XML 前再次脱敏，防止人工编辑污染
            content = redact_secrets(content)
            escaped = content.replace("]]>", "]]]]><![CDATA[>")
            # ...
```

### 2. 标准 Skill 路径修正 (Standard Skill Path Correction)

```markdown
<!-- skills/agent-context-handoff/SKILL.md -->
# Agent Context Handoff

Create an agent-neutral, evidence-based handoff under `.agent_handoff/`. Preserve human-authored context and distinguish verified facts from unknowns.
...
- Keep `AGENTS.md` short; detailed state belongs in `.agent_handoff/`.
```

---

## 📈 后续执行计划

1. **第一阶段：热修复 (Hotfix)**
   - 修正 `SKILL.md` 中所有残留的 `.ai-context/` 引用。
   - 对 XML 打包逻辑添加 `redact_secrets` 二次脱敏过滤。
2. **第二阶段：健壮性加固 (Hardening)**
   - 重构 `--test` 机制，支持数组参数执行并正确记录非零退出状态码。
   - 清理所有模板文件中的虚构占位信息。
3. **第三阶段：测试补充 (Testing)**
   - 编写 `test_packaging_redaction` 测试用例，确保 XML 打包敏感信息无法穿透。
   - 编写并发/大文件扫描稳定性测试。

---

## 💡 借鉴与融合：CodeGraph 与 Codebase Memory MCP

为了进一步提升 `agent-context-handoff` 的深度和效能，我们对业界主流的两个代码库上下文映射与记忆工具——**CodeGraph** 与 **Codebase Memory MCP** 的设计模型与优点进行了调研整理，并据此提炼出对本工具的改进方向。

### 1. CodeGraph 设计模型与优点
CodeGraph（如 `colbymchenry/codegraph` 等实现）采用基于语法树的静态分析机制：
* **AST 级符号映射**：不依赖简单的纯文本 `grep`，而是通过 AST（如 Tree-sitter）对代码结构进行解析，精准识别类（Class）、函数（Function/Method）、导入/导出（Imports/Exports）的定义与调用关系。
* **依赖 blast radius（变更波及范围）分析**：通过有向无环图（DAG）追踪依赖方向，使 Agent 能够一键查询 “修改此函数会波及哪些上游调用方”。
* **API 与路由映射**：将外部路由（如 HTTP 路由/事件订阅入口）与底层的业务逻辑处理器（Handlers）强关联绑定，帮助 Agent 快速定位请求处理链路。

### 2. Codebase Memory MCP 设计模型与优点
Codebase Memory MCP 侧重于高性能本地记忆与上下文代理：
* **本地高性能图存储（SQLite + RAM-first）**：将扫描得到的符号与关系存入轻量级 SQLite 中，配合内存缓存与哈希对比实现增量索引，查询响应通常低于 1ms，支持 Linux 内核级的大型项目。
* **Leiden 社区发现算法**：通过图聚类算法自动划定模块/子系统的边界，帮 Agent 辨识高复杂度与高耦合的“核心热点区域”。
* **架构决策记录（ADR）深度集成**：显式维护和持久化 ADR，使技术决策和上下文约束在跨工具、跨会话时保持连续。
* **高 Token 吞吐效率**：相比全量载入文件，通过图查询仅把必要的依赖和关系反馈给 LLM，能节省多达 99% 的 Context Token。

---

## 🚀 改进 agent-context-handoff 的融合方案

结合上述工具的优点，`agent-context-handoff` 可以在保持“轻量、无依赖、免配置”的前提下，进行以下维度的演进：

### A. 升级 code-map 生成至“准 AST 符号解析”（借鉴 CodeGraph）
* **现状**：目前 `cli.py` 依靠简单的文本正则提取局部 symbol 和 import 关系。
* **改进**：
  1. 在 `cli.py` 中引入 Python 自带的 `ast` 模块解析 Python 文件；对 JS/TS 等文件，采用增强的词法状态扫描。
  2. 提取更精准的 `Caller -> Callee`（调用者 -> 被调用者）拓扑，将简单的 Mermaid 模块级依赖图升级为**关键业务流时序图**。

### B. 引入文件哈希与增量扫描机制（借鉴 Codebase Memory MCP）
* **现状**：每次执行 `ai-context-handoff` 都会重新扫码整个 codebase，对于大型项目耗时较长。
* **改进**：
  1. 在 `.agent_handoff/` 下增设一个轻量级哈希对照表（`.checksums`）。
  2. 每次运行时，仅扫描哈希发生变化的文件，对 `code-map.md` 进行增量刷新，实现亚秒级的极速分析。

### C. 结构化 ADR (Architecture Decision Record) 日志（借鉴 Codebase Memory MCP）
* **现状**：当前的 `decisions.md` 是一个松散的 Markdown 描述。
* **改进**：
  1. 将 `decisions.md` 规范化为标准的 **ADR** 格式（包含 `Title`、`Context`、`Decision`、`Status (Accepted/Proposed)`、`Consequences`）。
  2. 在 Skill 指令中，要求接手 Agent 修改架构设计前必须先读取此 ADR 链，杜绝与历史决策冲突的重复返工。

### D. web API 路由与业务入口的显式锚定
* **现状**：难以直观映射外部接口与内部函数的联系。
* **改进**：
  1. 在静态扫描中，针对主流 web 框架（如 FastAPI、Express 等）的路由装饰器进行特殊识别。
  2. 在 `code-map.md` 中增加 **HTTP/Event 路由表**，并将路由跳转链接通过绝对路径定位到具体文件行号，例如：`POST /api/v1/handoff` -> `agent_context_handoff/cli.py#L190`。

