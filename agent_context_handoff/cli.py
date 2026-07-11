import os
import sys
import re
import argparse
import subprocess
import datetime
import json
from dataclasses import dataclass
import shlex

from agent_context_handoff import __version__


EXCLUDED_SCAN_DIRS = {
    ".agent_handoff", ".ai-context", ".git", ".venv", "venv", "__pycache__",
    "node_modules", "target", "build", "dist", "logs", ".codegraph",
    ".sisyphus", ".codefree", ".codefree-output", "coverage", ".pytest_cache",
}
LINT_CLAIMS = ("Publish to GitHub", "No active blockers")

# Secret stripping regular expressions
SECRET_PATTERNS = [
    (r'-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z0-9 ]*PRIVATE KEY-----', '<REDACTED_PRIVATE_KEY>'),
    (r'([a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:]+:)([^\s/@]+)(@)', r'\1<REDACTED_PASSWORD>\3'),
    (r'(?i)(authorization\s*:\s*bearer\s+)[^\s`\'\"]+', r'\1<REDACTED_SECRET>'),
    (r'(?i)(cookie\s*:\s*)[^\r\n]+', r'\1<REDACTED_COOKIE>'),
    (r'(?i)\b(api[-_]?key|secret|token|password|pass|passwd|private[-_]?key|credential|auth|session[-_]?id)(\s*[:=]\s*)(?:[\'\"])?([^\s\'\"`,;]+)(?:[\'\"])?', r'\1\2<REDACTED_SECRET>'),
    (r'\bey[a-zA-Z0-9_-]+\.ey[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b', '<REDACTED_SECRET>'),
    (r'\b1[3-9]\d{9}\b', '<REDACTED_PHONE>'),
    (r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+\b', '<REDACTED_EMAIL>'),
    (r'\b(?:10(?:\.\d{1,3}){3}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|192\.168(?:\.\d{1,3}){2})\b', '<REDACTED_INTERNAL_HOST>')
]

def redact_secrets(content):
    """Sanitize secrets from content using regex."""
    sanitized = content
    for pattern, replacement in SECRET_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized

@dataclass(frozen=True)
class CommandResult:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self):
        return self.returncode == 0


