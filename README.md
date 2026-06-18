# Agent Context Handoff

[English](README.md) | [简体中文](README.zh-CN.md)

An agent-neutral Skill and Python CLI for transferring unfinished engineering work between agents or sessions without losing verified context.

## What It Maintains

The CLI creates a short index in `AGENTS.md` and a handoff bundle under `.ai-context/`:

```text
.ai-context/
├── README.md
├── project.md
├── current-task.md
├── agent-handoff.md
├── changed-files.md
├── decisions.md
├── known-issues.md
├── validation.md
└── next-agent-prompt.md
```

Chinese output uses `.zh-CN.md` suffixes. The CLI refreshes machine-owned Git snapshots while preserving human-authored context by default.

## Install and Run

Python 3.9 or newer is required.

```bash
python3 -m pip install .
ai-context-handoff --dir /path/to/project --lang en
ai-context-handoff --dir /path/to/project --lang zh
```

Routine reruns preserve `project`, `current-task`, `agent-handoff`, `decisions`, `known-issues`, and `validation`. Use `--force` only when you intentionally want those durable documents regenerated:

```bash
ai-context-handoff --dir /path/to/project --lang en --force
```

The Git snapshot includes staged, unstaged, and untracked paths and works from repository subdirectories and Git worktrees.

## Install the Skill

Copy the canonical Skill directory into an agent Skill path:

```bash
cp -R skills/agent-context-handoff ~/.agents/skills/
```

The Skill instructs an agent to run the CLI for deterministic collection, inspect the real workspace and conversation, then refine the durable documents with verified facts.

## Security Boundary

Every CLI-generated payload passes through redaction for common credentials, URL passwords, bearer tokens, cookies, JWTs, private keys, email addresses, phone numbers, and private-network hosts.

Regex redaction reduces accidental exposure; it cannot prove that output is safe. Review the final handoff bundle before sharing it outside its trust boundary. Do not place raw Git diffs in handoff documents.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 -m pip wheel . --no-deps --no-build-isolation
```

## License

[MIT](LICENSE)
