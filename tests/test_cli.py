import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import json

from agent_context_handoff.cli import redact_secrets, run_command


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
    def test_chinese_agents_section_links_only_generated_localized_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = run_cli(target, "--lang", "zh")
            self.assertEqual(result.returncode, 0, result.stderr)
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(".agent_handoff/README.zh-CN.md", agents)
            self.assertIn(".agent_handoff/current-task.zh-CN.md", agents)
            self.assertNotIn(".agent_handoff/README.md", agents)

    def test_rerun_replaces_legacy_agents_section_for_selected_language(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            (target / "AGENTS.md").write_text(
                "# Guide\n\n## AI Context Handoff\n\nRead [.agent_handoff/README.md](file:///tmp/project/.agent_handoff/README.md).\n\n## Local Rules\n\nKeep me.\n",
                encoding="utf-8",
            )
            result = run_cli(target, "--lang", "zh")
            self.assertEqual(result.returncode, 0, result.stderr)
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(".agent_handoff/README.zh-CN.md", agents)
            self.assertNotIn("file://", agents)
            self.assertIn("## Local Rules\n\nKeep me.", agents)

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

    def test_pack_redacts_secrets_from_existing_human_documents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            first = run_cli(target)
            self.assertEqual(first.returncode, 0, first.stderr)
            handoff = target / ".agent_handoff" / "agent-handoff.md"
            handoff.write_text(
                "# Human context\nAuthorization: Bearer secret-token-value\n",
                encoding="utf-8",
            )

            packed = run_cli(target, "--pack")
            self.assertEqual(packed.returncode, 0, packed.stderr)
            xml = (target / ".agent_handoff" / "packaged-context.xml").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("secret-token-value", xml)
            self.assertIn("<REDACTED_SECRET>", xml)

    def test_initial_handoff_does_not_claim_unverified_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = run_cli(target)
            self.assertEqual(result.returncode, 0, result.stderr)
            handoff = (target / ".agent_handoff" / "agent-handoff.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("Init repo", handoff)
            self.assertNotIn("Publish to GitHub", handoff)
            self.assertNotIn("No active blockers", handoff)
            self.assertIn("To be verified", handoff)

    def test_force_replaces_durable_handoff_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            first = run_cli(target)
            self.assertEqual(first.returncode, 0, first.stderr)
            handoff = target / ".agent_handoff" / "agent-handoff.md"
            handoff.write_text("# Custom durable context\n", encoding="utf-8")

            forced = run_cli(target, "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertNotIn("Custom durable context", handoff.read_text(encoding="utf-8"))

    def test_single_language_output_has_no_missing_cross_language_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = run_cli(target, "--lang", "zh")
            self.assertEqual(result.returncode, 0, result.stderr)
            readme = (target / ".agent_handoff" / "README.zh-CN.md").read_text(
                encoding="utf-8"
            )
            handoff = (target / ".agent_handoff" / "agent-handoff.zh-CN.md").read_text(
                encoding="utf-8"
            )
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("(README.md)", readme)
            self.assertNotIn("(agent-handoff.md)", handoff)
            self.assertNotIn("file://", agents)
            self.assertNotIn(".agent_handoff/README.md", agents)

    def test_generated_documents_use_portable_relative_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            (target / "app.py").write_text("class Example:\n    pass\n", encoding="utf-8")
            result = run_cli(target, "--scan")
            self.assertEqual(result.returncode, 0, result.stderr)
            generated = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (target / ".agent_handoff").glob("*.md")
            )
            self.assertNotIn("file://", generated)

    def test_code_map_excludes_build_logs_and_tooling_noise(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            for directory in (
                "src",
                "target/classes",
                "logs/archive",
                ".codegraph/cache",
                ".sisyphus/state",
                ".codefree/output",
            ):
                path = target / directory
                path.mkdir(parents=True)
                (path / "sample.py").write_text("class Sample:\n    pass\n", encoding="utf-8")
            (target / ".DS_Store").write_text("noise", encoding="utf-8")

            result = run_cli(target, "--scan")
            self.assertEqual(result.returncode, 0, result.stderr)
            code_map = (target / ".agent_handoff" / "code-map.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("/src", code_map)
            for noise in ("target", "logs", ".codegraph", ".sisyphus", ".codefree", ".DS_Store"):
                self.assertNotIn(noise, code_map)

    def test_lint_reports_stale_git_snapshot_as_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            (repo / "app.py").write_text("print('one')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "app.py"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "first"], check=True)
            generated = run_cli(repo)
            self.assertEqual(generated.returncode, 0, generated.stderr)

            (repo / "app.py").write_text("print('two')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "app.py"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "second"], check=True)
            linted = run_cli(repo, "lint", "--json")
            self.assertEqual(linted.returncode, 1, linted.stderr)
            report = json.loads(linted.stdout)
            self.assertTrue(any(item["code"] == "stale-commit" for item in report["findings"]))

    def test_lint_reports_obsolete_paths_and_unverified_example_claims(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            generated = run_cli(target)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            handoff = target / ".agent_handoff" / "agent-handoff.md"
            handoff.write_text(
                "Read .ai-context/README.md\nPublish to GitHub\nNo active blockers\n",
                encoding="utf-8",
            )
            linted = run_cli(target, "lint", "--json")
            self.assertEqual(linted.returncode, 1, linted.stderr)
            codes = {item["code"] for item in json.loads(linted.stdout)["findings"]}
            self.assertIn("obsolete-path", codes)
            self.assertIn("unverified-claim", codes)

    def test_lint_reports_snapshot_older_than_seven_days(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            generated = run_cli(target)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            state_path = target / ".agent_handoff" / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["generated_at"] = "2000-01-01T00:00:00+00:00"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            linted = run_cli(target, "lint", "--json")
            self.assertEqual(linted.returncode, 1, linted.stderr)
            codes = {item["code"] for item in json.loads(linted.stdout)["findings"]}
            self.assertIn("stale-timestamp", codes)

    def test_doctor_json_reports_cli_and_handoff_health(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            generated = run_cli(target)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            checked = run_cli(target, "doctor", "--json")
            self.assertEqual(checked.returncode, 0, checked.stderr)
            report = json.loads(checked.stdout)
            self.assertIn("version", report)
            self.assertTrue(report["handoff_exists"])
            self.assertEqual(report["findings"], [])

    def test_refresh_updates_generated_task_metadata_without_losing_human_sections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            generated = run_cli(target)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            task = target / ".agent_handoff" / "current-task.md"
            content = task.read_text(encoding="utf-8")
            content = content.replace("待确认 / To be confirmed", "Preserve this objective")
            content = content.replace(
                next(line for line in content.splitlines() if line.startswith("- **Last Updated**:")),
                "- **Last Updated**: 2000-01-01 00:00:00",
            )
            task.write_text(content, encoding="utf-8")

            refreshed = run_cli(target, "--refresh")
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
            updated = task.read_text(encoding="utf-8")
            self.assertIn("Preserve this objective", updated)
            self.assertNotIn("2000-01-01 00:00:00", updated)

    def test_prompt_is_mode_aware_and_handoff_declares_trust_levels(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            generated = run_cli(target, "--mode", "review")
            self.assertEqual(generated.returncode, 0, generated.stderr)
            prompt = (target / ".agent_handoff" / "next-agent-prompt.md").read_text(
                encoding="utf-8"
            )
            handoff = (target / ".agent_handoff" / "agent-handoff.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Review mode", prompt)
            for label in ("Verified facts", "Historical context", "Assumptions", "Unverified TODOs"):
                self.assertIn(label, handoff)


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


class CommandTests(unittest.TestCase):
    def test_failed_command_exposes_exit_code_and_stderr(self):
        result = run_command(
            [
                sys.executable,
                "-c",
                "import sys; print('git exploded', file=sys.stderr); raise SystemExit(7)",
            ]
        )
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.stderr, "git exploded")
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
