---
name: insentek-openapi
version: 1.1.0
description: >
  通过自然语言查询 insentek（东方智感）物联网设备数据。
  支持土壤墒情仪、气象站、见厘液位计等多种设备类型的实时数据、
  历史数据、趋势分析、跨设备对比与数据导出。
api_base_url: http://openapi.ecois.info
author: insentek-api-skills
guardrails:
  raw_data_output: PROHIBITED
  dry_run_preview_rows: 5
  max_chat_rows: 200
  max_export_rows: 50000
---

# Insentek OpenAPI Skill

> 轻量 Runtime Contract。完整交互规范见 `docs/interaction.md`，分析策略见 `docs/analysis.md`。
> 兼容平台：OpenClaw、Hermes-Agent、Claude Code、ChatGPT

---

## 1. Routing

用户意图 → 工具路由：

| L1 意图 | L2 输出 | 调用 |
|---------|---------|------|
| 查询数据 | 对话展示 | `query_device` → `query_data` → 按输出格式回复 |
| 查询数据 | 文件导出 | `query_device` → `export_*` → 返回文件路径 |
| 生成报告 | 文件导出 | `query_device` → `query_data` → 分析 → `write_html` |
| 对比设备 | 对话展示 | `query_device` (xN) → `query_data` (xN) → 对比表格 |
| 对比设备 | 文件导出 | `query_device` (xN) → `query_data` (xN) → `export_excel` |

**任何一层意图不明确时，MUST 向用户确认，不得假设。** 详见 `docs/interaction.md` Section 1。

---

## 2. Tools

### authenticate

用户首次提供 appid/secret 时调用，或缓存凭据失效时。

```json
{
  "appid": { "type": "string", "description": "E 生态应用 ID" },
  "secret": { "type": "string", "description": "E 生态应用密钥" }
}
```

```bash
python scripts/insentek_cli.py auth --appid ${appid} --secret ${secret}
```

成功后缓存 `appid`, `secret`, `token`, `expires_at` 到会话内存。同一会话不再询问。

---

### query_device

查询设备信息：列表、详情、别名解析。

```json
{
  "page": { "type": "integer", "default": 1 },
  "limit": { "type": "integer", "default": 20 },
  "sn": { "type": "string", "description": "设备序列号，与 alias 二选一" },
  "alias": { "type": "string", "description": "设备别名，支持部分匹配" }
}
```

```bash
# 列表
python scripts/insentek_cli.py devices --token ${token} --page ${page} --limit ${limit}
# 详情
python scripts/insentek_cli.py device --token ${token} --sn ${sn}
```

**行为：** alias → 模糊匹配 → 多匹配时反问用户 → 单匹配时缓存 alias→sn 映射。

---

### query_data

查询设备历史数据或实时数据。

```json
{
  "sn": { "type": "string", "required": true },
  "time_expression": { "type": "string", "description": "自然语言时间描述，如'现在'、'昨天'、'最近7天'。不传默认最近24小时。" },
  "range": { "type": "string", "description": "YYYYMMDD,YYYYMMDD，由 time_expression 自动计算" },
  "includeParameters": { "type": "string", "description": "指定参数，逗号分隔，如 moisture,temperature" }
}
```

```bash
# 历史数据
python scripts/insentek_cli.py data --token ${token} --sn ${sn} --range ${range} [--include-params ${params}]

# 预览（调试/验证用）
python scripts/insentek_cli.py data --token ${token} --sn ${sn} --range ${range} --dry-run

# 实时数据（latest）— 允许直接用 curl
 curl -s -H "Authorization: ${token}" "http://openapi.ecois.info/v3/device/${sn}/latest"
```

时间表达式解析见 `docs/interaction.md` Section 2。

---

### export_csv / export_excel / export_json

用户意图明确为"导出/下载"时调用，而非 `query_data`。

