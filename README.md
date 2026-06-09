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

## 🚀 Installation & Setup

### 1. Online/Direct Installation
You can install the CLI tool directly from GitHub:
```bash
python3 -m pip install git+https://github.com/wangerpan/agent-context-handoff.git
```

### 2. Local Editable Installation (Development)
```bash
# Clone the repository
git clone https://github.com/wangerpan/agent-context-handoff.git
cd agent-context-handoff

# Install locally in editable mode
python3 -m pip install -e .
```

### 3. Manual Installation (No pip)
If you don't have Python pip or want a zero-dependency setup:
1. Download the source folder `agent_context_handoff` from this repository.
2. Copy it directly into your target project directory.
3. Run the CLI tool manually by calling the python module:
   ```bash
   python3 -m agent_context_handoff.cli --lang en
   ```

### 4. Agent-Assisted Installation
If you are currently pairing with a Coding Agent (e.g. Cline, Cursor, Antigravity, Claude Code), you can simply instruct the agent:
> *"Help me clone and install the agent-context-handoff package from GitHub https://github.com/wangerpan/agent-context-handoff.git"*
The agent will handle cloning, local setup, and package verification.

### 🗑️ Uninstallation
To remove the package and the command:
```bash
python3 -m pip uninstall agent-context-handoff
```

---

## 💻 How to Use

### Method A: Automated CLI Generation (Recommended)

Run the CLI in your target project root:
```bash
# Generate in English (default)
ai-context-handoff --lang en

# Generate in Chinese
ai-context-handoff --lang zh

# Specify target directory manually
ai-context-handoff --lang zh --dir /path/to/your/project
```

#### Detailed CLI Parameters:
* `--lang`: The document output language (`en` or `zh`).
* `--dir`: The workspace folder where `.ai-context/` will be generated (defaults to current directory `.`).

The CLI automatically performs:
- **Git State Capture**: Invokes git commands to retrieve modified files, lines, and logs.
- **Incremental Task Preserve**: If `.ai-context/current-task.md` already exists, it extracts and preserves your current custom `Objective` and `Task Checklist` blocks, instead of overwriting them.
- **Advanced Secret Scrubbing**: Scans files and output blocks for tokens, credentials, emails, and internal range IP addresses, replacing them with `<REDACTED_SECRET>` tags.
- **Indexing update**: Appends the Handoff indexes to `AGENTS.md`.

### Method B: Manual/Agent Prompt Integration
If you prefer your AI Agent to compile the markdown files directly via conversation:
1. Copy the contents of `agent_context_handoff/SKILL.md` (or `SKILL.zh-CN.md`).
2. Add the copied skill description into your agent's rule settings (e.g., `.cursorrules`, `.clinerules`, or system prompts).
3. Trigger the skill by prompting the agent with keywords:
   - *"context-handoff"* / *"agent-handoff"* / *"compress context"* / *"导出上下文"* / *"准备切换 Agent"*
4. (Optional) Instruct the agent to run `ai-context-handoff` directly to pre-populate files:
   > *"Run the handoff CLI and refine the results with our current status"*

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
