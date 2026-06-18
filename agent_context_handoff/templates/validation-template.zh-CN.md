# 工程验证方案

[English](validation.md) | [简体中文](validation.zh-CN.md)

## 自动化测试与动态断言
执行以下命令以验证工程是否正常运行。禁止对数量进行硬编码断言（如 `wc -l` 等于 17），请使用动态状态检查：
```bash
# 验证接口响应非空且包含内置模块状态即可（不限制内置 Agent 绝对数量）
curl -s http://localhost:8000/agents | grep -q "built-in" && echo "PASS: 内置模块服务正常"

# 执行 pytest 验证
{test_commands}
```
## 手动验证步骤
{manual_verification_steps}

## 最近验证结果
- **日期**: {last_validation_date}
- **状态**: {last_validation_status} (已通过 / 失败 / 未测试)
- **日志 / 输出片段**:
```
{last_validation_output}
```
