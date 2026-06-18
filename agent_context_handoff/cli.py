import argparse
from dataclasses import dataclass
import datetime
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable, Optional, Sequence


REDACTION_RULES = (
    (
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]+?"
            r"-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.IGNORECASE,
        ),
        "<REDACTED_PRIVATE_KEY>",
    ),
    (
        re.compile(r"([a-z][a-z0-9+.-]*://[^\s/:]+:)([^\s/@]+)(@)", re.IGNORECASE),
        r"\1<REDACTED_PASSWORD>\3",
    ),
    (
        re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s`'\"]+"),
        r"\1<REDACTED_SECRET>",
    ),
    (
        re.compile(r"(?i)(cookie\s*:\s*)[^\r\n]+"),
        r"\1<REDACTED_COOKIE>",
    ),
    (
        re.compile(
            r"(?i)\b(api[-_]?key|secret|token|password|pass|passwd|"
            r"private[-_]?key|credential|auth|session[-_]?id)"
            r"(\s*[:=]\s*)(?:['\"])?([^\s'\"`,;]+)(?:['\"])?"
        ),
        r"\1\2<REDACTED_SECRET>",
    ),
    (
        re.compile(r"\bey[a-zA-Z0-9_-]+\.ey[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b"),
        "<REDACTED_SECRET>",
    ),
    (
        re.compile(r"\b1[3-9]\d{9}\b"),
        "<REDACTED_PHONE>",
    ),
    (
        re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+\b"),
        "<REDACTED_EMAIL>",
    ),
    (
        re.compile(
            r"\b(?:10(?:\.\d{1,3}){3}|172\.(?:1[6-9]|2\d|3[01])"
            r"(?:\.\d{1,3}){2}|192\.168(?:\.\d{1,3}){2})\b"
        ),
        "<REDACTED_INTERNAL_HOST>",
    ),
)


@dataclass(frozen=True)
class CommandResult:
    args: Sequence[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True)
class GitSnapshot:
    repository_root: Optional[Path]
    status: str
    diff_stat: str
    changed_files: tuple[str, ...]
    recent_log: str
    errors: tuple[str, ...]


def redact_secrets(content: str) -> str:
    """Return content with common credential and personal-data shapes removed."""
    sanitized = content
    for pattern, replacement in REDACTION_RULES:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def run_command(args: Sequence[str], cwd: Optional[Path] = None) -> CommandResult:
    """Run a command without a shell and retain failures for the handoff report."""
    try:
        result = subprocess.run(
            list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return CommandResult(
            args=tuple(args),
            returncode=result.returncode,
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
        )
    except OSError as error:
        return CommandResult(
            args=tuple(args),
            returncode=127,
            stdout="",
            stderr=str(error),
        )


def _git(target: Path, *args: str) -> CommandResult:
    return run_command(("git", "-C", str(target), *args))


def _command_error(result: CommandResult) -> str:
    command = " ".join(result.args)
    detail = result.stderr or f"exit code {result.returncode}"
    return f"{command}: {detail}"


def collect_git_snapshot(target: Path) -> GitSnapshot:
    root_result = _git(target, "rev-parse", "--show-toplevel")
    if not root_result.ok:
        return GitSnapshot(
            repository_root=None,
            status="Not a git repository",
            diff_stat="N/A",
            changed_files=(),
            recent_log="N/A",
            errors=(_command_error(root_result),),
        )

    root = Path(root_result.stdout)
    commands = {
        "status": _git(root, "status", "--porcelain=v1"),
        "unstaged": _git(root, "diff", "--stat"),
        "staged": _git(root, "diff", "--cached", "--stat"),
        "untracked": _git(root, "ls-files", "--others", "--exclude-standard"),
        "log": _git(root, "log", "--oneline", "-5"),
    }
    errors = tuple(_command_error(result) for result in commands.values() if not result.ok)

    changed_files: set[str] = set()
    status_result = commands["status"]
    if status_result.ok:
        for line in status_result.stdout.splitlines():
            if len(line) < 4:
                continue
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed_files.add(path.strip('"'))
    if commands["untracked"].ok:
        changed_files.update(commands["untracked"].stdout.splitlines())

    stat_parts = []
    if commands["staged"].stdout:
        stat_parts.append("Staged:\n" + commands["staged"].stdout)
    if commands["unstaged"].stdout:
        stat_parts.append("Unstaged:\n" + commands["unstaged"].stdout)

    return GitSnapshot(
        repository_root=root,
        status=status_result.stdout or "No changes (clean)",
        diff_stat="\n\n".join(stat_parts) or "No tracked-file changes",
        changed_files=tuple(sorted(path for path in changed_files if path)),
        recent_log=commands["log"].stdout or "No commits yet",
        errors=errors,
    )


def load_template(template_name: str) -> str:
    template_path = Path(__file__).with_name("templates") / template_name
    try:
        return template_path.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(f"Required template is unavailable: {template_path}: {error}") from error


def write_document(path: Path, content: str, *, overwrite: bool) -> bool:
    """Write redacted content atomically enough for small local Markdown files."""
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact_secrets(content), encoding="utf-8")
    return True