def run_command(cmd, cwd=None):
    """Run a command without a shell and retain stdout, stderr, and status."""
    args = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    try:
        res = subprocess.run(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        return CommandResult(tuple(args), res.returncode, res.stdout.strip(), res.stderr.strip())
    except OSError as error:
        return CommandResult(tuple(args), 127, "", str(error))


def command_output(cmd, cwd=None, report_error=True):
    """Return successful stdout and surface failures instead of treating them as empty state."""
    result = run_command(cmd, cwd=cwd)
    if result.ok:
        return result.stdout
    if report_error:
        command = " ".join(result.args)
        detail = result.stderr or f"exit code {result.returncode}"
        print(f"Warning: command failed ({result.returncode}): {command}: {detail}", file=sys.stderr)
    return ""

def load_template(template_name):
    """Load template content from the package templates directory."""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_path = os.path.join(templates_dir, template_name)
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    raise RuntimeError(f"Required template is unavailable: {template_path}")


def write_document(path, content, overwrite=True):
    """Write a redacted document while respecting durable human-authored files."""
    if os.path.exists(path) and not overwrite:
        return False
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write(redact_secrets(content))
    return True


def resolve_target_dir(path):
    """Return the Git root when available, otherwise the absolute input path."""
    target_dir = os.path.abspath(path)
    git_root = command_output(
        ["git", "-C", target_dir, "rev-parse", "--show-toplevel"],
        report_error=False,
    )
    return git_root or target_dir


def lint_handoff(target_dir):
    """Return actionable findings for stale or unsafe handoff artifacts."""
    target_dir = resolve_target_dir(target_dir)
    context_dir = os.path.join(target_dir, ".agent_handoff")
    findings = []
    if not os.path.isdir(context_dir):
        return [{"code": "missing-handoff", "path": ".agent_handoff", "message": "Handoff directory does not exist."}]

    state_path = os.path.join(context_dir, "state.json")
    state = {}
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as file_obj:
                state = json.load(file_obj)
        except (OSError, ValueError) as error:
            findings.append({"code": "invalid-state", "path": ".agent_handoff/state.json", "message": str(error)})
    else:
        findings.append({"code": "missing-state", "path": ".agent_handoff/state.json", "message": "Regenerate the handoff to add freshness metadata."})

    generated_at = state.get("generated_at")
    if generated_at:
        try:
            generated_time = datetime.datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
            if generated_time.tzinfo is None:
                generated_time = generated_time.replace(tzinfo=datetime.timezone.utc)
            age = datetime.datetime.now(datetime.timezone.utc) - generated_time
            if age > datetime.timedelta(days=7):
                findings.append({"code": "stale-timestamp", "path": ".agent_handoff/state.json", "message": "Handoff snapshot is older than seven days."})
        except (TypeError, ValueError):
            findings.append({"code": "invalid-timestamp", "path": ".agent_handoff/state.json", "message": "generated_at is not a valid ISO-8601 timestamp."})

    current_commit = command_output(["git", "-C", target_dir, "rev-parse", "HEAD"], report_error=False)
    current_branch = command_output(["git", "-C", target_dir, "branch", "--show-current"], report_error=False)
    if current_commit and state.get("git_commit") not in (None, "N/A", current_commit):
        findings.append({"code": "stale-commit", "path": ".agent_handoff/state.json", "message": "Handoff commit differs from HEAD."})
    if current_branch and state.get("git_branch") not in (None, "N/A", current_branch):
        findings.append({"code": "stale-branch", "path": ".agent_handoff/state.json", "message": "Handoff branch differs from the current branch."})

    for root, dirs, files in os.walk(context_dir):
        dirs[:] = [name for name in dirs if name not in EXCLUDED_SCAN_DIRS]
        for name in files:
            if not (name.endswith(".md") or name.endswith(".xml")):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file_obj:
                    content = file_obj.read()
            except OSError:
                continue
            rel_path = os.path.relpath(path, target_dir)
            if ".ai-context" in content:
                findings.append({"code": "obsolete-path", "path": rel_path, "message": "Replace .ai-context with .agent_handoff."})
            if "file://" in content:
                findings.append({"code": "nonportable-link", "path": rel_path, "message": "Replace file:// links with relative Markdown links."})
            if any(claim in content for claim in LINT_CLAIMS):
                findings.append({"code": "unverified-claim", "path": rel_path, "message": "Remove example completion or blocker claims unless verified."})
    return findings


def print_health_report(action, target_dir, as_json):
    """Print lint or doctor output and return a process exit code."""
    target_dir = resolve_target_dir(target_dir)
    findings = lint_handoff(target_dir)
    if action == "doctor":
        report = {
            "version": __version__,
            "target_dir": target_dir,
            "git_available": bool(command_output(["git", "--version"], report_error=False)),
            "handoff_exists": os.path.isdir(os.path.join(target_dir, ".agent_handoff")),
            "findings": findings,
        }
    else:
        report = {"target_dir": target_dir, "findings": findings}
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{action}: {len(findings)} finding(s)")
        for finding in findings:
            print(f"- [{finding['code']}] {finding['path']}: {finding['message']}")
    return 1 if findings else 0


def update_agents_handoff_section(existing_content, rendered_section):
    """Replace the managed or legacy handoff section while preserving local rules."""
    managed = re.compile(
        r"(?ms)^<!-- agent-context-handoff:start -->.*?^<!-- agent-context-handoff:end -->\s*"
    )
    legacy = re.compile(r"(?ms)^## AI Context Handoff[^\n]*\n.*?(?=^## |\Z)")
    replacement = rendered_section.strip() + "\n\n"
    if managed.search(existing_content):
        return managed.sub(replacement, existing_content, count=1).rstrip() + "\n"
    if legacy.search(existing_content):
        return legacy.sub(replacement, existing_content, count=1).rstrip() + "\n"
    return existing_content.rstrip() + "\n\n" + replacement

def get_line_count(file_path):
    """Get the physical line count of a file."""
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
    except Exception:
        pass
    return "N/A"

def scan_platform_apis(target_dir):
    """Scan the codebase for platform specific API references and static external dependencies."""
    apis = {
        "chrome.storage": "Chrome Extension Storage API",
        "chrome.runtime": "Chrome Extension Runtime API",
        "localStorage": "Web Browser Storage API",
        "process.env": "Node.js Process Environment API",
        "window.": "Browser DOM Window Reference",
        "document.": "Browser DOM Document Reference"
    }
    results = {k: 0 for k in apis}
    exclude_dirs = EXCLUDED_SCAN_DIRS
    valid_extensions = {".js", ".ts", ".html", ".py", ".java", ".json", ".vue", ".jsx", ".tsx"}
    
    dependencies = {}
    js_stdlib = {"path", "fs", "crypto", "http", "os", "child_process", "util", "events", "stream", "url", "querystring", "zlib", "assert", "readline", "process"}
    py_stdlib = {"os", "sys", "re", "argparse", "subprocess", "datetime", "time", "json", "math", "collections", "shutil", "tempfile", "hashlib", "urllib", "traceback", "logging", "typing", "functools", "abc", "uuid", "io", "pathlib", "random", "ast", "inspect", "unittest"}
    
    js_import_pat = re.compile(r'\bimport\s+(?:(?:[\w\s{},*]+)\s+from\s+)?[\'"]([a-zA-Z0-9@\-_/]+)[\'"]')
    js_require_pat = re.compile(r'\brequire\(\s*[\'"]([a-zA-Z0-9@\-_/]+)[\'"]\s*\)')
    py_import_pat = re.compile(r'^\s*import\s+([a-zA-Z0-9_]+)', re.MULTILINE)
    py_from_pat = re.compile(r'^\s*from\s+([a-zA-Z0-9_]+)\s+import', re.MULTILINE)
    
    try:
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_extensions:
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                            content = file_obj.read()
                            # Count platform APIs
                            for api in apis:
                                results[api] += content.count(api)
                            
                            # Count external dependencies
                            if ext in {".js", ".ts", ".jsx", ".tsx", ".vue"}:
                                imports = js_import_pat.findall(content) + js_require_pat.findall(content)
                                for imp in imports:
                                    pkg = imp.split('/')[0] if not imp.startswith('@') else '/'.join(imp.split('/')[:2])
                                    if pkg and pkg not in js_stdlib:
                                        if not os.path.exists(os.path.join(root, pkg)) and not os.path.exists(os.path.join(target_dir, pkg)):
                                            dependencies[pkg] = dependencies.get(pkg, 0) + 1
                            elif ext == ".py":
                                imports = py_import_pat.findall(content) + py_from_pat.findall(content)
                                for imp in imports:
                                    if imp and imp not in py_stdlib:
                                        if not os.path.exists(os.path.join(root, imp)) and not os.path.exists(os.path.join(root, imp + ".py")) and not os.path.exists(os.path.join(target_dir, imp)) and not os.path.exists(os.path.join(target_dir, imp + ".py")):
                                            dependencies[imp] = dependencies.get(imp, 0) + 1
                    except Exception:
                        pass
    except Exception:
        pass
        
    active_apis = {k: v for k, v in results.items() if v > 0}
    active_deps = {k: v for k, v in dependencies.items() if v > 0}
    return active_apis, apis, active_deps


def package_context(ai_context_dir, target_dir, lang):
    """Bundle generated language-specific .agent_handoff files into an XML file."""
    suffix = ".zh-CN.md" if lang == "zh" else ".md"
    xml_parts = [f'<agent_handoff language="{lang}">']
    
    files_to_pack = []
    try:
        for entry in sorted(os.listdir(ai_context_dir)):
            if entry.endswith(suffix):
                if "packaged-context" in entry:
                    continue
                files_to_pack.append(entry)
                
        for entry in files_to_pack:
            file_path = os.path.join(ai_context_dir, entry)
            rel_path = os.path.relpath(file_path, target_dir)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                escaped = content.replace("]]>", "]]]]><![CDATA[>")
                xml_parts.append(f'  <file path="{rel_path}">\n    <![CDATA[\n{escaped}\n    ]]>\n  </file>')
            except Exception as e:
                print(f"Warning: Failed to package {entry}: {e}")
    except Exception as e:
        print(f"Warning: Failed to scan directory for packaging: {e}")
        
    xml_parts.append('</agent_handoff>')
    xml_content = "\n".join(xml_parts)
    
    pack_filename = f"packaged-context{suffix.replace('.md', '.xml')}"
    pack_path = os.path.join(ai_context_dir, pack_filename)
    try:
        write_document(pack_path, xml_content)
        print(f"Bundled active context files into: {pack_path}")
    except Exception as e:
        print(f"Error writing packaged context file: {e}")


def extract_markdown_section(content, section_headers):
    """Extract content under specific section headers (e.g. ## Objective or ## 任务目标)."""
    if not content:
        return ""
    
    lines = content.splitlines()
    section_content = []
    in_section = False
    
    # Clean section headers to look for
    headers = [h.strip().lower() for h in section_headers]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("##"):
            # Header found. Check if it matches our target section.
            header_text = stripped[2:].strip().lower()
            if header_text in headers:
                in_section = True
                continue
            elif in_section:
                # We hit another section header, stop capturing.
                break
        
        if in_section:
            section_content.append(line)
            
    return "\n".join(section_content).strip()

def main():
    parser = argparse.ArgumentParser(description="Universal Cross-Agent Context Handoff CLI")
    parser.add_argument("action", nargs="?", choices=["generate", "lint", "doctor"], default="generate")
    parser.add_argument("--lang", choices=["en", "zh"], default="en", help="Language for handoff docs (en or zh)")
    parser.add_argument("--dir", default=".", help="Target directory (default: current directory)")
    parser.add_argument("--focus", default="", help="Focus or objective for the next session/agent")
    parser.add_argument("--scan", action="store_true", help="Enable platform API and dependency scanning")
    parser.add_argument("--test", help="Test command to run for auto-test integration and validation log capture")
    parser.add_argument("--pack", action="store_true", help="Bundle generated .agent_handoff files into a single packaged XML file")
    parser.add_argument("--force", action="store_true", help="Replace durable human-authored context documents")
    parser.add_argument("--refresh", action="store_true", help="Refresh generated task metadata while preserving human-authored sections")
    parser.add_argument("--mode", choices=["analysis", "fix", "review", "handoff"], default="handoff", help="Operating mode for the incoming agent prompt")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output for lint or doctor")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)
    os.makedirs(target_dir, exist_ok=True)

    if args.action in {"lint", "doctor"}:
        raise SystemExit(print_health_report(args.action, target_dir, args.json))

    # Resolve repository subdirectories and worktrees to their actual project root.
    git_root = command_output(
        ["git", "-C", target_dir, "rev-parse", "--show-toplevel"],
        report_error=False,
    )
    if git_root:
        target_dir = git_root
    
    # Auto-migration from old .ai-context to .agent_handoff
    old_context_dir = os.path.join(target_dir, ".ai-context")
    ai_context_dir = os.path.join(target_dir, ".agent_handoff")
    if os.path.exists(old_context_dir) and not os.path.exists(ai_context_dir):
        print(f"Migrating/renaming old directory {old_context_dir} -> {ai_context_dir}")
        try:
            os.rename(old_context_dir, ai_context_dir)
        except Exception as e:
            print(f"Warning: Failed to migrate .ai-context directory: {e}")
            
    os.makedirs(ai_context_dir, exist_ok=True)

    print(f"Creating/updating AI Context Handoff documentation in: {target_dir}")
    print(f"Target language: {args.lang.upper()}")

    # 1. Fetch Git info if in a Git repo
    is_git = bool(git_root)
    git_status = "Not a git repository"
    git_diff_stat = "N/A"
    git_log = "N/A"
    git_commit_sha = "N/A"
    
    modified_files = []
    deleted_files = []

    if is_git:
        git_status = command_output("git status --short", cwd=target_dir) or "No changes (clean)"
        unstaged_stat = command_output(["git", "diff", "--stat"], cwd=target_dir)
        staged_stat = command_output(["git", "diff", "--cached", "--stat"], cwd=target_dir)
        stat_parts = []
        if staged_stat:
            stat_parts.append("Staged:\n" + staged_stat)
        if unstaged_stat:
            stat_parts.append("Unstaged:\n" + unstaged_stat)
        git_diff_stat = "\n\n".join(stat_parts) or "No tracked-file changes"
        git_log = command_output("git log --oneline -5", cwd=target_dir) or "No commits yet"
        git_commit_sha = command_output("git rev-parse HEAD", cwd=target_dir) or "N/A"
        
        status_raw = command_output("git status --porcelain", cwd=target_dir)
        if status_raw:
            for line in status_raw.splitlines():
                if len(line) > 2:
                    state = line[:2]
                    file_path = line[2:].strip()
                    if file_path.startswith('"') and file_path.endswith('"'):
                        file_path = file_path[1:-1]
                    
                    if 'D' in state:
                        deleted_files.append(file_path)
                    else:
                        modified_files.append(file_path)

    # Redact gathered git outputs
    git_status = redact_secrets(git_status)
    git_diff_stat = redact_secrets(git_diff_stat)

    suffix = ".zh-CN.md" if args.lang == "zh" else ".md"
    is_zh = (args.lang == "zh")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_id = os.environ.get("CONVERSATION_ID") or os.environ.get("SESSION_ID") or "N/A"

    # Build files list details (with physical line counts)
    changed_table_rows = []
    handoff_relevant_rows = []
    
    if modified_files:
        for f in modified_files:
            full_path = os.path.join(target_dir, f)
            lines_count = get_line_count(full_path)
            base_name = os.path.basename(f)
            changed_table_rows.append(f"| {base_name} | [{f}](../{f}) | {lines_count} |")
            handoff_relevant_rows.append(f"| {f} | Modified in this session | {lines_count} | Changed |")
    else:
        changed_table_rows.append("| N/A | N/A | N/A |")
        handoff_relevant_rows.append("| N/A | N/A | N/A | N/A |")

    git_diff_names = "\n".join(changed_table_rows)
    relevant_files_table = "\n".join(handoff_relevant_rows)

    # Build deleted files warnings
    if deleted_files:
        del_list = []
        if is_zh:
            del_list.append("> [!WARNING]\n> 检测到以下文件或目录已被删除，请注意在接手开发时同步清理相关引用和引入的模块：\n>")
        else:
            del_list.append("> [!WARNING]\n> The following files or folders have been deleted. Ensure all references and imports are cleaned up:\n>")
        
        for f in deleted_files:
            del_list.append(f"> - `{f}`")
        git_deleted_files = "\n".join(del_list)
    else:
        git_deleted_files = "- " + ("None" if not is_zh else "无")

    # Run platform API scan if enabled
    platform_api_scan_str = ""
    platform_dependencies_str = ""
    
    if args.scan:
        active_apis, apis_meta, active_deps = scan_platform_apis(target_dir)
        scan_rows = []
        dep_rows = []
        
        # 1. Platform APIs
        if active_apis:
            for api, count in active_apis.items():
                desc = apis_meta[api]
                scan_rows.append(f"| Platform API: `{api}` | {count} | {desc} |")
                dep_rows.append(f"| Platform API: `{api}` | {count} | N/A | [Describe alternative solution here] |" if not is_zh else f"| 平台 API: `{api}` | {count} | N/A | [在此描述替代技术方案] |")
        
        # 2. External dependencies
        if active_deps:
            for dep, count in sorted(active_deps.items(), key=lambda x: x[1], reverse=True):
                scan_rows.append(f"| Dependency: `{dep}` | {count} | Imported module/package |" if not is_zh else f"| 外部依赖: `{dep}` | {count} | 引入的第三方包/模块 |")
                dep_rows.append(f"| Dependency: `{dep}` | {count} | N/A | External library |" if not is_zh else f"| 外部依赖: `{dep}` | {count} | N/A | 第三方库依赖 |")
                
        if scan_rows:
            platform_api_scan_str = "\n".join(scan_rows)
            platform_dependencies_str = "\n".join(dep_rows)
        else:
            msg = "No platform specific API references or external dependencies found." if not is_zh else "未扫描到平台专属 API 引用或外部依赖。"
            platform_api_scan_str = f"- {msg}"
            platform_dependencies_str = f"| N/A | N/A | N/A | {msg} |"
    else:
        msg = "Scan not enabled. Run CLI with --scan option to check platform coupling." if not is_zh else "扫描未开启。请在 CLI 运行 --scan 参数以启动平台耦合度扫描。"
        platform_api_scan_str = f"- {msg}"
        platform_dependencies_str = f"| N/A | N/A | N/A | {msg} |"

    # Generate Code Map & Dependency Graph
    directory_layout = "- None"
    key_entry_points = "- None"
    mermaid_dependency_graph = "  Main --> App"
    
    if args.scan:
        exclude_dirs = EXCLUDED_SCAN_DIRS
        dirs_found = []
        try:
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                rel = os.path.relpath(root, target_dir)
                if rel == "." or any(p.startswith('.') for p in rel.split(os.sep)):
                    continue
                file_count = len(files)
                if file_count > 0:
                    dirs_found.append(f"- `/{rel}`: Contains {file_count} files.")
            directory_layout = "\n".join(sorted(dirs_found)) or "- None"
        except Exception:
            pass

        symbols = []
        try:
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in {".py", ".js", ".ts", ".jsx", ".tsx"}:
                        file_path = os.path.join(root, f)
                        rel_path = os.path.relpath(file_path, target_dir)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                            lines = file_obj.readlines()
                        for idx, line in enumerate(lines):
                            if ext == ".py":
                                class_match = re.match(r'^\s*class\s+([a-zA-Z0-9_]+)', line)
                                def_match = re.match(r'^\s*def\s+(main|[a-zA-Z0-9_]+_entry|start|run|init)\s*\(', line)
                                if class_match:
                                    symbols.append(f"- **Class**: `{class_match.group(1)}` in [{rel_path}](../{rel_path}#L{idx+1})")
                                elif def_match:
                                    symbols.append(f"- **Entry Function**: `{def_match.group(1)}()` in [{rel_path}](../{rel_path}#L{idx+1})")
                            elif ext in {".js", ".ts", ".jsx", ".tsx"}:
                                class_match = re.search(r'\bclass\s+([a-zA-Z0-9_]+)', line)
                                if class_match:
                                    symbols.append(f"- **Class**: `{class_match.group(1)}` in [{rel_path}](../{rel_path}#L{idx+1})")
        except Exception:
            pass
        key_entry_points = "\n".join(symbols[:20]) or "- None"

        relations = []
        seen_relations = set()
        try:
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in {".py", ".js", ".ts", ".jsx", ".tsx"}:
                        file_path = os.path.join(root, f)
                        base_name = os.path.splitext(f)[0]
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                            content = file_obj.read()
                        
                        if ext == ".py":
                            imports = re.findall(r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import', content, re.MULTILINE)
                            imports += re.findall(r'^\s*import\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
                            for imp in imports:
                                top_module = imp.split('.')[0]
                                if os.path.exists(os.path.join(target_dir, top_module)) or os.path.exists(os.path.join(target_dir, top_module + ".py")) or os.path.exists(os.path.join(root, top_module)) or os.path.exists(os.path.join(root, top_module + ".py")):
                                    if top_module != base_name:
                                        rel_str = f"  {base_name} --> {top_module}"
                                        if rel_str not in seen_relations:
                                            seen_relations.add(rel_str)
                                            relations.append(rel_str)
                        elif ext in {".js", ".ts", ".jsx", ".tsx"}:
                            imports = re.findall(r'\bfrom\s+[\'"]\.*?\/([a-zA-Z0-9_\-\/]+)[\'"]', content)
                            imports += re.findall(r'\brequire\(\s*[\'"]\.*?\/([a-zA-Z0-9_\-\/]+)[\'"]\s*\)', content)
                            for imp in imports:
                                target_base = imp.split('/')[-1]
                                if target_base != base_name:
                                    rel_str = f"  {base_name} --> {target_base}"
                                    if rel_str not in seen_relations:
                                        seen_relations.add(rel_str)
                                        relations.append(rel_str)
        except Exception:
            pass
        mermaid_dependency_graph = "\n".join(relations[:15]) or "  Main --> App"

    # Write code-map
    code_map_tpl = load_template("code-map-template.zh-CN.md" if is_zh else "code-map-template.md")
    code_map_content = code_map_tpl.format(
        directory_layout=directory_layout,
        key_entry_points=key_entry_points,
        mermaid_dependency_graph=mermaid_dependency_graph
    )
    write_document(os.path.join(ai_context_dir, f"code-map{suffix}"), code_map_content)

    # 2. Write or update target files
    # Write .agent_handoff/README.md (.zh-CN.md)
    readme_tpl = load_template("README-template.zh-CN.md" if is_zh else "README-template.md")
    write_document(os.path.join(ai_context_dir, f"README{suffix}"), readme_tpl)

    # Write or keep .agent_handoff/project.md
    proj_path = os.path.join(ai_context_dir, f"project{suffix}")
    if not os.path.exists(proj_path):
        proj_tpl = load_template("project-template.zh-CN.md" if is_zh else "project-template.md")
        proj_content = proj_tpl.format(
            project_background="待核实 / To be verified",
            tech_stack_details="- 待核实 / To be verified",
            project_modules="- 待核实 / To be verified",
            setup_commands="# Add only verified setup commands",
            build_commands="# Add only verified build and run commands"
        )
        write_document(proj_path, proj_content)

    # Write or incrementally update .agent_handoff/current-task.md
    task_path = os.path.join(ai_context_dir, f"current-task{suffix}")
    
    # Default initial values
    task_objective = args.focus if args.focus else "待确认 / To be confirmed"
    task_status = "进行中 / In Progress"
    task_checklist = "- [ ] Task 1\n- [ ] Task 2"
    task_focus = args.focus if args.focus else "Task 1"
    
    # Parse existing file to preserve user modifications
    if os.path.exists(task_path):
        try:
            with open(task_path, "r", encoding="utf-8") as f:
                existing_task_content = f.read()
            
            ext_objective = extract_markdown_section(existing_task_content, ["objective", "任务目标"])
            ext_checklist = extract_markdown_section(existing_task_content, ["task checklist", "任务清单"])
            ext_focus = extract_markdown_section(existing_task_content, ["current focus", "当前关注焦点"])
            
            status_match = re.search(r'-\s*\*\*(?:status|当前状态)\*\*:\s*([^\n\r(]+)', existing_task_content, re.IGNORECASE)
            
            if args.focus:
                task_objective = args.focus
                task_focus = args.focus
            else:
                if ext_objective:
                    task_objective = ext_objective
                if ext_focus:
                    task_focus = ext_focus

            if ext_checklist:
                task_checklist = ext_checklist
            if status_match:
                task_status = status_match.group(1).strip()
        except Exception as e:
            print(f"Warning: Failed to parse existing current-task file: {e}")

    task_tpl = load_template("current-task-template.zh-CN.md" if is_zh else "current-task-template.md")
    task_content = task_tpl.format(
        current_task_objective=task_objective,
        current_task_status=task_status,
        start_time=now_str,
        last_updated=now_str,
        task_checklist=task_checklist,
        current_focus=task_focus
    )
    if not os.path.exists(task_path) or args.force or args.focus or args.refresh:
        write_document(task_path, task_content)

    # Write .agent_handoff/changed-files.md
    changed_path = os.path.join(ai_context_dir, f"changed-files{suffix}")
    changed_tpl = load_template("changed-files-template.zh-CN.md" if is_zh else "changed-files-template.md")
    changed_content = changed_tpl.format(
        git_status=git_status,
        git_diff_stat=git_diff_stat,
        git_log=git_log,
        git_diff_names=git_diff_names,
        git_deleted_files=git_deleted_files,
        platform_api_scan=platform_api_scan_str,
        changes_summary="待确认 / To be confirmed"
    )
    write_document(changed_path, changed_content)

    # Write or keep .agent_handoff/decisions.md
    dec_path = os.path.join(ai_context_dir, f"decisions{suffix}")
    if not os.path.exists(dec_path):
        dec_tpl = load_template("decisions-template.zh-CN.md" if is_zh else "decisions-template.md")
        dec_content = dec_tpl.format(
            decision_title="待核实" if is_zh else "To be verified",
            decision_context="待核实" if is_zh else "To be verified",
            decision_details="待核实" if is_zh else "To be verified",
            decision_consequences="待核实" if is_zh else "To be verified",
            decision_status="待核实" if is_zh else "To be verified"
        )
        write_document(dec_path, dec_content)

    # Write or keep .agent_handoff/known-issues.md
    issues_path = os.path.join(ai_context_dir, f"known-issues{suffix}")
    if not os.path.exists(issues_path):
        issues_tpl = load_template("known-issues-template.zh-CN.md" if is_zh else "known-issues-template.md")
        issues_content = issues_tpl.format(
            mcp_offline_indicators="- To be verified" if not is_zh else "- 待核实",
            active_blockers="- To be verified" if not is_zh else "- 待核实",
            historical_traps="- To be verified" if not is_zh else "- 待核实",
            env_constraints="- To be verified" if not is_zh else "- 待核实"
        )
        write_document(issues_path, issues_content)

    # Run test command if provided
    test_output = "N/A"
    test_status = "Untested" if not is_zh else "未测试"
    test_cmd_used = "# Add only a verified test command" if not is_zh else "# 仅填写已经核实的测试命令"
    
    if getattr(args, 'test', None):
        test_cmd_used = args.test
        print(f"Running automated test: {args.test}...")
        try:
            res = subprocess.run(args.test, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=target_dir)
            test_output = (res.stdout or "") + "\n" + (res.stderr or "")
            test_output = test_output.strip()
            if res.returncode == 0:
                test_status = "Passed" if not is_zh else "已通过"
            else:
                test_status = "Failed" if not is_zh else "失败"
        except Exception as e:
            test_status = "Failed" if not is_zh else "失败"
            test_output = f"Error executing test command: {e}"
        print(f"Test status: {test_status}")

    # Write or keep/update .agent_handoff/validation.md
    val_path = os.path.join(ai_context_dir, f"validation{suffix}")
    
    if not os.path.exists(val_path) or args.force:
        val_tpl = load_template("validation-template.zh-CN.md" if is_zh else "validation-template.md")
        val_content = val_tpl.format(
            test_commands=test_cmd_used,
            manual_verification_steps="- To be verified" if not is_zh else "- 待核实",
            last_validation_date=now_str,
            last_validation_status=test_status,
            last_validation_output=test_output
        )
        write_document(val_path, val_content)
    elif args.test:
        try:
            with open(val_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_results_block = (
                f"## Last Verification Results\n"
                f"- **Date**: {now_str}\n"
                f"- **Status**: {test_status}\n"
                f"- **Log / Output**:\n"
                f"```\n"
                f"{test_output}\n"
                f"```"
            ) if not is_zh else (
                f"## 最近验证结果\n"
                f"- **日期**: {now_str}\n"
                f"- **状态**: {test_status}\n"
                f"- **日志 / 输出片段**:\n"
                f"```\n"
                f"{test_output}\n"
                f"```"
            )
            
            header_matches = ["## Last Verification Results", "## 最近验证结果"]
            replaced = False
            for h in header_matches:
                if h in content:
                    parts = content.split(h)
                    content = parts[0] + new_results_block
                    replaced = True
                    break
            if not replaced:
                content = content.strip() + "\n\n" + new_results_block
                
            write_document(val_path, content)
        except Exception as e:
            print(f"Warning: Failed to update existing validation file: {e}")

    # Write .agent_handoff/next-agent-prompt.md
    prompt_path = os.path.join(ai_context_dir, f"next-agent-prompt{suffix}")
    prompt_tpl = load_template("next-agent-prompt-template.zh-CN.md" if is_zh else "next-agent-prompt-template.md")
    mode_labels = {
        "analysis": "Analysis mode: inspect and explain; do not modify code without explicit approval.",
        "fix": "Fix mode: reproduce, implement the scoped fix, and verify it.",
        "review": "Review mode: report evidence-backed findings; do not modify code.",
        "handoff": "Handoff mode: validate the snapshot and continue only after confirming scope.",
    }
    mode_labels_zh = {
        "analysis": "分析模式：检查并解释；未经明确授权不要修改代码。",
        "fix": "修复模式：复现问题，实施范围内修复并完成验证。",
        "review": "审查模式：给出有证据支撑的问题，不修改代码。",
        "handoff": "交接模式：先验证快照，再在确认范围后继续。",
    }
    write_document(
        prompt_path,
        prompt_tpl.format(mode_instruction=(mode_labels_zh if is_zh else mode_labels)[args.mode]),
    )

    # Write .agent_handoff/agent-handoff.md
    handoff_path = os.path.join(ai_context_dir, f"agent-handoff{suffix}")
    handoff_tpl = load_template("agent-handoff-template.zh-CN.md" if is_zh else "agent-handoff-template.md")
    
    # Render next session focus or fallback to default
    next_session_focus_val = args.focus if args.focus else ("No specific focus given." if not is_zh else "无特定关注焦点。")

    # Generate placeholders for critical path mapping
    mermaid_business_flow = (
        "  Start --> Process --> End" if not is_zh else
        "  开始[Start] --> 业务处理[Process] --> 结束[End]"
    )
    business_flow_steps = (
        "| Step 1 | Entry | `[cli.py#L190](../agent_context_handoff/cli.py#L190)` | CLI entry execution pipeline |" if not is_zh else
        "| 步骤 1 | 请求入口 | `[cli.py#L190](../agent_context_handoff/cli.py#L190)` | CLI 入口执行流 |"
    )
    
    # Generate placeholder for obsolete legacy code
    obsolete_code_placeholder = (
        "- None" if not is_zh else
        "- 无活动废弃类 (若有 DTO 无外部调用，请在此列出以引导清理)"
    )

    handoff_content = handoff_tpl.format(
        timestamp=now_str,
        git_commit_sha=git_commit_sha,
        session_id=session_id,
        built_in_agents_count="To be verified" if not is_zh else "待核实",
        understand_anything_count="To be verified" if not is_zh else "待核实",
        online_mcps="To be verified" if not is_zh else "待核实",
        offline_mcps="To be verified" if not is_zh else "待核实",
        active_screens="To be verified" if not is_zh else "待核实",
        current_task_brief="待当前 Agent 核实并补充" if is_zh else "To be verified and completed by the current agent.",
        project_context="待当前 Agent 核实并补充" if is_zh else "To be verified and completed by the current agent.",
        tech_stack="待核实" if is_zh else "To be verified",
        relevant_files=relevant_files_table,
        mermaid_business_flow=mermaid_business_flow,
        business_flow_steps=business_flow_steps,
        platform_dependencies=platform_dependencies_str,
        completed_work="- To be verified" if not is_zh else "- 待核实",
        remaining_work="- To be verified" if not is_zh else "- 待核实",
        obsolete_code=obsolete_code_placeholder,
        current_errors="To be verified" if not is_zh else "待核实",
        confirmed_decisions="- To be verified" if not is_zh else "- 待核实",
        next_session_focus=next_session_focus_val,
        known_issues_summary="- To be verified" if not is_zh else "- 待核实",
        rejected_alternatives="| N/A | N/A |" if not is_zh else "| 无 | 无 |",
        validation_commands="# 仅填写已经核实的命令" if is_zh else "# Add only verified commands"
    )
    write_document(handoff_path, handoff_content, overwrite=args.force or not os.path.exists(handoff_path))

    # 3. Create or update AGENTS.md in target_dir
    agents_path = os.path.join(target_dir, "AGENTS.md")
    agents_section_tpl = load_template("agents-section-template.zh-CN.md" if is_zh else "agents-section-template.md")

    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
    else:
        existing_content = "# AI Agents Guide\n\nThis file serves as a guide for AI Coding Agents working on this project."

    updated_content = update_agents_handoff_section(existing_content, agents_section_tpl)
    write_document(agents_path, updated_content)
    print("Updated AGENTS.md with AI Context Handoff section.")

    if getattr(args, 'pack', False):
        package_context(ai_context_dir, target_dir, args.lang)

    git_branch = command_output(["git", "-C", target_dir, "branch", "--show-current"], report_error=False) or "N/A"
    state = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "language": args.lang,
        "git_branch": git_branch,
        "git_commit": git_commit_sha,
    }
    write_document(
        os.path.join(ai_context_dir, "state.json"),
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    )

    print("Successfully generated context files.")

if __name__ == "__main__":
    main()
