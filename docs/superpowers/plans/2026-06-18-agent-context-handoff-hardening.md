# Agent Context Handoff Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Skill discoverable and the installed CLI non-destructive, complete, secure, and verifiable.

**Architecture:** Centralize command execution, redaction, Git collection, and file writing in focused functions. Preserve the existing output contract while explicitly separating machine-refreshed snapshots from durable human-authored context.

**Tech Stack:** Python 3.9+, standard-library `unittest`, setuptools via `pyproject.toml`, Markdown.

---

### Task 1: Establish failing behavior tests

**Files:**
- Create: `tests/test_cli.py`

- [ ] Test that reruns preserve `agent-handoff.md` and the original task start time.
- [ ] Test staged, unstaged, and untracked Git collection from a repository subdirectory.
- [ ] Test bearer tokens, cookies, phones, URL credentials, private hosts, and ordinary prose redaction.
- [ ] Test Chinese prompts reference files that the Chinese run creates.
- [ ] Run `python3 -m unittest discover -s tests -v` and confirm failures against the current implementation.

### Task 2: Refactor and harden the CLI

**Files:**
- Modify: `agent_context_handoff/cli.py`

- [ ] Replace shell commands with argument arrays and surfaced command results.
- [ ] Add complete Git snapshot collection.
- [ ] Add centralized redacted writes and `--force` overwrite semantics.
- [ ] Preserve durable files and task timestamps on ordinary reruns.
- [ ] Run the tests and confirm they pass.

### Task 3: Fix packaging and Skill discovery

**Files:**
- Create: `pyproject.toml`
- Delete: `setup.py`
- Create: `skills/agent-context-handoff/SKILL.md`
- Modify: `agent_context_handoff/SKILL.md`
- Modify: `agent_context_handoff/SKILL.zh-CN.md`

- [ ] Explicitly package `templates/*.md` and require Python 3.9+.
- [ ] Add valid Skill frontmatter and concise trigger-oriented instructions.
- [ ] Keep legacy Skill paths as compatibility documentation.

### Task 4: Align templates and documentation

**Files:**
- Modify: `agent_context_handoff/templates/*.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

- [ ] Remove non-portable `file://` links.
- [ ] Ensure language-specific links point to generated files.
- [ ] Document preservation, `--force`, Git coverage, and redaction limits accurately.

### Task 5: Installed-artifact verification

**Files:**
- Modify: `tests/test_packaging.py`

- [ ] Build a wheel in a temporary directory.
- [ ] Verify template files exist inside the wheel.
- [ ] Install the wheel into a temporary target and run the installed CLI.
- [ ] Run the full test suite and inspect `git diff --check` and `git status --short`.