def _template_name(base: str, is_zh: bool) -> str:
    return f"{base}-template.zh-CN.md" if is_zh else f"{base}-template.md"


def _document_name(base: str, is_zh: bool) -> str:
    return f"{base}.zh-CN.md" if is_zh else f"{base}.md"


def _format_changed_files(files: Iterable[str]) -> str:
    rendered = [f"- `{path}`" for path in files]
    return "\n".join(rendered) if rendered else "- None"


def _relevant_files_table(files: Iterable[str]) -> str:
    rows = [f"| `{path}` | Changed in working tree | Changed |" for path in files]
    return "\n".join(rows) if rows else "| N/A | N/A | N/A |"


def generate_context(target_dir: Path, *, lang: str, force: bool = False) -> None:
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    is_zh = lang == "zh"
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    snapshot = collect_git_snapshot(target_dir)
    if snapshot.repository_root is not None:
        target_dir = snapshot.repository_root
    context_dir = target_dir / ".ai-context"
    context_dir.mkdir(parents=True, exist_ok=True)

    readme = load_template(_template_name("README", is_zh))
    write_document(
        context_dir / _document_name("README", is_zh),
        readme,
        overwrite=True,
    )

    project = load_template(_template_name("project", is_zh)).format(
        project_background="待当前 Agent 补充" if is_zh else "To be completed by the current agent.",
        tech_stack_details="- 语言：\n- 框架：" if is_zh else "- Language:\n- Framework:",
        project_modules="- 待补充" if is_zh else "- To be documented",
        setup_commands="# 待补充" if is_zh else "# Add verified setup commands",
        build_commands="# 待补充" if is_zh else "# Add verified build commands",
    )
    write_document(
        context_dir / _document_name("project", is_zh), project, overwrite=force
    )

    current_task = load_template(_template_name("current-task", is_zh)).format(
        current_task_objective="待当前 Agent 补充" if is_zh else "To be completed by the current agent.",
        current_task_status="进行中" if is_zh else "In Progress",
        start_time=now,
        last_updated=now,
        task_checklist="- [ ] 补充真实任务清单" if is_zh else "- [ ] Add the verified task checklist",
        current_focus="待补充" if is_zh else "To be documented",
    )
    write_document(
        context_dir / _document_name("current-task", is_zh),
        current_task,
        overwrite=force,
    )

    error_text = "\n".join(f"- {error}" for error in snapshot.errors)
    changed = load_template(_template_name("changed-files", is_zh)).format(
        git_status=snapshot.status,
        git_diff_stat=snapshot.diff_stat,
        git_diff_names=_format_changed_files(snapshot.changed_files),
        git_log=snapshot.recent_log,
        changes_summary=(
            ("采集错误：\n" if is_zh else "Collection errors:\n") + error_text
            if error_text and snapshot.repository_root is not None
            else ("待当前 Agent 补充变更意图。" if is_zh else "The current agent must summarize change intent.")
        ),
    )
    write_document(
        context_dir / _document_name("changed-files", is_zh),
        changed,
        overwrite=True,
    )

    decisions = load_template(_template_name("decisions", is_zh)).format(
        decision_title="待补充" if is_zh else "Decision title",
        decision_context="待补充" if is_zh else "Document the verified context.",
        decision_details="待补充" if is_zh else "Document the confirmed decision.",
        decision_consequences="待补充" if is_zh else "Document known consequences.",
        decision_status="待确认" if is_zh else "Proposed",
    )
    write_document(
        context_dir / _document_name("decisions", is_zh), decisions, overwrite=force
    )

    issues = load_template(_template_name("known-issues", is_zh)).format(
        active_blockers="- 待确认" if is_zh else "- To be verified",
        historical_traps="- 待确认" if is_zh else "- To be verified",
        env_constraints="- 待确认" if is_zh else "- To be verified",
    )
    write_document(
        context_dir / _document_name("known-issues", is_zh), issues, overwrite=force
    )

    validation = load_template(_template_name("validation", is_zh)).format(
        test_commands="# 仅填写实际执行过或已确认的命令" if is_zh else "# Add only verified commands",
        manual_verification_steps="- 待补充" if is_zh else "- To be documented",
        last_validation_date=now,
        last_validation_status="未测试" if is_zh else "Untested",
        last_validation_output="N/A",
    )
    write_document(
        context_dir / _document_name("validation", is_zh), validation, overwrite=force
    )

    prompt = load_template(_template_name("next-agent-prompt", is_zh))
    write_document(
        context_dir / _document_name("next-agent-prompt", is_zh),
        prompt,
        overwrite=True,
    )

    handoff = load_template(_template_name("agent-handoff", is_zh)).format(
        current_task_brief="待当前 Agent 补充" if is_zh else "To be completed by the current agent.",
        project_context="见项目上下文文档。" if is_zh else "See the project context document.",
        tech_stack="待确认" if is_zh else "To be verified",
        relevant_files=_relevant_files_table(snapshot.changed_files),
        completed_work="- 待补充" if is_zh else "- To be documented",
        remaining_work="- 待补充" if is_zh else "- To be documented",
        current_errors="- 待确认" if is_zh else "- To be verified",
        confirmed_decisions="- 待补充" if is_zh else "- To be documented",
        pending_items="- 待确认" if is_zh else "- To be verified",
        rejected_alternatives="| 待补充 | 待补充 |" if is_zh else "| To be documented | To be documented |",
        risks="- 待确认" if is_zh else "- To be verified",
        next_step_suggestions="- 待补充" if is_zh else "- To be documented",
        validation_commands="# 仅填写已确认的命令" if is_zh else "# Add only verified commands",
    )
    write_document(
        context_dir / _document_name("agent-handoff", is_zh), handoff, overwrite=force
    )

    agents_path = target_dir / "AGENTS.md"
    section = load_template(_template_name("agents-section", is_zh))
    if agents_path.exists():
        existing = agents_path.read_text(encoding="utf-8")
    else:
        existing = (
            "# AI Agent 协作指南\n" if is_zh else "# AI Agents Guide\n"
        )
    if "## AI Context Handoff" not in existing:
        combined = existing.rstrip() + "\n\n" + section.lstrip()
        write_document(agents_path, combined, overwrite=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Universal cross-agent context handoff CLI"
    )
    parser.add_argument(
        "--lang", choices=("en", "zh"), default="en", help="Document language"
    )
    parser.add_argument("--dir", default=".", help="Target project directory")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace durable human-authored context documents",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    target = Path(args.dir)
    try:
        generate_context(target, lang=args.lang, force=args.force)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Context handoff updated in {target.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
