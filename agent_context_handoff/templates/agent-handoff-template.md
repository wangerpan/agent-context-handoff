# Agent Project Handoff Documentation

[English](agent-handoff.md) | [简体中文](agent-handoff.zh-CN.md)

## 📌 Handoff Metadata
- **Generated At**: {timestamp}
- **Git Commit SHA**: {git_commit_sha}
- **Session / Trace ID**: {session_id}

---

## 1. Current Task
{current_task_brief}

## 2. Current State (Runtime Status)
- **Active Agent Classifications**:
  - Built-in Agents: {built_in_agents_count} (Describe classification instead of hardcoded numbers in assertions)
  - Understand-Anything Agents: {understand_anything_count}
- **MCP Servers Status**:
  - Online MCPs: {online_mcps}
  - Offline MCPs (e.g. headroom): {offline_mcps} (Do not try to call offline servers)
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

## 5. Core Private & Helper Methods
| Method Name | Trigger/Invocation | Purpose / Data Transformation Role |
|---|---|---|
{private_methods}

## 6. Work Completed in This Run
{completed_work}

## 7. Work Remaining
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

## 14. Requirements for Incoming Agent
- Read `AGENTS.md` and all files under `.ai-context/` before editing code.
- Repeat/summarize your understanding of the task, completed progress, and next steps before starting.
- Maintain project coding standards and avoid unsolicited large refactorings.
- Update `.ai-context/current-task.md` after completion.
