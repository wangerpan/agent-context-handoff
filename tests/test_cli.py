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

            handoff = target / ".agent_handoff" / "agent-handoff.md"
            task = target / ".agent_handoff" / "current-task.md"
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
            changed_path = repo / ".agent_handoff" / "changed-files.md"
            self.assertTrue(changed_path.exists())
            self.assertFalse((nested / ".agent_handoff").exists())
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
            prompt = (target / ".agent_handoff" / "next-agent-prompt.zh-CN.md").read_text(
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

    def test_xml_packaging_redacts_manually_injected_secrets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            # 1. Run first pass to generate folders
            run_cli(target)
            
            # 2. Write a manual file with raw secrets
            custom_doc = target / ".agent_handoff" / "custom-doc.md"
            custom_doc.write_text("API KEY IS: api-key=leak_this_secret\n", encoding="utf-8")
            
            # 3. Pack context
            result = run_cli(target, "--pack")
            self.assertEqual(result.returncode, 0, result.stderr)
            
            # 4. Verify XML does not contain the raw secret
            xml_file = target / ".agent_handoff" / "packaged-context.xml"
            self.assertTrue(xml_file.exists())
            xml_content = xml_file.read_text(encoding="utf-8")
            self.assertNotIn("leak_this_secret", xml_content)
            self.assertIn("<REDACTED_SECRET>", xml_content)

    def test_test_command_execution_failure_captures_exit_code_and_stderr(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            # Run test with custom Python statement returning exit code 42
            result = run_cli(target, "--test", f'{sys.executable} -c "import sys; print(\'error log\', file=sys.stderr); sys.exit(42)"')
            self.assertEqual(result.returncode, 0, result.stderr)
            
            val_file = target / ".agent_handoff" / "validation.md"
            self.assertTrue(val_file.exists())
            val_content = val_file.read_text(encoding="utf-8")
            self.assertIn("Failed (Exit Code: 42)", val_content)
            self.assertIn("error log", val_content)

    def test_incremental_scanning_creates_checksums_and_skips_when_no_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            # Setup a small python code file
            (target / "app.py").write_text("class CoreApp:\n    pass\n", encoding="utf-8")
            
            # First pass: Build
            res1 = run_cli(target, "--scan")
            self.assertEqual(res1.returncode, 0, res1.stderr)
            checksums_file = target / ".agent_handoff" / ".checksums"
            self.assertTrue(checksums_file.exists())
            
            # Second pass: Check skipped log output
            res2 = run_cli(target, "--scan")
            self.assertEqual(res2.returncode, 0, res2.stderr)
            self.assertIn("Skipping code-map scan", res2.stdout)


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
