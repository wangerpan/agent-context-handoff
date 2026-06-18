import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from agent_context_handoff.cli import redact_secrets


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(target: Path, *extra_args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "agent_context_handoff.cli",
            "--dir",
            str(target),
            *extra_args,
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class CliIntegrationTests(unittest.TestCase):
    def test_rerun_preserves_human_handoff_and_task_start_time(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            first = run_cli(target)
            self.assertEqual(first.returncode, 0, first.stderr)

            handoff = target / ".ai-context" / "agent-handoff.md"
            task = target / ".ai-context" / "current-task.md"
            handoff.write_text("# Human handoff\nKeep this context.\n", encoding="utf-8")
            original_task = task.read_text(encoding="utf-8")
            start_line = next(
                line for line in original_task.splitlines() if line.startswith("- **Start Time**:")
            )

            time.sleep(0.01)
            second = run_cli(target)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                handoff.read_text(encoding="utf-8"),
                "# Human handoff\nKeep this context.\n",
            )
            self.assertIn(start_line, task.read_text(encoding="utf-8"))

    def test_git_snapshot_includes_staged_unstaged_and_untracked_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
                check=True,
            )
            (repo / "staged.txt").write_text("base\n", encoding="utf-8")
            (repo / "unstaged.txt").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "initial"], check=True)

            (repo / "staged.txt").write_text("staged\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "staged.txt"], check=True)
            (repo / "unstaged.txt").write_text("unstaged\n", encoding="utf-8")
            (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            nested = repo / "nested"
            nested.mkdir()

            result = run_cli(nested)
            self.assertEqual(result.returncode, 0, result.stderr)
            changed_path = repo / ".ai-context" / "changed-files.md"
            self.assertTrue(changed_path.exists())
            self.assertFalse((nested / ".ai-context").exists())
            changed = changed_path.read_text(encoding="utf-8")
            self.assertIn("staged.txt", changed)
            self.assertIn("unstaged.txt", changed)
            self.assertIn("untracked.txt", changed)
            self.assertIn("initial", changed)
            self.assertNotIn("Not a git repository", changed)

    def test_chinese_prompt_references_generated_chinese_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = run_cli(target, "--lang", "zh")
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = (target / ".ai-context" / "next-agent-prompt.zh-CN.md").read_text(
                encoding="utf-8"
            )
            for name in (
                "README.zh-CN.md",
                "project.zh-CN.md",
                "current-task.zh-CN.md",
                "agent-handoff.zh-CN.md",
                "changed-files.zh-CN.md",
            ):
                self.assertIn(name, prompt)


class RedactionTests(unittest.TestCase):
    def test_redacts_supported_secret_shapes_without_changing_ordinary_text(self):
        source = "\n".join(
            [
                "Authorization: Bearer abcdefghijklmnop",
                "Cookie: sessionid=abc123456",
                "phone=13812345678",
                "DATABASE_URL=postgres://user:secret@10.0.0.2/prod",
                "token: abcdefgh",
                "Contact dev@example.com",
                "Ordinary project description remains readable.",
            ]
        )
        redacted = redact_secrets(source)
        for secret in (
            "abcdefghijklmnop",
            "abc123456",
            "13812345678",
            "secret@",
            "10.0.0.2",
            "abcdefgh",
            "dev@example.com",
        ):
            self.assertNotIn(secret, redacted)
        self.assertIn("Ordinary project description remains readable.", redacted)


if __name__ == "__main__":
    unittest.main()
