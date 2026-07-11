# SKILL: Agent Context Handoff

[English](SKILL.md) | [简体中文](SKILL.zh-CN.md)

## Description
Create a universal, tool-agnostic, and clean engineering context handoff package when switching coding agents. When triggered, compile the project state and write the context to `.agent_handoff/`.

---

## 🎯 Trigger Words
Trigger this skill when the user inputs any of the following keywords or intents:
- `context-handoff` / `agent-handoff` / `handoff`
- `compress context` / `export context` / `prepare handoff` / `switch agent`
- `准备切换 Agent` / `交接` / `导出上下文`

---

## 📋 Core Instructions

When triggered, you must perform project classification and pre-write verifications before writing the context files to **`.agent_handoff/agent-handoff.md`** (or `agent-handoff.zh-CN.md` for Chinese).

### 0. Project Type Detection (Before Template Filling)
First, identify the project type. Skip sections that are not applicable to avoid bloated documentation:
- **Chrome Extension**: Include Platform Dependency Audit (API mapping). Skip MCP / Screen sections.
- **Web App**: Include Tech Stack & Deployments. Skip MCP / Screen / Agent Classification.
- **CLI Tool**: Include Command entry point and dependencies. Skip MCP / Screen / Agent Classification.
- **Library / SDK**: Include Public APIs and version policies. Skip Runtime Status section completely.
- **Agent Plugin / Tool (OpenCode/ClaudeCode)**: Include all sections.

### 0. Pre-Write Verification Gate (Mandatory)
Before compiling or writing ANY content to the handoff files, you must run the following checks and verify that your planned claims are backed by codebase evidence:
1. **Evidence Check**: For every claim like "Implemented X" or "Supports Y", grep the codebase. If no matches are found, you must classify the item as `📋 Planned` (Planned, zero code) or `🔄 In Progress`, NOT `✅ Completed`.
2. **Line Count Verification**: Fetch actual line counts of key changed files using count commands (do not guess).
3. **Function/Symbol Validation**: Verify that any function, class, or API names you document actually exist in the files.
4. **Platform Coupling Scan**: Check for platform-specific APIs (e.g. `chrome.*`, `localStorage`, `process.env`) to document coupling.

### 0. Continuous Whiteboard Sync & Self-Evolving Rules (Conversational Memory)
To keep the context as a living conversation memory:
1. **Continuous Syncing**: You MUST update `.agent_handoff/current-task.md` (checklists/focus) and `.agent_handoff/decisions.md` (agreed design decisions) immediately in the current turn when progress is made, rather than waiting for the end of the session.
2. **Self-Evolving Rules**: If you and the developer agree on a new coding standard, design rule, or file constraint during the conversation, you MUST immediately modify `.cursorrules` or `.clinerules` to add the rule, locking it in for future turns of the conversation.

### 1. Enforced Task Progress Prefixes
Every status entry in the completed or remaining task sections must use one of the following prefixes. Statements without prefixes are forbidden:
- `✅`: Completed (Code exists in workspace and is verified via grep).
- `🔄`: In Progress (Partial code exists; list the relevant file paths).
- `📋`: Planned (Zero code exists; log the target schedule or discussion date).
- `⚠️`: Blocked (Work is stuck; explain active obstacles).

### 2. Mandatory Handoff Structure Checklist
Every generated handoff document must include these fixed sections:
- **Handoff Metadata & Reading Priority**: Current timestamp, Git Commit SHA, and a prioritized reading order table (e.g. 1. File Audit, 2. Decisions, 3. Run Commands) to guide the incoming agent.
- **Current State (Runtime Status)**:
  - Document active agent classifications, MCP server states, and active background/managed screen session counts (Skip if N/A for project type).
- **Core Artifact Paths & Size Audit**: Key changed files, their roles, current statuses, and actual physical line counts.
- **Critical Code Path & Business Flow**: Graphic flowcharts (Mermaid syntax) and repository-relative file/symbol jump tables with line numbers.
- **Platform Dependency Audit**: (Required for cross-platform/migration projects) Table of platform-specific APIs (e.g. `chrome.storage.local`) and their target equivalents (e.g. `localStorage`).
- **Prerequisite Background Launch Guides**: Explicitly document if background screen sessions (e.g. `screen -r`) require trigger calls (such as `/config` or `/cli` POST requests) before they can be attached.
- **Startup / Validation Commands**: Provide runnable command blocks to start, test, or verify the application.
- **Key Decisions Summary & Legacy Code Audit**:
  - Summarize critical architectural and domain logic decisions. Refer to file paths and brief comments instead of full source code duplication.
  - Scan for orphaned/unused legacy files and document them in an Obsolete Code list.
