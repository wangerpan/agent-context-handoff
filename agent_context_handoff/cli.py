import os
import sys
import re
import argparse
import subprocess
import datetime

# Secret stripping regular expressions
SECRET_PATTERNS = [
    # API key / token / password assignments in code/text: key = "value"
    (r'(?i)(api[-_]?key|secret|token|password|pass|passwd|private[-_]?key|credential|auth)\s*[:=]\s*["\']([^"\']{4,})["\']', 
     r'\1 = "<REDACTED_SECRET>"'),
    # Generic URLs with passwords, e.g. postgres://user:password@host:port/db
    (r'([a-zA-Z+.-]+://[^/:]+:)([^/@]+)(@[^/]+)', r'\1<REDACTED_PASSWORD>\3'),
    # Standard JWT tokens
    (r'ey[a-zA-Z0-9-_]+\.ey[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+', '<REDACTED_TOKEN>'),
    # Typical SSH private keys
    (r'-----BEGIN [A-Z]+ PRIVATE KEY-----\n[\s\S]+?\n-----END [A-Z]+ PRIVATE KEY-----', '<REDACTED_PRIVATE_KEY>'),
    # Email addresses
    (r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '<REDACTED_EMAIL>'),
    # Private IP addresses (10.x.x.x, 172.16.x.x-172.31.x.x, 192.168.x.x)
    (r'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b', '<REDACTED_INTERNAL_HOST>')
]

def redact_secrets(content):
    """Sanitize secrets from content using regex."""
    sanitized = content
    for pattern, replacement in SECRET_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized

