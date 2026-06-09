# SKILL: Agent Context Handoff

[English](SKILL.md) | [简体中文](SKILL.zh-CN.md)

## Description
Create a universal, cross-agent engineering context handoff package.

---

## 🎯 Trigger Words
Trigger this skill when the user inputs any of the following:
- `context-handoff` / `agent-handoff` / `handoff`
- `compress context` / `export context` / `prepare for next agent` / `prepare handoff`
- `generate context pack` / `switch agent`

---

## 📋 Core Instructions

When triggered, compile the active workspace status into a structured context bundle under the `.ai-context/` directory in the project root. The main handoff file must be written to **`.ai-context/agent-handoff.md`** (or `agent-handoff.zh-CN.md` for Chinese).

### 1. Mandatory Handoff Structure Checklist
Every generated handoff document must include these fixed sections:
- **Git Tracking Info**: Include the current timestamp and target Git Commit SHA.
- **Current State (Runtime Status)**:
  - Document active agent classifications (e.g. built-in vs dynamic/extendable counts).
  - Document MCP server states (online / offline).
  - Document active background/managed screen session counts.
- **Core Artifact Paths**: Map key changed files, their roles, and current statuses.
- **Prerequisite Background Launch Guides**: Explicitly document if background screen sessions (e.g. `screen -r`) require trigger calls (such as `/config` or `/cli` POST requests) before they can be attached.
- **Startup / Validation Commands**: Provide runnable command blocks to start, test, or verify the application.
- **Key Decisions Summary**: Summarize critical architectural and domain logic decisions. Refer to file paths and brief comments instead of full source code duplication.
- **Known Limits & Service States**: Document environmental gotchas, dependency constraints, and explicitly tag known offline services (e.g. `headroom` offline) so incoming agents don't attempt to use them.
- **Focus for Next Session**: Incorporate the user's focus parameter (if specified).

### 2. Avoid Hardcoded Magic Numbers
Do NOT write down fixed numbers for dynamically changing system metrics (e.g., active agent counts, session line counts, or output lists) inside the handoff descriptions or validation instructions. Use **descriptive assertions** (e.g. "Returns list of active agents" instead of "Returns exactly 17 agents").

### 3. Dynamic Assertions in Validation
All verification and validation checklists must use dynamic assertions rather than static line-count or word-count checks:
* Prefer: `curl -s .../agents | grep -q "agents"` or verifying the response body is non-empty.
* Avoid: `curl -s .../agents | wc -l` expecting a static count (e.g. checking if it equals `17`).

### 4. CLI Tool Integration (Recommended)
If the CLI tool is available in the target workspace (e.g. `ai-context-handoff` or `python3 -m agent_context_handoff.cli`), run it first to automatically generate or update the `.ai-context/` directory structure:
```bash
# Specifying language and next session focus
ai-context-handoff --lang en --focus "Describe the focus for the incoming agent"
```
After execution, manually refine the fields with specific context details.

### 5. Redaction of Sensitive Data
Sanitize all outputs. Replace sensitive strings with:
- Access Tokens / API Keys / Secrets -> `<REDACTED_SECRET>`
- Passwords -> `<REDACTED_PASSWORD>`
- Private Keys -> `<REDACTED_PRIVATE_KEY>`
- Production Databases -> `<REDACTED_PROD_DB>`
- Personal Phones / Emails -> `<REDACTED_PHONE>` / `<REDACTED_EMAIL>`
- Internal Hosts -> `<REDACTED_INTERNAL_HOST>`
- Session Cookies -> `<REDACTED_COOKIE>`

### 6. Verification Step (Self-Audit)
Before completing the handoff, you must:
1. Cross-check your compiled documentation against the actual `git diff` and workspace code.
2. Confirm that critical criteria (e.g., specific file paths, configuration changes, or flags) match your written descriptions. Correct any discrepancies.

---

## 📝 Output Document Specifications

### `.ai-context/agent-handoff.md`
Must follow the layout:
1. **Metadata**: Traceability fields (timestamp, commit SHA, session info).
2. **Current Task**: Objective of the current step.
3. **Current State (Runtime Status)**: Active agents classification list, online/offline MCPs, active screens.
4. **Project Context**: High-level background.
5. **Tech Stack**: Key languages and frameworks.
6. **Relevant Modules & Files**: Table of files and status.
7. **Work Completed / Remaining**: Lists of achievements and pending items.
8. **Current Errors / Blockers**: Active errors.
9. **Confirmed Decisions**: Architectural choices (concise summaries with file link references like `[filename](file:///path/to/file#L123)`).
10. **Focus for Next Session**: Dedicated section describing next steps or user-defined targets.
11. **Known Issues & Environmental Limits**: Document environmental constraints, and tag known offline services.
12. **Validation Commands**: Execute blocks containing dynamic assertions.
13. **Requirements for Incoming Agent**.
