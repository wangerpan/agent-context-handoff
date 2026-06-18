---
name: agent-context-handoff
description: Use when transferring an unfinished engineering task to another agent or session without losing verified project context, decisions, changes, blockers, or validation evidence.
---

# Agent Context Handoff

This is a compatibility copy. The canonical installable Skill is at
`skills/agent-context-handoff/SKILL.md`.

## Workflow

1. Locate the project root with `git rev-parse --show-toplevel` when Git is available.
2. Run `ai-context-handoff --dir <project> --lang <en|zh>` to initialize the bundle and refresh the Git snapshot. Do not use `--force` unless the user explicitly wants human-authored documents replaced.
3. Inspect the actual workspace, active conversation, Git state, relevant source files, and test output.
4. Refine the durable files with verified facts. Never invent completed work, decisions, commands, errors, or validation results.
5. Redact secrets and personal or internal infrastructure data before writing.
6. Confirm that file paths and validation commands are actionable for the incoming agent.

## Required Content

Keep these files current:

- `current-task.md`: objective, state, checklist, and current focus.
- `agent-handoff.md`: completed and remaining work, relevant files, blockers, decisions, rejected alternatives, risks, next steps, and validation commands.
- `changed-files.md`: machine-generated staged, unstaged, and untracked Git snapshot.
- `validation.md`: commands actually run, status, and concise evidence.
- `next-agent-prompt.md`: read-first instructions for the incoming agent.

Use language-suffixed filenames when running with `--lang zh`.

## Safety Rules

- Do not include raw diffs, credentials, cookies, private keys, production connection strings, personal contact data, or sensitive internal hosts.
- Do not overwrite existing human-authored context during routine refreshes.
- Treat regex redaction as defense in depth, not proof that output is safe. Review the final bundle.
- Keep `AGENTS.md` as a short index; detailed state belongs in `.ai-context/`.