def run_command(cmd, cwd=None):
    """Run a shell command and return its output."""
    try:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def load_template(template_name):
    """Load template content from the package templates directory."""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_path = os.path.join(templates_dir, template_name)
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def get_line_count(file_path):
    """Get the physical line count of a file."""
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
    except Exception:
        pass
    return "N/A"

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
    parser.add_argument("--lang", choices=["en", "zh"], default="en", help="Language for handoff docs (en or zh)")
    parser.add_argument("--dir", default=".", help="Target directory (default: current directory)")
    parser.add_argument("--focus", default="", help="Focus or objective for the next session/agent")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)
    ai_context_dir = os.path.join(target_dir, ".ai-context")
    os.makedirs(ai_context_dir, exist_ok=True)

    print(f"Creating/updating AI Context Handoff documentation in: {target_dir}")
    print(f"Target language: {args.lang.upper()}")

    # 1. Fetch Git info if in a Git repo
    is_git = os.path.isdir(os.path.join(target_dir, ".git"))
    git_status = "Not a git repository"
    git_diff_stat = "N/A"
    git_log = "N/A"
    git_commit_sha = "N/A"
    
    modified_files = []
    deleted_files = []

    if is_git:
        git_status = run_command("git status --short", cwd=target_dir) or "No changes (clean)"
        git_diff_stat = run_command("git diff --stat", cwd=target_dir) or "No code changes"
        git_log = run_command("git log --oneline -5", cwd=target_dir) or "No commits yet"
        git_commit_sha = run_command("git rev-parse HEAD", cwd=target_dir) or "N/A"
        
        # Parse porcelain status to categorize modified vs deleted files
        status_raw = run_command("git status --porcelain", cwd=target_dir)
        if status_raw:
            for line in status_raw.splitlines():
                if len(line) > 2:
                    state = line[:2]
                    file_path = line[2:].strip()
                    # Strip quotes if filename has spaces
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
            changed_table_rows.append(f"| {base_name} | [{f}](file://./{f}) | {lines_count} |")
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

    # 2. Write or update target files
    # Write .ai-context/README.md (.zh-CN.md)
    readme_tpl = load_template("README-template.zh-CN.md" if is_zh else "README-template.md")
    with open(os.path.join(ai_context_dir, f"README{suffix}"), "w", encoding="utf-8") as f:
        f.write(readme_tpl)

    # Write or keep .ai-context/project.md
    proj_path = os.path.join(ai_context_dir, f"project{suffix}")
    if not os.path.exists(proj_path):
        proj_tpl = load_template("project-template.zh-CN.md" if is_zh else "project-template.md")
        proj_content = proj_tpl.format(
            project_background="待确认 / To be confirmed",
            tech_stack_details="- Language:\n- Framework:",
            project_modules="- `/src`: source\n- `/tests`: tests",
            setup_commands="pip install -r requirements.txt",
            build_commands="python3 main.py"
        )
        with open(proj_path, "w", encoding="utf-8") as f:
            f.write(proj_content)

    # Write or incrementally update .ai-context/current-task.md
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
    with open(task_path, "w", encoding="utf-8") as f:
        f.write(task_content)

    # Write .ai-context/changed-files.md
    changed_path = os.path.join(ai_context_dir, f"changed-files{suffix}")
    changed_tpl = load_template("changed-files-template.zh-CN.md" if is_zh else "changed-files-template.md")
    changed_content = changed_tpl.format(
        git_status=git_status,
        git_diff_stat=git_diff_stat,
        git_diff_names=git_diff_names,
        git_deleted_files=git_deleted_files,
        changes_summary="待确认 / To be confirmed"
    )
    with open(changed_path, "w", encoding="utf-8") as f:
        f.write(changed_content)

    # Write or keep .ai-context/decisions.md
    dec_path = os.path.join(ai_context_dir, f"decisions{suffix}")
    if not os.path.exists(dec_path):
        dec_tpl = load_template("decisions-template.zh-CN.md" if is_zh else "decisions-template.md")
        dec_content = dec_tpl.format(
            decision_title="初始化架构决策",
            decision_context="需要确定跨 Agent 交接的规范形式",
            decision_details="选择使用标准 Markdown 模板并放在 .ai-context/ 目录下",
            decision_consequences="所有支持 Markdown 读取 of AI Agent 都可以无感阅读该上下文",
            decision_status="已批准" if is_zh else "Approved"
        )
        with open(dec_path, "w", encoding="utf-8") as f:
            f.write(dec_content)

    # Write or keep .ai-context/known-issues.md
    issues_path = os.path.join(ai_context_dir, f"known-issues{suffix}")
    if not os.path.exists(issues_path):
        issues_tpl = load_template("known-issues-template.zh-CN.md" if is_zh else "known-issues-template.md")
        issues_content = issues_tpl.format(
            mcp_offline_indicators="- headroom: [OFFLINE] / [离线]",
            active_blockers="- None" if not is_zh else "- 无",
            historical_traps="- None" if not is_zh else "- 无",
            env_constraints="- Git CLI needs to be installed" if not is_zh else "- 需在支持 Git 的环境下运行"
        )
        with open(issues_path, "w", encoding="utf-8") as f:
            f.write(issues_content)

    # Write or keep .ai-context/validation.md
    val_path = os.path.join(ai_context_dir, f"validation{suffix}")
    if not os.path.exists(val_path):
        val_tpl = load_template("validation-template.zh-CN.md" if is_zh else "validation-template.md")
        val_content = val_tpl.format(
            test_commands="pytest" if not is_zh else "pytest",
            manual_verification_steps="- Run the application manually and test handoff files" if not is_zh else "- 手动验证生成的上下文文件",
            last_validation_date=now_str,
            last_validation_status="Untested" if not is_zh else "未测试",
            last_validation_output="N/A"
        )
        with open(val_path, "w", encoding="utf-8") as f:
            f.write(val_content)

    # Write .ai-context/next-agent-prompt.md
    prompt_path = os.path.join(ai_context_dir, f"next-agent-prompt{suffix}")
    prompt_tpl = load_template("next-agent-prompt-template.zh-CN.md" if is_zh else "next-agent-prompt-template.md")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_tpl)

    # Write .ai-context/agent-handoff.md
    handoff_path = os.path.join(ai_context_dir, f"agent-handoff{suffix}")
    handoff_tpl = load_template("agent-handoff-template.zh-CN.md" if is_zh else "agent-handoff-template.md")
    
    # Render next session focus or fallback to default
    next_session_focus_val = args.focus if args.focus else ("No specific focus given." if not is_zh else "无特定关注焦点。")

    # Generate placeholder for core helper methods to remind developers
    private_methods_placeholder = (
        "| N/A | N/A | N/A |" if not is_zh else
        "| 方法名 | 调用/触发场景 | 作用与数据转换职责 (待 Agent 补充) |"
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
        built_in_agents_count="17 (built-in)" if not is_zh else "17个 (内置)",
        understand_anything_count="9 (understand-anything)" if not is_zh else "9个 (理解类)",
        online_mcps="N/A" if not is_zh else "暂无",
        offline_mcps="headroom [OFFLINE] / [离线]",
        active_screens="N/A" if not is_zh else "暂无",
        current_task_brief="开发/生成 agent-context-handoff Skill" if is_zh else "Develop/generate agent-context-handoff Skill",
        project_context="自动压缩/打包当前 Coding Agent 上下文" if is_zh else "Automated compression of Coding Agent context",
        tech_stack="Python / Shell / Markdown",
        relevant_files=relevant_files_table,
        private_methods=private_methods_placeholder,
        completed_work="- Init repo\n- Create templates\n- Implement CLI" if not is_zh else "- 初始化仓库\n- 创建模板\n- 实现 CLI",
        remaining_work="- Validate locally\n- Publish to GitHub" if not is_zh else "- 本地验证\n- 发布到 GitHub",
        obsolete_code=obsolete_code_placeholder,
        current_errors="None" if not is_zh else "无",
        confirmed_decisions="- Standardized folder layout '.ai-context/'" if not is_zh else "- 标准化 '.ai-context/' 目录结构",
        next_session_focus=next_session_focus_val,
        known_issues_summary="- headroom: [OFFLINE] / [离线] \n- No active blockers" if not is_zh else "- headroom: [离线] \n- 无活动阻塞项",
        rejected_alternatives="| N/A | N/A |" if not is_zh else "| 无 | 无 |",
        validation_commands="python3 -m agent_context_handoff.cli --lang zh" if is_zh else "python3 -m agent_context_handoff.cli --lang en"
    )
    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(handoff_content)

    # 3. Create or update AGENTS.md in target_dir
    agents_path = os.path.join(target_dir, "AGENTS.md")
    agents_section_tpl = load_template("agents-section-template.zh-CN.md" if is_zh else "agents-section-template.md")

    needs_section = True
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
        if "AI Context Handoff" in existing_content:
            needs_section = False
    else:
        existing_content = "# AI Agents Guide\n\nThis file serves as a guide for AI Coding Agents working on this project."

    if needs_section:
        updated_content = existing_content + "\n" + agents_section_tpl
        with open(agents_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("Updated AGENTS.md with AI Context Handoff section.")
    else:
        print("AGENTS.md already contains AI Context Handoff section. Skipping append.")

    print("Successfully generated context files.")

if __name__ == "__main__":
    main()
