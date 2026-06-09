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

## 3. Project Context
{project_context}

## 4. Tech Stack
{tech_stack}

## 5. Relevant Modules & Files
| File Path | Role / Purpose | Current Status |
|---|---|---|
{relevant_files}

## 6. Work Completed in This Run
{completed_work}

## 7. Work Remaining
{remaining_work}

## 8. Current Errors / Blockers
{current_errors}

## 9. Confirmed Decisions & Key Logic Summary
{confirmed_decisions}

## 10. Focus for Next Session
{next_session_focus}

## 11. Known Issues & Environmental Limits
{known_issues_summary}

## 12. Validation Commands
```bash
{validation_commands}
```

## 13. Requirements for Incoming Agent
- Read `AGENTS.md` and all files under `.ai-context/` before editing code.
- Repeat/summarize your understanding of the task, completed progress, and next steps before starting.
- Maintain project coding standards and avoid unsolicited large refactorings.
- Update `.ai-context/current-task.md` after completion.
