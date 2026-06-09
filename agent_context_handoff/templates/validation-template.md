# Project Validation Plan

[English](validation.md) | [简体中文](validation.zh-CN.md)

## Automated Tests / Dynamic Assertions
Commands to verify correct operation. Avoid hardcoding exact counts (e.g. `wc -l` count of 17). Use dynamic checks:
```bash
# Verify the active agent API returns a non-empty payload containing built-in status
curl -s http://localhost:8000/agents | grep -q "built-in" && echo "PASS: Built-in agents present"

# Run pytest verification
{test_commands}
```

## Manual Verification Steps
{manual_verification_steps}

## Last Verification Results
- **Date**: {last_validation_date}
- **Status**: {last_validation_status} (Passed / Failed / Untested)
- **Log / Output**:
```
{last_validation_output}
```
