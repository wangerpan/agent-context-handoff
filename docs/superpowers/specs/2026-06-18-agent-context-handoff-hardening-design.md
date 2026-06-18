# Agent Context Handoff Hardening Design

## Goal

Make the Skill discoverable and the installed CLI safe, accurate, and testable without breaking the existing nine-file handoff format.

## Design

- Keep the existing `.ai-context/` document layout for backward compatibility.
- Treat human-authored documents as durable state: create them only when missing. Refresh only machine-owned Git snapshot files by default; require `--force` to replace durable files.
- Collect repository state with argument-based Git subprocess calls, including staged, unstaged, and untracked files. Resolve repositories through `git rev-parse` so subdirectories and worktrees work.
- Redact every generated payload immediately before writing it. Cover assignments, URL credentials, JWTs, private keys, bearer tokens, cookies, email addresses, phone numbers, and private hosts.
- Package templates explicitly through modern `pyproject.toml` metadata.
- Keep Python package code under `agent_context_handoff/` and publish a standards-compliant Skill under `skills/agent-context-handoff/`.

## Error Handling

Command failures remain visible in generated snapshots and CLI stderr. Missing templates are fatal instead of silently producing empty documents. Writes use a single helper so redaction and overwrite policy cannot be bypassed accidentally.

## Verification

Use `unittest` integration tests for preservation, Git collection, redaction, localization, and installed-wheel behavior. Build and install the wheel into a temporary target before running the CLI.
