import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_wheel_contains_templates_and_installed_cli_generates_documents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source"
            shutil.copytree(
                REPO_ROOT,
                source,
                ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__", "*.pyc"),
            )
            wheel_dir = temp / "wheel"
            wheel_dir.mkdir()
            build = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    str(source),
                    "--no-deps",
                    "--no-build-isolation",
                    "--wheel-dir",
                    str(wheel_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            wheel = next(wheel_dir.glob("*.whl"))
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
            self.assertIn(
                "agent_context_handoff/templates/agent-handoff-template.md", names
            )
            self.assertIn(
                "agent_context_handoff/templates/agent-handoff-template.zh-CN.md", names
            )

            installed = temp / "installed"
            install = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    str(wheel),
                    "--no-deps",
                    "--target",
                    str(installed),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            target = temp / "target"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(installed)
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_context_handoff.cli",
                    "--dir",
                    str(target),
                ],
                cwd=temp,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            generated = target / ".ai-context" / "agent-handoff.md"
            self.assertIn(
                "# Agent Project Handoff Documentation",
                generated.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
