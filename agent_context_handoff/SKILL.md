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
- **Git Tracking Info**: Include the current timestamp and target Git Commit SHA for context traceability.
- **Core Artifact Paths**: Map key changed files, their roles, and current statuses.
- **Startup / Validation Commands**: Provide runnable command blocks to start, test, or verify the application.
- **Current State**: Mark task progress clearly (Completed / In Progress / Blocked).
- **Key Decisions Summary**: Summarize critical architectural and domain logic decisions. Refer to file paths and brief comments instead of full source code duplication.
- **Known Limits**: Document environmental gotchas and dependency constraints.
- **Focus for Next Session**: Incorporate the user's focus parameter (if specified) into a dedicated section.

### 2. CLI Tool Integration (Recommended)
If the CLI tool is available in the target workspace (e.g. `ai-context-handoff` or `python3 -m agent_context_handoff.cli`), run it first to automatically generate or update the `.ai-context/` directory structure:
```bash
# Specifying language and next session focus
ai-context-handoff --lang en --focus "Describe the focus for the incoming agent"
```
After execution, manually refine the fields with specific context details.

### 3. Redaction of Sensitive Data
Sanitize all outputs. Replace sensitive strings with:
- Access Tokens / API Keys / Secrets -> `<REDACTED_SECRET>`
- Passwords -> `<REDACTED_PASSWORD>`
- Private Keys -> `<REDACTED_PRIVATE_KEY>`
- Production Databases -> `<REDACTED_PROD_DB>`
- Personal Phones / Emails -> `<REDACTED_PHONE>` / `<REDACTED_EMAIL>`
- Internal Hosts -> `<REDACTED_INTERNAL_HOST>`
- Session Cookies -> `<REDACTED_COOKIE>`

### 4. Verification Step (Self-Audit)
Before completing the handoff, you must:
1. Cross-check your compiled documentation against the actual `git diff` and workspace code.
2. Confirm that critical criteria (e.g., specific file paths, configuration changes, or flags) match your written descriptions. Correct any discrepancies.

---

## 📝 Output Document Specifications

### `.ai-context/agent-handoff.md`
Must follow the layout:
1. **Metadata**: Traceability fields (timestamp, commit SHA, session info).
2. **Current Task**: Objective of the current step.
3. **Project Context**: High-level background.
4. **Tech Stack**: Key languages and frameworks.
5. **Relevant Modules & Files**: Table of files and status.
6. **Work Completed / Remaining**: Lists of achievements and pending items.
7. **Current Errors / Blockers**: Active errors.
8. **Confirmed Decisions**: Architectural choices (concise summaries with file link references like `[filename](file:///path/to/file#L123)`).
9. **Focus for Next Session**: Dedicated section describing next steps or user-defined targets.
10. **Validation Commands**: Execute blocks.
11. **Requirements for Incoming Agent**.
