# Agent Context Handoff Skill

[English](README.md) | [简体中文](README.zh-CN.md)

A universal, agent-neutral context handoff skill and CLI tool to compress active project contexts into clean markdown files, enabling coding agents (such as Cursor, Antigravity, Claude Code, Cline, Roo Code, etc.) to seamlessly hand over tasks to each other.

---

## 🌟 Overview

When working with Coding Agents, switching from one agent to another (or starting a new session) often leads to context loss. This project implements a standardized **Context Handoff Skill** that packages:
- Current task status and objectives
- Recent code changes and summaries (via git status/diff)
- Key architectural & business decisions
- Known issues/blockers
- Validation steps and commands
- A prompt tailored for the incoming agent to read the context first before editing any code

---

## 📂 Project Structure

```
agent-context-handoff/
├── SKILL.md                 # English Skill instructions for agents
├── SKILL.zh-CN.md           # Chinese Skill instructions for agents
└── templates/               # Standard context file templates
    ├── agent-handoff-template.md (.zh-CN.md)
    ├── current-task-template.md (.zh-CN.md)
    ├── changed-files-template.md (.zh-CN.md)
    ├── decisions-template.md (.zh-CN.md)
    ├── known-issues-template.md (.zh-CN.md)
    ├── validation-template.md (.zh-CN.md)
    ├── next-agent-prompt-template.md (.zh-CN.md)
    └── agents-section-template.md (.zh-CN.md)
```

Generated folder structure inside the target project:
```
TargetProject/
├── AGENTS.md                # Entry point and index for all AI context files
└── .ai-context/             # Handoff context folder (ignored by git or committed for sharing)
    ├── README.md            # Explains folder purpose and usage
    ├── project.md           # Project background, tech stack, and build commands
    ├── current-task.md      # Summary of current task status
    ├── agent-handoff.md     # Main context handoff documentation
    ├── changed-files.md     # Git status & diff summary
    ├── decisions.md         # Key engineering & domain decisions
    ├── known-issues.md      # Obstacles and environmental limits
    ├── validation.md        # Command checklists and validation results
    └── next-agent-prompt.md # Quick handoff prompt for the next agent
```

---

## 🚀 How to Use

### 1. Programmatic CLI Usage

You can use the Python CLI tool to automatically generate the `.ai-context` files from your project's Git status and templates.

#### Installation

You can install the CLI tool directly from GitHub:
```bash
python3 -m pip install git+https://github.com/wangerpan/agent-context-handoff.git
```

Alternatively, for local development:
```bash
# Clone the repository
git clone https://github.com/wangerpan/agent-context-handoff.git
cd agent-context-handoff

# Install locally in editable mode
python3 -m pip install -e .
```

#### Uninstallation
To remove the package and the CLI command:
```bash
python3 -m pip uninstall agent-context-handoff
```

#### Running the CLI
Run the CLI in your target project root:
```bash
# Generate in English (default)
ai-context-handoff --lang en

# Generate in Chinese
ai-context-handoff --lang zh
```
The CLI automatically:
- Parses `git status`, `git diff`, and recent logs.
- Redacts sensitive information (tokens, API keys, passwords) replacing them with placeholders like `<REDACTED_SECRET>`.
- Creates or updates `.ai-context/` files.
- Appends the Handoff index section to `AGENTS.md` if it doesn't already exist.

### 2. Manual/Agent Prompt Skill Usage

If you prefer to have the AI Agent write and compress the handoff documents directly:
1. Copy the contents of `agent_context_handoff/SKILL.md` (or `SKILL.zh-CN.md`).
2. Add it to your agent's system instructions (e.g., `.cursorrules`, `.clinerules`, custom system prompt).
3. Trigger the skill by prompting the agent with trigger words:
   - *"context-handoff"* / *"agent-handoff"*
   - *"compress context"* / *"export context"* / *"prepare for next agent"*

---

## 🔒 Security & Secrets Redaction

The CLI and agent instructions strictly enforce stripping sensitive credentials. Any matching patterns of the following will be redacted:
- API Keys & Access Tokens
- Passwords & Private Keys
- Production Database URLs
- SSH Private Keys, Cookies, and Session identifiers

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