- **Known Limits & Service States**: Document environmental gotchas, dependency constraints, and tag known offline services (e.g. `headroom` offline).
- **Project-Specific Constraints (Incoming Agent Requirements)**: Replace generic boilerplate rules with project-specific instructions (e.g. Must-Read files, files that are absolutely not allowed to be modified, and core logic traps).

### 3. Avoid Hardcoded Magic Numbers
Do NOT write down fixed numbers for dynamically changing system metrics (e.g., active agent counts, session line counts, or output lists) inside the handoff descriptions or validation instructions. Use **descriptive assertions** (e.g. "Returns list of active agents" instead of "Returns exactly 17 agents").

### 4. CLI Tool Integration (Recommended)
If the CLI tool is available in the target workspace (e.g. `agent-context-handoff` or `python3 -m agent_context_handoff.cli`), run it first to automatically generate or update the `.agent_handoff/` directory structure, run tests, and package context:
```bash
# Specifying language, next session focus, enabling code/API scanning, running tests, and XML packaging
agent-context-handoff --lang en --focus "Next session focus" --scan --test "pytest" --pack
```
Before packaging or sharing, run `agent-context-handoff lint --dir <project>`. If it reports stale branch, commit, or timestamp metadata, re-check the current workspace before regenerating. Use `--mode analysis|fix|review|handoff` to constrain the incoming agent prompt.
After execution, manually refine the fields with specific context details. Direct downstream agents to read the packaged XML block (`.agent_handoff/packaged-context.xml`) to absorb all context in a single token-efficient step.

### 5. Redaction of Sensitive Data
Sanitize all outputs. Replace sensitive strings with:
- Access Tokens / API Keys / Secrets -> `<REDACTED_SECRET>`
- Passwords -> `<REDACTED_PASSWORD>`
- Private Keys -> `<REDACTED_PRIVATE_KEY>`
- Production Databases -> `<REDACTED_PROD_DB>`
- Personal Phones / Emails -> `<REDACTED_PHONE>` / `<REDACTED_EMAIL>`
- Internal Hosts -> `<REDACTED_INTERNAL_HOST>`
- Session Cookies -> `<REDACTED_COOKIE>`

---

## 📝 Output Document Specifications

### `.agent_handoff/agent-handoff.md`
Must follow the layout:
1. **⚡ Reading Order Priority Table**: Guides the incoming agent on what to read first.
2. **📌 Metadata & Git Tracking Info**: Timestamp, commit SHA, session info.
3. **Current Task**: Objective of the current step.
4. **Current State (Runtime Status)**: Active agents classification list, online/offline MCPs, active screens (Skip if N/A).
5. **Project Context & Tech Stack**: High-level background, key languages and frameworks.
6. **Relevant Modules & Files**: Table of files, purpose, status (using ✅/🔄/📋/⚠️), and physical line counts.
7. **Critical Code Path & Business Flow**: Mermaid sequence/flowcharts and clickable symbol steps table.
8. **Platform Dependency Audit**: Table of platform API references and mapping (Skip if N/A).
9. **Work Completed / Remaining**: Lists of achievements and pending items with prefix state symbols.
10. **Obsolete / Legacy Code**: Scan results for unused files or deprecated paths.
11. **Current Errors / Blockers**: Active errors.
12. **Confirmed Decisions**: Architectural choices with concise summaries and repository-relative file references.
13. **Focus for Next Session**: Dedicated section describing next steps or user-defined targets.
14. **Known Issues & Environmental Limits**: Document environmental constraints, and tag known offline services.
15. **Validation Commands**: Execute blocks containing dynamic assertions.
16. **Specific Constraints for Incoming Agent**: (Must Read, Cannot Modify, Logic Traps).
