# SKILL: Agent Context Handoff

[English](SKILL.md) | [简体中文](SKILL.zh-CN.md)

## Description
Create a universal cross-agent engineering context handoff package.

---

## 🎯 Trigger Words
Trigger this skill when the user inputs any of the following:
- `context-handoff` / `agent-handoff` / `handoff`
- `compress context` / `export context` / `prepare for next agent` / `prepare handoff`
- `generate context pack` / `switch agent`

---

## 📋 Core Instructions

When triggered, you must compile the active workspace status into a structured context bundle under the `.ai-context/` directory in the project root. Your output must remain **Agent-neutral** and avoid assuming the next tool's identity.

### 1. File Structure to Maintain
Ensure the target project has the following file structure. If files do not exist, create them. If they do exist, update their content based on current progress.

```
TargetProject/
├── AGENTS.md
└── .ai-context/
    ├── README.md
    ├── project.md
    ├── current-task.md
    ├── agent-handoff.md
    ├── changed-files.md
    ├── decisions.md
    ├── known-issues.md
    ├── validation.md
    └── next-agent-prompt.md
```

### 2. CLI Tool Integration
If the CLI tool is available in the target workspace (e.g. `ai-context-handoff` or `python3 -m agent_context_handoff.cli`), you should prioritize running it first to automatically generate or update the basic `.ai-context/` directory structure and git-related stats. After execution, you can manually open and refine the files (like `agent-handoff.md` and `current-task.md`) with more specific context details.

### 3. Git Integration
If a git repository is accessible, run the following commands to collect status and diff information:
- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- `git log --oneline -5`

> [!WARNING]
> Do NOT write large raw git diffs into the context files. Summarize the changes instead.

### 3. Redaction of Sensitive Data
You must scan the generated texts and sanitize any sensitive information. Replace them with standard redaction tokens:
- Access Tokens / API Keys / Secrets -> `<REDACTED_SECRET>`
- Passwords -> `<REDACTED_PASSWORD>`
- Private Keys -> `<REDACTED_PRIVATE_KEY>`
- Production Databases -> `<REDACTED_PROD_DB>`
- Personal Phones / Emails -> `<REDACTED_PHONE>` / `<REDACTED_EMAIL>`
- Internal Hosts -> `<REDACTED_INTERNAL_HOST>`
- Session Cookies -> `<REDACTED_COOKIE>`

### 4. Update index in AGENTS.md
If `AGENTS.md` does not exist, create it. If it exists but doesn't have an "AI Context Handoff" section, append the section to index `.ai-context/agent-handoff.md` and `.ai-context/README.md`. Keep `AGENTS.md` light as an entry-point index.

---

## 📝 Document Requirements

### agent-handoff.md
Must include:
1. **Current Task**: Brief objective of the current step.
2. **Project Context**: High-level context.
3. **Tech Stack**: Key languages and frameworks.
4. **Relevant Modules & Files**: A Markdown table mapping files, their purposes, and status.
5. **Completed Work**: Bullet points of what was achieved.
6. **Remaining Work**: What is left to do.
7. **Current Errors / Blockers**: Any active issues.
8. **Confirmed Decisions**: Final design choices.
9. **Pending Items**: Open questions or variables.
10. **Rejected Alternatives**: Solutions considered and why they were ruled out.
11. **Risk Points**: Potential issues to watch out for.
12. **Next Steps**: Specific actions for the incoming agent.
13. **Validation Commands**: Execution blocks for tests or runs.
14. **Requirements for Next Agent**:
    - Read `AGENTS.md` and `.ai-context/` files first.
    - Explain the task understanding before writing code.
    - Do not perform wide-scope refactoring unless requested.
    - Match project coding standards.

### next-agent-prompt.md
Provide a prompt block that the user can copy and paste directly to the next incoming coding agent. It instructs the new agent to read the documentation first and verify understanding before starting work.
