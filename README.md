# Agent Context Handoff

[English](README.md) | [简体中文](README.zh-CN.md)

A universal, agent-neutral CLI tool and system prompt to pack, strip secrets, and handover active project context between AI Coding Agents (Cursor, Claude Code, Cline, Roo Code, etc.).

---

## 📂 Layout

```
.agent_handoff/              # Generated handoff directory
├── packaged-context.xml     # Unified XML context bundle (recommended entry point)
├── state.json               # Snapshot branch, commit, timestamp, and language
├── code-map.md              # Project static map (structure & dependencies flowchart)
├── README.md               # Folder description
├── project.md              # Tech stack & build guidelines
├── current-task.md         # Checklist & task state (preserved incrementally)
├── agent-handoff.md        # Core handoff notes & business flow anchors
├── changed-files.md        # Git status & diff summary
├── decisions.md            # Architecture decisions log
├── known-issues.md         # Gotchas & active blockers
├── validation.md           # Verify scripts & status
└── next-agent-prompt.md    # Instructions copy-paste for the next agent
```
*Note: The CLI also automatically registers entries in `AGENTS.md` at the project root.*

---

## 🚀 Installation & Setup

**Prerequisites**: Python 3.6+ (with `pip`), Git.

| Method | Command | Description |
|---|---|---|
| **Direct (GitHub)** | `pip install git+https://github.com/wangerpan/agent-context-handoff.git` | Quick setup |
| **Local (Dev)** | `git clone <repo> && pip install -e .` | Editable development |
| **Manual (No pip)** | Copy `agent_context_handoff` folder to target dir | Call as python module |
| **Agent-assisted** | Ask agent: *"Clone and install git+https://github.com/wangerpan/agent-context-handoff.git"* | Hands-free install |

*Uninstall command: `pip uninstall agent-context-handoff`*

---

## 💻 How to Use

### Method A: Automated CLI Generation (Recommended)
Run inside target project root:
```bash
# Generate (Default: English) with Platform & Dependency scanning, Test run, and XML packaging
agent-context-handoff --lang en --scan --test "pytest" --pack

# Generate in Chinese (Alternative directory)
agent-context-handoff --lang zh --dir /path/to/project --scan --test "pytest" --pack

# Check freshness and content safety; use --json in automation
agent-context-handoff lint --dir /path/to/project

# Check installation and handoff health
agent-context-handoff doctor --dir /path/to/project
```
* CLI automatically scans Git status/diff, **preserves customized objectives & checklist** in `current-task.md`, and redacts secrets (tokens, keys, emails, private IPs) into `<REDACTED_SECRET>`.
* `--scan` parses platform API references, extracts third-party dependencies, and generates the static architecture index `code-map.md`.
* `--mode analysis|fix|review|handoff` tailors the incoming-agent prompt to the authorized work mode.
* `--refresh` updates generated task metadata while preserving the objective, checklist, and focus written by humans or agents.
* `lint` detects stale branch/commit/timestamps, obsolete `.ai-context` references, non-portable links, and unverified example claims. `doctor` adds CLI version and environment health.
* `--test` runs the supplied string through the local shell and logs results in `validation.md`. Treat it as trusted local input; never pass untrusted text.
* `--pack` compiles all active markdown context files into a token-efficient, redacted XML bundle at `.agent_handoff/packaged-context.xml` (or `.zh-CN.xml`).
* Redaction is defense in depth, not proof of safety. Review the final bundle before sharing it outside its trust boundary.

### Method B: System Instruction Integration
1. Copy [SKILL.md](agent_context_handoff/SKILL.md) / [SKILL.zh-CN.md](agent_context_handoff/SKILL.zh-CN.md).
2. Add contents into agent instructions (`.cursorrules`, `.clinerules`, system prompts).
3. Trigger by typing: `context-handoff`, `handoff`, `压缩上下文`, `准备切换 Agent`.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
