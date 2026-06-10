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
- **Generated At**: {timestamp}
- **Git Commit SHA**: {git_commit_sha}
- **Session / Trace ID**: {session_id}

---

## 1. Current Task
{current_task_brief}

## 2. Current State (Runtime Status - Skip if N/A)
- **Active Agent Classifications**:
  - Built-in Agents: {built_in_agents_count} (Use descriptive assertions)
  - Understand-Anything Agents: {understand_anything_count}
- **MCP Servers Status**:
  - Online MCPs: {online_mcps}
  - Offline MCPs (e.g. headroom): {offline_mcps}
- **Managed Background Screens**:
  - Active screen count: {active_screens}
  - *Prerequisite*: Before attaching via `screen -r`, make sure they are started by invoking `/config` or `/cli` POST endpoint first.

## 3. Project Context & Tech Stack
{project_context}
- **Tech Stack**: {tech_stack}

## 4. Relevant Modules & Files (Physical Size Audit)
| File Path | Role / Purpose | Physical Line Count | Current Status |
|---|---|---|---|
{relevant_files}

## 5. Critical Code Path & Business Flow (Task-Specific Flowchart & Jump Table)
```mermaid
graph TD
{mermaid_business_flow}
```

| Step | Node Type | Code Anchor (Click-to-Jump) | Data Transformation & Role |
|---|---|---|---|
{business_flow_steps}

## 6. Platform Dependency Audit (Skip if N/A)
| API Reference / File | Reference Count | Location | Target Platform Replacement |
|---|:---:|---|---|
{platform_dependencies}

## 7. Work Completed / Remaining (Status Prefix Rules Enforced)
*Use: `✅ Completed` (code exists), `🔄 In Progress` (partial code exists), `📋 Planned` (zero code, design discussion only), `⚠️ Blocked` (stuck).*

- **Completed Progress**:
{completed_work}

- **Remaining Tasks**:
{remaining_work}

## 8. Obsolete / Legacy Code (Orphaned Files)
{obsolete_code}

## 9. Current Errors / Blockers
{current_errors}

## 10. Confirmed Decisions & Key Logic Summary
{confirmed_decisions}

## 11. Focus for Next Session
{next_session_focus}

## 12. Known Issues & Environmental Limits
{known_issues_summary}

## 13. Validation Commands
```bash
{validation_commands}
```

## 14. Specific Constraints for Incoming Agent
### 📚 Must-Read Files
1. `.agent_handoff/project.md` — Project layout and specifications.
2. `.agent_handoff/decisions.md` — Design intents and decisions log.
3. `.agent_handoff/code-map.md` — Code map and architecture flowcharts.

### 🚫 Files Absolutely Cannot Modify
- Describe files or paths that are highly sensitive and should not be modified (e.g., scoring config, core algorithms).

### ⚠️ Gotchas & Design Traps
- Describe specific logic traps (e.g., "Changing return structure of X breaks mapping Y").