```bash
# CSV
python scripts/insentek_cli.py export --token ${token} --sn ${sn} --range ${range} --format csv --output ${file}.csv

# Excel
python scripts/export_excel.py --token ${token} --sn ${sn} --range ${range} --output ${file}.xlsx

# JSON
python scripts/insentek_cli.py export --token ${token} --sn ${sn} --range ${range} --format json --output ${file}.json
```

所有导出脚本均支持 `--dry-run`。

---

### write_html

Agent 完成数据分析后，将动态生成的 HTML 内容写入文件。

```bash
echo "${html_content}" | python scripts/write_html.py --output ${file}.html
```

---

## 3. Guardrails

### 3.1 硬限制

| 限制项 | 规则 | 超限处理 |
|--------|------|----------|
| 单次查询跨度 | ≤ 365 天 | 拒绝，提供拆分选项 |
| 历史回溯 | ≤ 3 年 | 拒绝，提示最早日期 |
| 对话展示 | ≤ 200 条 | 展示摘要 + 首尾各 10 条抽样 |
| 文件导出 | ≤ 50,000 条 | 拒绝，建议缩小范围或分批 |

### 3.2 数据可用性校验（MUST）

`query_data` 返回后，检查实际数据范围 vs 请求范围：

```
requested_days = 用户请求的天数
actual_days    = 实际返回数据的天数
coverage       = actual_days / requested_days

IF coverage < 0.5 OR actual_days < 7:
  → STOP
  → 告知用户实际范围，询问是否继续
  → 等待确认后才可生成报告/分析
ELSE IF actual_range < requested_range:
  → 继续，但报告 MUST 使用 actual_range 标注
```

### 3.3 原始数据输出禁令（MUST）

Agent **禁止**将原始传感器全量数据输出到对话中。

| 场景 | 处理 |
|------|------|
| "看看数据" | 统计摘要 + 首尾各 5 条 |
| "调试" | `--dry-run` 预览 |
| "给我原始数据" | 引导导出 CSV/Excel |
| "全部发给我" | 拒绝，解释 Token 限制 |

完整输出格式规范见 `docs/interaction.md` Section 4。

---

## 4. Authentication

会话内存中维护：`cached_appid`, `cached_secret`, `cached_token`, `token_expires_at`。

```
IF token 有效 (>300s 剩余):
  → 直接使用
ELIF token 即将过期 (≤300s):
  → 自动刷新（用户无感知）
ELIF 有缓存凭据但 token 失效:
  → 静默重新获取
ELSE:
  → 询问 appid/secret → 获取 token → 缓存
```

- Secret **绝不**输出到对话，**绝不**写入磁盘
- Token 仅缓存于会话内存，会话结束自动清除
- `expires` 通常为 7200s，过期前 300s 自动刷新

---

## 5. Environment Check

首次交互前执行：

```bash
python scripts/insentek_cli.py check
```

关键项失败时 STOP，可选项失败时降级运行并告知用户。

---

## 6. Error Handling

| HTTP | 处理 |
|------|------|
| 200 | 正常处理 |
| 400 | 检查参数格式后重试 |
| 401/403 | 重新认证 |
| 404 | 确认设备 SN/别名 |
| 429 | 限流，等待后重试 |
| 500 | 指数退避重试 3 次 |

脚本返回 `"success": false` 时，解析 `error` 字段：含"认证"则重认证，含"范围/限制"则解释护栏，否则展示友好错误。

---

## Notes

- **Pagination**: `page` starts at 1.
- **Values**: Nested `{node_name: {parameter_code: value}}`
- **Alias**: Case-insensitive partial match on `alias`.
- **Param names**: Use Chinese names from `/description` endpoint for display.
- **Script-first**: Prefer `scripts/insentek_cli.py` over raw `curl`.
- **Dry-run**: Append `--dry-run` for preview; never output raw data to chat.
- **Reference**: Edge cases → `reference/api-doc.md` (OpenAPI v3.1.9).
