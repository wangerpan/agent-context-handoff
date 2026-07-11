---
name: agent-context-handoff
description: Use when transferring an unfinished engineering task to another agent or session without losing verified project context, decisions, changes, blockers, or validation evidence.
---

# Agent Context Handoff

Create an agent-neutral, evidence-based handoff under `.agent_handoff/`. Preserve human-authored context and distinguish verified facts from unknowns.

## Workflow

1. Locate the project root with `git rev-parse --show-toplevel` when Git is available.
2. Run `agent-context-handoff --dir <project> --lang <en|zh> --mode <analysis|fix|review|handoff>` to initialize files and refresh the Git snapshot. Use `--refresh` to update generated task metadata while preserving human sections. Use `--force` only when the user explicitly requests replacement of durable context.
3. Inspect the active conversation, workspace, relevant source files, Git state, and test output.
4. Refine the durable documents with verified facts. Never invent completed work, decisions, commands, errors, or validation results.
5. Redact secrets and personal or internal infrastructure data before writing.
6. Confirm that paths, blockers, next steps, and validation commands are actionable.
7. Run `agent-context-handoff lint --dir <project>` before packaging or sharing. Treat stale branch, commit, or timestamp findings as a requirement to re-check the workspace and regenerate the snapshot.

## Required Content

- `current-task.md`: objective, state, checklist, and focus.
- `agent-handoff.md`: completed and remaining work, relevant files, blockers, decisions, rejected alternatives, risks, next steps, and validation.
- `changed-files.md`: staged, unstaged, and untracked Git snapshot maintained by the CLI.
- `validation.md`: commands actually run, status, and concise evidence.
- `next-agent-prompt.md`: read-first instructions for the incoming agent.

Chinese runs use language-suffixed filenames such as `agent-handoff.zh-CN.md`.

## Safety Rules

- Do not include raw diffs, credentials, cookies, private keys, production connection strings, personal contact data, or sensitive internal hosts.
- Do not overwrite existing human-authored context during routine refreshes.
- Regex redaction is defense in depth, not proof of safety. Review the final bundle.
- Keep `AGENTS.md` short; detailed state belongs in `.agent_handoff/`.

## Completion Check

- Every claim is supported by workspace or conversation evidence.
- Unknowns are labeled instead of guessed.
- Facts, historical context, assumptions, and unverified TODOs are clearly distinguished.
- Validation distinguishes commands run from commands merely suggested.
- The incoming agent can identify the exact next action without rereading the full conversation.
