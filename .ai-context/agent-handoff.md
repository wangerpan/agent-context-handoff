# Agent Project Handoff Documentation

[English](agent-handoff.md) | [简体中文](agent-handoff.zh-CN.md)

## ⚡ Recommended Reading Order for Incoming Agent

| Priority | Section | Reason |
|:---:|---|---|
| 1 | **4. Relevant Modules & Files** | Establish physical structure understanding |
| 2 | **10. Confirmed Decisions** | Understand design intent & rationale |
| 3 | **13. Validation Commands** | Run tests and confirm environment is operational |
| 4 | **12. Known Issues & Limits** | Avoid stepping into known gotchas/traps |
| 5 | **1. Current Task & 11. Focus** | Understand what needs to be done next |

---

## 📌 Handoff Metadata
- **Generated At**: 2026-06-09 13:17:02
- **Git Commit SHA**: 7771fc696acf4f1f16b7aa3025c7b73df4c87c0d
- **Session / Trace ID**: N/A

---

## 1. Current Task
Develop/generate agent-context-handoff Skill

## 2. Current State (Runtime Status - Skip if N/A)
- **Active Agent Classifications**:
  - Built-in Agents: 17 (built-in) (Use descriptive assertions)
  - Understand-Anything Agents: 9 (understand-anything)
- **MCP Servers Status**:
  - Online MCPs: N/A
  - Offline MCPs (e.g. headroom): headroom [OFFLINE] / [离线]
- **Managed Background Screens**:
  - Active screen count: N/A
  - *Prerequisite*: Before attaching via `screen -r`, make sure they are started by invoking `/config` or `/cli` POST endpoint first.

## 3. Project Context & Tech Stack
Automated compression of Coding Agent context
- **Tech Stack**: Python / Shell / Markdown

## 4. Relevant Modules & Files (Physical Size Audit)
| File Path | Role / Purpose | Physical Line Count | Current Status |
|---|---|---|---|
| .clinerules | Modified in this session | 73 | Changed |
| .cursorrules | Modified in this session | 73 | Changed |
| README.md | Modified in this session | 66 | Changed |
| README.zh-CN.md | Modified in this session | 66 | Changed |
| agent_context_handoff/SKILL.md | Modified in this session | 102 | Changed |
| agent_context_handoff/SKILL.zh-CN.md | Modified in this session | 88 | Changed |
| agent_context_handoff/cli.py | Modified in this session | 576 | Changed |
| .gitignore | Modified in this session | 110 | Changed |
| agent-context-handoff-skill-plan.docx | Modified in this session | 341 | Changed |

## 5. Core Private & Helper Methods
| Method Name | Trigger/Invocation | Purpose / Data Transformation Role |
|---|---|---|
| N/A | N/A | N/A |

## 6. Platform Dependency Audit (Skip if N/A)
| API Reference / File | Reference Count | Location | Target Platform Replacement |
|---|:---:|---|---|
| Platform API: `chrome.storage` | 1 | N/A | [Describe alternative solution here] |
| Platform API: `chrome.runtime` | 1 | N/A | [Describe alternative solution here] |
| Platform API: `localStorage` | 1 | N/A | [Describe alternative solution here] |
| Platform API: `process.env` | 1 | N/A | [Describe alternative solution here] |
| Platform API: `window.` | 1 | N/A | [Describe alternative solution here] |
| Platform API: `document.` | 1 | N/A | [Describe alternative solution here] |
| Dependency: `setuptools` | 1 | N/A | External library |

## 7. Work Completed / Remaining (Status Prefix Rules Enforced)
*Use: `✅ Completed` (code exists), `🔄 In Progress` (partial code exists), `📋 Planned` (zero code, design discussion only), `⚠️ Blocked` (stuck).*

- **Completed Progress**:
- Init repo
- Create templates
- Implement CLI

- **Remaining Tasks**:
- Validate locally
- Publish to GitHub

## 8. Obsolete / Legacy Code (Orphaned Files)
- None

## 9. Current Errors / Blockers
None

## 10. Confirmed Decisions & Key Logic Summary
- Standardized folder layout '.ai-context/'

## 11. Focus for Next Session
No specific focus given.

## 12. Known Issues & Environmental Limits
- headroom: [OFFLINE] / [离线] 
- No active blockers

## 13. Validation Commands
```bash
python3 -m agent_context_handoff.cli --lang en
```

## 14. Specific Constraints for Incoming Agent
### 📚 Must-Read Files
1. `.ai-context/project.md` — Project layout and score definitions.
2. `.ai-context/decisions.md` — Design intents.

### 🚫 Files Absolutely Cannot Modify
- Describe files or paths that are highly sensitive and should not be modified (e.g., scoring config, core algorithms).

### ⚠️ Gotchas & Design Traps
- Describe specific logic traps (e.g., "Changing return structure of X breaks mapping Y").
