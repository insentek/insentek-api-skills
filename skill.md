---
name: insentek-openapi
version: 1.0.2
description: >
  通过自然语言查询 insentek（东方智感）物联网设备数据。
  支持土壤墒情仪、气象站、见厘液位计等多种设备类型的实时数据、
  历史数据、趋势分析、跨设备对比与数据导出。
api_base_url: http://openapi.ecois.info
author: insentek-api-skills
guardrails:
  raw_data_output: PROHIBITED
  # Agent MUST NEVER output raw sensor full data to conversation.
  # Use --dry-run for preview, export to file for full data, or summarize.
  dry_run_preview_rows: 5
  max_chat_rows: 200
  max_export_rows: 50000
---

# Insentek OpenAPI Skill

> 让终端用户用自然语言轻松查询物联网设备数据。
> 兼容平台：OpenClaw、Hermes-Agent、Claude Code、ChatGPT

---

## 1. Intent Resolution

### 1.1 意图分层模型

Agent 必须按以下层次解析用户意图，**任何一层不明确时，必须向用户确认，不得擅自假设**。

| 层级 | 名称 | 说明 | 缺失时的处理 |
|------|------|------|-------------|
| L1 | 核心意图 | 用户想做什么？查询数据 / 对比设备 / 导出文件 / 生成报告 | 反问："您想查询数据、对比设备，还是导出报告？" |
| L2 | 输出意图 | 以什么形式呈现？对话中查看 / 生成文件 | 若 L1=查询但未明确：提供选项让用户选择 |
| L3 | 格式意图 | 文件要什么格式？CSV / Excel / JSON / HTML | 仅在 L2=文件时询问；推荐 CSV 作为默认值 |

### 1.2 意图关键词映射

| 用户关键词 | 推断 L1 | 推断 L2 | 需要确认 L3？ |
|-----------|---------|---------|--------------|
| "查一下"、"看看"、"多少"、"怎么样" | 查询数据 | 对话展示 | 否 |
| "导出"、"下载"、"保存"、"给我一份" | 查询数据 | 文件导出 | **是** |
| "生成报告"、"做一份报告"、"出份报告" | 生成报告 | 文件导出 | **是** |
| "对比"、"比较"、"哪个高" | 对比设备 | 对话展示 | 否 |
| "把对比结果导出来" | 对比设备 | 文件导出 | **是** |

### 1.3 意图不明确时的确认流程

**场景 A：用户只说了"查数据"，没说要怎么看**

```
User: "查一下3号设备上个月的数据"
Agent: "已定位到3号设备。请问您希望：
  1. 直接在对话中查看（摘要 + 趋势分析）
  2. 导出为 CSV 文件（适合 Excel 分析）
  3. 导出为 Excel 文件（含统计摘要）
  4. 生成 HTML 报告（含图表，适合分享）
  5. 导出为 JSON 文件（适合程序处理）"
```

**场景 B：用户意图完整，直接执行**

```
User: "导出3号设备上个月数据为CSV"
Agent: → 直接调用 export_csv 脚本
```

**场景 C：用户只说了"报告"，没说什么报告**

```
User: "给我一份报告"
Agent: "请问您需要：
  1. 单设备历史数据报告（选择设备和时间段）
  2. 多设备对比报告（选择对比设备）
  3. 实时状态概览报告"
```

### 1.4 快捷意图（一句话完整表达）

以下表达被视为意图完整，无需额外确认：

- "导出 [设备] [时间段] 数据为 [格式]"
- "下载 [设备] 的 [时间段] CSV"
- "生成 [设备] [时间段] 的 HTML 报告"
- "把 [设备A] 和 [设备B] [时间段] 的对比结果导出为 Excel"

---

## 2. Query Guardrails

### 2.1 硬限制规则

| 限制项 | 规则值 | 说明 |
|--------|--------|------|
| 单次查询最大跨度 | ≤ 365 天 | 防止单次请求数据量过大导致超时 |
| 历史数据最大回溯 | ≤ 3 年 | 从当前日期往前计算 |
| 对话展示最大条数 | ≤ 200 条 | Agent 上下文安全 |
| 文件导出最大条数 | ≤ 50,000 条 | 内存与生成时间安全 |

### 2.2 范围验证逻辑

```
IF 用户未提供时间范围:
  → 默认查询最近 24 小时

IF 计算出的跨度 > 365 天:
  → 拒绝查询
  → 向用户提供拆分选项:
    "单次查询最多支持 1 年范围。您查询的 [开始] 到 [结束] 共 N 天，超过限制。
     建议：
     1. 查询最近 1 年
     2. 查询 [上一年] 的数据
     3. 分批导出（拆分为多个文件）"

IF 结束日期 < 今天 - 3年:
  → 拒绝查询
  → 提示最早支持日期

IF 输出模式 == "对话展示" AND 数据条数 > 200:
  → 展示统计摘要 + 首尾各 10 条抽样
  → 提示："该时间段共 N 条数据，为您展示摘要。如需完整数据请导出文件。"

IF 输出模式 == "文件导出" AND 数据条数 > 50,000:
  → 拒绝导出
  → 提示："数据量 N 条超过导出上限 50,000 条，建议缩小时间范围或分批导出。"
```

### 2.3 用户提示消息

| 场景 | Agent 回复 |
|------|-----------|
| 跨度超限 | "单次查询最多支持 1 年范围。您查询的 [开始日期] 到 [结束日期] 共 N 天，超过限制。建议拆分为多次查询，或选择更近的时间段。" |
| 历史超限 | "系统仅保留最近 3 年数据。您查询的 [日期] 超出范围，最早支持查询到 [最早日期]。" |
| 对话展示超限 | "该时间段共有 N 条数据，为您展示统计摘要和首尾各 10 条。如需完整数据，建议导出为 CSV。" |
| 导出超限 | "数据量较大（N 条），超过单次导出上限 50,000 条。建议缩小时间范围（如改为最近 1 个月）或分批导出。" |

### 2.4 原始数据输出禁令（Raw Data Output Prohibition）

**Agent 绝对禁止将原始传感器全量数据直接输出到对话中。**

| 情景 | 处理方式 |
|------|---------|
| 用户说"看看这段数据" | 输出统计摘要 + 首尾各 5 条抽样 |
| 用户说"调试一下" | 使用 `--dry-run` 预览（数据条数、时间范围、字段摘要、前 N 条预览） |
| 用户说"给我原始数据" | 引导用户导出为 CSV/Excel 文件，而非对话输出 |
| 用户说"全部数据发给我" | 拒绝并解释："为控制 Token 消耗与提升体验，完整数据请通过文件导出获取。" |

**Why:** 传感器数据可能每小时采样一次，单次查询数百上千条。直接输出全量数据会：
1. 导致上下文窗口爆炸（Token 消耗迁增）
2. 降低模型处理效率（有效信息被淹没）
3. 影响用户阅读体验（难以聚焦关键信息）

**总之：对话中只提供摘要，文件中存储完整数据。**

---

## 3. Environment Prerequisites

Before executing any API calls or scripts, Agent **MUST** verify the runtime environment. This prevents mid-operation failures due to missing dependencies.

### 3.1 Check Trigger

Run environment check in the following situations:

| Situation | Action |
|-----------|--------|
| **First user interaction** | Run `check` once before the first API call; then check authentication state (see [4.1 Authentication Flow](#41-认证决策流程每会话一次)) |
| **Before Excel export** | Re-verify `openpyxl` is installed |
| **After script execution failure** | Run `check` to diagnose environment issues |
| **Token expired and re-auth failed** | Clear cached credentials and prompt user to re-enter |

### 3.2 Check Command

```bash
python scripts/insentek_cli.py check
```

### 3.3 Check Items

| Item | Critical? | Success Criteria | Failure Action |
|------|-----------|------------------|----------------|
| Python >= 3.8 | **Yes** | `sys.version_info >= (3, 8)` | Inform user: "需要 Python 3.8 或更高版本" |
| `insentek_cli.py` exists | **Yes** | File exists in `scripts/` | Inform user: "核心脚本缺失，请检查项目完整性" |
| `export_excel.py` exists | No | File exists in `scripts/` | Warn: "Excel 导出脚本缺失" |
| `write_html.py` exists | No | File exists in `scripts/` | Warn: "HTML 写入脚本缺失，报告生成功能不可用" |
| `openpyxl` installed | No | `import openpyxl` succeeds | Warn: "Excel 导出不可用，运行 `pip install openpyxl` 安装" |
| `curl` available | No | `curl --version` succeeds | Note: "curl 作为 fallback 不可用" |
| API reachable | No | HTTP 200/400/401 from API base | Warn: "API 服务暂时不可访问" |

### 3.4 Check Output Format

```json
{
  "success": true,
  "all_checks_passed": true,
  "checks": {
    "python": {"ok": true, "version": "3.11.0", "message": "..."},
    "scripts_cli": {"ok": true, "path": "...", "message": "..."},
    "scripts_excel": {"ok": true, "path": "...", "message": "..."},
    "openpyxl": {"ok": true, "version": "3.1.2", "message": "..."},
    "curl": {"ok": true, "message": "..."},
    "api_reachable": {"ok": true, "status": 400, "message": "..."}
  },
  "summary": {
    "critical": "通过",
    "optional": "全部通过",
    "message": "环境检查通过，所有功能可用。"
  }
}
```

### 3.5 Agent Behavior After Check

```
IF critical checks fail:
  → STOP and inform user of missing requirements
  → Provide installation/fix instructions

IF critical checks pass but optional checks fail:
  → PROCEED with limited capability
  → Inform user which features are unavailable and how to enable them
  → Example: "环境已满足基本查询需求，但 Excel 导出不可用。如需导出 Excel，请运行: pip install openpyxl"

IF all checks pass:
  → PROCEED normally
  → Optionally: "环境检查通过，所有功能就绪"
```

### 3.6 Minimal Environment Setup Guide

For users setting up the skill for the first time:

```bash
# 1. Verify Python
python --version  # >= 3.8

# 2. Install optional dependency (for Excel export)
pip install openpyxl

# 3. Verify setup
python scripts/insentek_cli.py check
```

---

## 4. Authentication

### 4.1 认证决策流程（每会话一次）

Agent 必须在**会话内存中**维护以下状态（不要写入文件）：

| 状态项 | 说明 |
|--------|------|
| `cached_appid` | 用户提供的 appid |
| `cached_secret` | 用户提供的 secret（**绝不输出到对话**） |
| `cached_token` | 当前有效的 access token |
| `token_expires_at` | token 过期时间戳（秒级 Unix timestamp） |

每次用户发起需要 API 调用的请求时，按以下优先级执行：

```
IF cached_token 存在 AND token_expires_at - now > 300 秒:
  → 使用 cached_token，直接执行 API 调用（无需任何交互）

ELIF cached_token 存在 AND token_expires_at - now <= 300 秒:
  → 自动刷新：用 cached_appid + cached_secret 重新获取 token
  → 更新 cached_token 和 token_expires_at
  → 执行 API 调用（用户无感知）

ELIF cached_appid 和 cached_secret 存在但 token 缺失/失效:
  → 用缓存的凭据获取 token
  → 执行 API 调用

ELSE:
  → 向用户询问 appid 和 secret
  → 获取后缓存到会话内存
  → 获取 token
  → 执行 API 调用
```

**核心原则：一个会话内，用户只需提供一次认证信息。**

### 4.2 首次使用引导

```
User: "查看我的设备"

Agent: （检测到无认证缓存）
  "请先提供您的 insentek 应用认证信息：
   appid 和 secret（可在 E 生态后台获取）"

User: "appid 是 xxx，secret 是 yyy"

Agent: authenticate → 缓存 appid/secret/token → query_device → 返回结果
```

### 4.3 后续使用（同一会话）

```
User: "1号大棚现在的温度"

Agent: （检测到 cached_token 有效）
  → 直接使用缓存的 token 调用 API
  → 返回结果（不再询问认证信息）

User: "再查一下湿度"

Agent: （token 仍有效）
  → 继续使用缓存的 token
  → 返回结果
```

### 4.4 脚本调用方式

**获取 token（首次或显式提供时）：**
```bash
python scripts/insentek_cli.py auth --appid ${appid} --secret ${secret}
```

**所有后续调用（使用缓存的 token）：**
```bash
python scripts/insentek_cli.py devices --token ${cached_token} ...
python scripts/insentek_cli.py data --token ${cached_token} ...
```

### 4.5 安全规范

- **Never log or display `appid`/`secret`** in conversation output
- **Never write appid/secret to disk** (session memory only)
- Token 可以显示（它已经是对外使用的凭证），但 secret 绝对不行
- 如果 token 过期且重新认证失败（如 secret 已变更），清除所有缓存并回到询问流程

### 4.6 Token 生命周期

| 阶段 | 行为 |
|------|------|
| 获取 | `expires` 通常为 7200 秒（2 小时） |
| 缓存 | 存入会话内存，后续所有调用复用 |
| 刷新阈值 | 过期前 5 分钟（300 秒）自动刷新 |
| 失效处理 | 401/403 时自动用缓存凭据重新认证 |
| 会话结束 | 所有缓存自动清除（不持久化） |

---

## 5. Tools

### 5.1 authenticate

Explicitly authenticate with the insentek API using user-provided credentials.

**When to use:**
- User explicitly provides appid/secret (first time in session)
- Cached credentials failed and user needs to re-enter
- User wants to switch to a different account

**When NOT to use:**
- Session already has valid cached token → reuse cached token directly
- Token expired but cached appid/secret available → auto re-auth silently

**Parameters:**
```json
{
  "appid": { "type": "string", "description": "在 E 生态创建的应用 ID" },
  "secret": { "type": "string", "description": "在 E 生态创建的应用密钥" }
}
```

**Agent Action:**
```bash
python scripts/insentek_cli.py auth --appid ${appid} --secret ${secret}
```

**After Success:**
1. Cache `appid`, `secret`, `token`, and `expires_at` in session memory
2. Use cached token for all subsequent API calls
3. Never ask for credentials again in this session unless re-auth fails

**Returns:**
```json
{ "token": "string", "expires": "integer (seconds)" }
```

---

### 5.2 query_device

Query device information: list all devices, get single device detail, or resolve alias to SN.

**Parameters:**
```json
{
  "page": { "type": "integer", "description": "页码，从 1 开始", "default": 1 },
  "limit": { "type": "integer", "description": "每页数量", "default": 20 },
  "sn": { "type": "string", "description": "设备序列号，与 alias 二选一" },
  "alias": { "type": "string", "description": "设备别名，支持部分匹配，与 sn 二选一" }
}
```

**Agent Action:**
```bash
# List devices
python scripts/insentek_cli.py devices --token ${token} --page ${page} --limit ${limit}

# Device detail
python scripts/insentek_cli.py device --token ${token} --sn ${sn}
```

**Agent Behavior:**
```
IF alias provided:
  → Call script devices --page 1 --limit 100
  → Find device(s) where alias contains the provided text (case-insensitive partial match)
  → IF multiple matches: ask user to specify which device
  → ELSE: call script device --sn {resolved_sn}

ELIF sn provided:
  → Call script device --sn {sn}

ELSE:
  → Call script devices --page {page} --limit {limit}
  → Return paginated device list
```

**Caching Hint:** Cache the alias→sn mapping and device metadata for the conversation.

---

### 5.3 query_data

Query device data: real-time, historical, specific moment, or incremental sync.

**Parameters:**
```json
{
  "sn": { "type": "string", "description": "设备序列号（必填）" },
  "time_expression": { "type": "string", "description": "自然语言时间描述，如'现在'、'昨天'、'最近7天'。不传则默认最近24小时。" },
  "range": { "type": "string", "description": "时间范围，格式 YYYYMMDD,YYYYMMDD。由 Agent 根据 time_expression 自动计算。" },
  "includeParameters": { "type": "string", "description": "指定返回的参数，逗号分隔（如 moisture,temperature）。不传则返回所有参数。" }
}
```

**Auto-Inference Rules:**

| Time Clue in User Query | API Endpoint | Range Calculation |
|------------------------|--------------|-------------------|
| "现在" / "最新" / "当前" / "实时" | `GET /v3/device/{sn}/latest` | — |
| "昨天" | `GET /v3/device/{sn}/data` | yesterday ~ yesterday |
| "最近7天" / "近一周" | `GET /v3/device/{sn}/data` | today-7d ~ today |
| "上周" | `GET /v3/device/{sn}/data` | last Monday ~ last Sunday |
| "本周" | `GET /v3/device/{sn}/data` | this Monday ~ today |
| "本月" | `GET /v3/device/{sn}/data` | 1st ~ today |
| "上月" | `GET /v3/device/{sn}/data` | 1st of last month ~ last day |
| "今年" | `GET /v3/device/{sn}/data` | Jan 1 ~ today |
| "某时刻" / "某个时间点" / "X点X分" | `GET /v3/device/{sn}/moment/{datetime}` | URL-encoded datetime |
| "同步" / "增量" / "更新" | `GET /v3/device/{sn}/data/incremental` | — |
| *(no time clue)* | `GET /v3/device/{sn}/data` (default) | last 24h |

**Agent Action (via script):**
```bash
# Historical data by range (with guardrails)
python scripts/insentek_cli.py data --token ${token} --sn ${sn} --range ${range} [--include-params ${params}]

# Preview mode -- DO NOT output full data to chat
python scripts/insentek_cli.py data --token ${token} --sn ${sn} --range ${range} --dry-run

# For real-time data (latest), direct API call is acceptable:
curl -s -H "Authorization: ${token}" "http://openapi.ecois.info/v3/device/${sn}/latest"
```

**Dry-Run Mode:** When debugging or previewing, ALWAYS append `--dry-run` to any `data` or `export` call. This outputs a safe preview instead of full data.

**Chain Pattern:** `query_data` requires `sn`. If user provides alias, call `query_device` first to resolve.

**Returns:**
```json
{
  "total": "integer (data points)",
  "list": [
    {
      "timestamp": "integer (Unix seconds)",
      "datetime": "string (YYYY-MM-DD HH:MM:SS)",
      "values": {
        "{node_name}": {
          "{parameter_code}": "number or string"
        }
      }
    }
  ]
}
```

---

## 6. Utility Scripts

当用户意图明确为"文件导出"时，调用以下脚本而非 `query_data`。

**注意**："生成报告"类需求不由脚本处理，由 Agent 动态分析并生成（见 [8.3](#83-深度分析报告-agent-generated-analysis-report)）。

### 6.0 dry-run 预览模式（所有导出脚本通用）

**任何导出/报告脚本均支持 `--dry-run`，Agent 在调试或预览时必须优先使用。**

```bash
python scripts/insentek_cli.py export --sn ${sn} --range ${range} --format csv --output ${filename}.csv --dry-run
python scripts/export_excel.py --sn ${sn} --range ${range} --output ${filename}.xlsx --dry-run
```

**Dry-Run 输出格式：**
```json
{
  "dry_run": true,
  "total": 1250,
  "time_range": {"start": "20250101", "end": "20250131"},
  "fields": {
    "nodes": ["10cm", "20cm", "30cm"],
    "parameters": ["moisture", "temperature", "ec"]
  },
  "preview": [
    {"timestamp": 1735689600, "datetime": "2025-01-01 00:00:00", "node": "10cm", "parameter": "moisture", "value": 23.5},
    ...
  ],
  "message": "Dry run: 1250 records, 3 nodes, 3 parameters. First 5 rows shown. Use without --dry-run to export full data."
}
```

**Dry-Run 行为：**
- 不写入任何文件
- 仅返回数据条数、时间范围、字段摘要、前 5 条抽样
- 可用于验证查询条件是否正确，再决定是否执行全量导出

### 6.1 export_csv

导出设备历史数据为 CSV 文件（UTF-8 with BOM，兼容 Excel 中文）。

**When to use:** 用户要求导出 CSV、下载数据、或需要表格文件在 Excel 中打开。

**Agent Action:**
```bash
python scripts/insentek_cli.py export \
  --token ${token} \
  --sn ${sn} \
  --range ${range} \
  --format csv \
  --output ${filename}.csv \
  [--include-params ${params}]
```

**Output:**
```json
{
  "success": true,
  "total": 1000,
  "file": "/absolute/path/to/file.csv",
  "message": "成功导出 1000 条数据到 file.csv"
}
```

**CSV Structure:**
| timestamp | datetime | node | parameter | value |
|-----------|----------|------|-----------|-------|
| 1541169181 | 2018-11-02 22:33:01 | 10cm | moisture | 12.3 |

---

### 6.2 export_excel

导出设备历史数据为 Excel 文件（多 sheet：原始数据 + 统计摘要）。

**When to use:** 用户需要带格式的表格文件，或需要统计摘要。

**Agent Action:**
```bash
python scripts/export_excel.py \
  --token ${token} \
  --sn ${sn} \
  --range ${range} \
  --output ${filename}.xlsx \
  [--include-params ${params}]
```

**Output:** 同 export_csv 的 JSON 格式。

**Excel Structure:**
- Sheet 1: "原始数据" — 所有数据点
- Sheet 2: "统计摘要" — 每参数的平均值、最小值、最大值、样本数

---

### 6.3 export_json

导出原始 API 响应为 JSON 文件，保留嵌套结构。

**When to use:** 用户是开发者，需要原始数据结构用于程序处理。

**Agent Action:**
```bash
python scripts/insentek_cli.py export \
  --token ${token} \
  --sn ${sn} \
  --range ${range} \
  --format json \
  --output ${filename}.json
```

---

### 6.4 write_html

将 AI 动态生成的 HTML 内容写入文件。本脚本不渲染模板、不处理数据，仅负责安全落盘。

**When to use:** Agent 已完成数据分析并动态构建了 HTML 内容，需要将结果保存为文件交付给用户。

**Agent Action:**
```bash
python scripts/write_html.py \
  --content "${html_content}" \
  --output ${filename}.html
```

**从 stdin 读取（适合大段内容）：**
```bash
echo "${html_content}" | python scripts/write_html.py --output ${filename}.html
```

**Output:**
```json
{
  "success": true,
  "file": "/absolute/path/to/report.html",
  "size": 15234,
  "message": "成功写入 HTML 文件: report.html (15234 bytes)",
  "warnings": []
}
```

**Validation:** 脚本会检查基本 HTML 结构（缺失标签等），但仅作为警告输出，不阻止写入。Agent 应确保生成的 HTML 是完整有效的。

---

## 7. Time Expression Parsing Guide

Convert natural language time expressions to API parameters:

| Expression | Start Date | End Date | Example (today=2025-05-13) |
|------------|-----------|----------|---------------------------|
| "最近7天" | today - 7 days | today | `20250506,20250513` |
| "昨天" | yesterday | yesterday | `20250512,20250512` |
| "本周" | this Monday | today | `20250512,20250513` |
| "上周" | last Monday | last Sunday | `20250505,20250511` |
| "本月" | 1st of month | today | `20250501,20250513` |
| "上月" | 1st of last month | last day of last month | `20250401,20250430` |
| "今年" | Jan 1 | today | `20250101,20250513` |
| "最近1个月" | today - 30 days | today | `20250413,20250513` |
| "最近3个月" | today - 90 days | today | `20250212,20250513` |
| "最近1年" | today - 365 days | today | `20240513,20250513` |
| *(default)* | today - 1 day | today | `20250512,20250513` |

**Date encoding rules:**
- Use local timezone of the user's query context
- Format as `YYYYMMDD` (no dashes or slashes)
- Range format: `startYYYYMMDD,endYYYYMMDD`
- For `/moment/{datetime}`, URL-encode as `YYYY-MM-DD HH:MM:SS`

**Range Validation:** Before every `query_data` or export script call, validate the range against [Query Guardrails](#2-query-guardrails).

---

## 8. Analysis Capabilities

分析能力由 Agent 的**动态推理能力**驱动，而非固定脚本模板。After retrieving data, the Agent should **understand the user's specific analytical intent** and perform flexible, context-aware analysis.

### 8.1 Agent-Driven Analysis Philosophy

Agent **MUST NOT** rely on hard-coded analysis templates (e.g., `generate_report.py`) for non-trivial analytical requests. Instead:

1. **Parse user intent**: What exactly does the user want to know? (correlation, anomaly detection, distribution, trend, comparison, etc.)
2. **Select appropriate methods**: Choose statistical/mathematical methods based on the question (Pearson correlation, regression, percentile analysis, rate-of-change, etc.)
3. **Compute on-the-fly**: Use Python scripts to calculate results from the retrieved data
4. **Synthesize insights**: Explain findings in natural language with domain context
5. **Generate deliverables**: Produce tables, charts, or HTML reports as requested

### 8.2 Common Analysis Patterns

The following are **examples**, not exhaustive rules. Agent should adapt to user-specific questions.

| User Question Type | Analysis Method | Example Deliverable |
|-------------------|-----------------|---------------------|
| "分析 X 和 Y 的关系" | Pearson/Spearman correlation, scatter plot | 相关系数 + 散点图 + 解释 |
| "找出异常数据" | Threshold-based or statistical outlier detection | 异常列表 + 时间标记 |
| "对比两台设备" | Side-by-side statistics + difference analysis | 对比表格 + 差异高亮 |
| "最近有什么趋势" | Linear regression, change rate calculation | 趋势方向 + 变化率 + 图表 |
| "降雨最多的几天" | Percentile or max-filtering on time series | 极值列表 + 日期 |
| "数据分布如何" | Histogram, percentile analysis (P10/P50/P90) | 分布图表 + 分位数 |
| "昼夜温差多大" | Day/night segmentation + range calculation | 昼夜统计对比表 |

**Key Principle:** The analysis output should directly answer the user's question, not just dump raw statistics.

### 8.3 深度分析报告 (Agent-Generated Analysis Report)

当用户提出具体分析需求并要求生成报告时，Agent 按以下流程执行：

```
User: "分析这台设备温湿度的关系，生成 HTML 报告"
  → query_device → resolve sn
  → query_data → retrieve data
  → Agent analyzes data (correlation, segmentation, etc.)
  → Agent dynamically constructs HTML with ECharts visualizations
  → Save HTML file → return path to user
```

**Report Generation Rules:**

1. **No fixed templates**: Each report is custom-built based on the specific analysis requested
2. **Use ECharts for visualizations**: Scatter plots, line charts, bar charts, heatmaps as appropriate
3. **Include narrative insights**: Don't just show charts — explain what they mean in context
4. **Professional styling**: Clean CSS, responsive layout, Chinese labels for all parameters
5. **One-shot generation**: Write the complete HTML in a Python script or direct file write; do NOT create reusable template scripts in the project repo
6. **Cleanup temporary scripts**: Any temporary Python scripts created solely for report generation MUST be deleted immediately after the report is generated. Only the final deliverable (HTML/CSV/Excel) should remain

**Example Report Structure:**
- Header: device info, location, time range, data count
- Key Findings: summary cards with core metrics
- Visual Analysis: interactive charts (ECharts)
- Detailed Results: tables, statistics, comparisons
- Conclusion: narrative explanation of what the data means

**Anti-pattern:** Do NOT create `generate_report_v2.py`, `analyze_correlation.py`, etc. in the project directory. Each analysis report should be generated ad-hoc.

---

## 9. Alert Detection Rules (ALERT-01)

After retrieving data, automatically scan for anomalies and mark them:

| Parameter | Alert Condition | Severity |
|-----------|----------------|----------|
| `moisture` (土壤水分) | < 5% or > 50% | Warning |
| `temperature` (温度) | Change > 10°C within 1 hour | Critical |
| `battery` (电池电压) | < 3.0V | Critical |
| `ec` (电导率) | < 0 or > 20 | Warning |
| `laserliquidLevel` (激光液位) | < 0 | Warning |

**Alert output format:**
```
⚠️ 异常数据检测
- [参数名] 在 [节点] [时间]: [值] [单位] — [异常描述]
```

---

## 10. Output Format Guide

Use the appropriate output format based on query type and user intent:

### 10.1 Real-time Data → Concise Card
```
📍 [设备别名] ([SN后4位])
─────────────────────────
🌡️ [参数中文名]: [值] [单位]  @[时间]
💧 [参数中文名]: [值] [单位]
🔋 [参数中文名]: [值] [单位]
─────────────────────────
状态: [状态描述]  |  位置: [城市]
```

### 10.2 Historical Data (Chat) → Table + Trend Summary

When data points ≤ 200:
```markdown
| 时间 | [节点1-参数1] | [节点1-参数2] | ... |
|------|--------------|--------------|-----|
| ...  | ...          | ...          | ... |

📊 趋势小结:
- [参数名]: 平均 [值], 最高 [值]@[时间], 最低 [值]@[时间], 总体[上升/下降/平稳]
```

When data points > 200:
```
📊 数据概览（共 N 条，展示摘要）

统计摘要:
| 参数 | 平均值 | 最大值 | 最小值 | 变化率 |
|------|--------|--------|--------|--------|
| ...  | ...    | ...    | ...    | ...    |

首尾抽样:
| 时间 | ... |
| ...（前10条）... |
...
| ...（后10条）... |

💡 提示: 该时间段数据量较大，如需完整数据请说"导出为CSV"。
```

### 10.3 File Export → Confirmation with File Info
```
✅ 导出成功

📄 文件: [filename.csv]
📊 数据条数: [N] 条
📅 时间范围: [开始] 至 [结束]
📥 文件路径: [绝对路径]
```

### 10.4 Comparison Analysis → Side-by-Side Table
```markdown
| 参数 | [设备A] | [设备B] | 差异 |
|------|---------|---------|------|
| ...  | ...     | ...     | ...  |
```

### 10.5 Alert Report → Marked List
```
⚠️ 检测到 N 条异常数据:
1. [时间] [节点] [参数]: [值] — [异常原因]
2. ...
```

---

## 11. Multi-Industry Adaptation

The skill auto-adapts based on device type. Do not assume a single industry context.

| Device Type Code | Industry | Typical Use Case | Key Parameters |
|-----------------|----------|-----------------|---------------|
| `Z` | Agriculture / 农业 | Soil monitoring / 土壤墒情监测 | moisture, temperature, ec |
| `T` | Meteorology / 气象 | Weather station / 气象站 | airTemperature, relativeHumidity, rainfall, wind... |
| `J` | Industry / 工业 | Liquid level monitoring / 液位监测 | laserliquidLevel, battery |

**Parameter Translation:** Use `/v3/device/{sn}/description` to translate raw parameter codes to Chinese names. Display "土壤温度" instead of "temperature" when device type is `Z`.

---

## 12. Interaction Flow Examples

### Flow 1: "查看我的设备列表"
```
User: "查看我的设备"
  → check auth state → authenticate only if no cached token
  → query_device (no sn/alias → list)
  → Return: paginated device list with status and location
```

### Flow 2: "查询某设备最新数据"
```
User: "3号设备现在温度多少"
  → check auth state → authenticate only if no cached token
  → query_device(alias="3号") → resolve sn
  → query_data(sn, time_expression="现在") → /latest
  → Return: latest temperature reading with timestamp
```

### Flow 3: "查询某设备上周历史数据（对话展示）"
```
User: "3号设备上周的土壤湿度"
  → check auth state → authenticate if needed
  → query_device(alias="3号") → resolve sn
  → query_data(sn, time_expression="上周") → /data with range
  → data points ≤ 200 → show full table + trend analysis
```

### Flow 4: "查询某设备1个月数据（意图不明确）"
```
User: "查一下3号设备1个月的数据"
  → check auth state → authenticate if needed
  → query_device(alias="3号") → resolve sn
  → Intent Resolution: L2 (output intent) is unclear
  → Agent asks: "请问您希望直接查看，还是导出为文件？"
  → User: "导出为 CSV"
  → Validate range (30 days ≤ 365 days limit) → OK
  → export_csv(sn, range, format="csv") → return file path
```

### Flow 5: "导出大数据量（超限处理）"
```
User: "导出3号设备最近2年的数据"
  → check auth state → authenticate if needed
  → query_device(alias="3号") → resolve sn
  → Calculate range: 730 days
  → Query Guardrails: 730 > 365 → REJECT
  → Agent replies: "单次查询最多支持1年范围。您查询的共730天，超过限制。
      建议：1. 查询最近1年  2. 查询前1年  3. 分批导出（2个文件）"
  → User: "分批导出"
  → export_csv(sn, range="20240513,20250513", output="data_2024-2025.csv")
  → export_csv(sn, range="20230513,20240512", output="data_2023-2024.csv")
```

### Flow 6: "生成报告"

```
User: "给3号设备生成一份上周的报告"
  → check auth state → authenticate if needed
  → query_device(alias="3号") → resolve sn
  → query_data(sn, range) → retrieve data
  → Agent analyzes data (statistics, trends, anomalies)
  → Agent dynamically constructs HTML report with ECharts visualizations
  → Save HTML file → 返回报告路径

User: "分析3号设备温湿度的关系，生成 HTML 报告"
  → check auth state → authenticate if needed
  → query_device(alias="3号") → resolve sn
  → query_data(sn, range) → retrieve data
  → Agent analyzes: Pearson correlation, day/night segmentation, etc.
  → Agent dynamically constructs HTML with scatter plot + trend chart
  → Save HTML file → 返回报告路径
```

**注意**：两种场景均由 Agent 动态分析并生成报告，不调用任何脚本模板。

### Flow 7: "多设备对比导出"
```
User: "把1号和2号设备最近一周的温度对比导出为Excel"
  → check auth state → authenticate if needed
  → query_device(alias="1号") → sn1
  → query_device(alias="2号") → sn2
  → query_data(sn1, range) + query_data(sn2, range)
  → export_excel (combined data) OR present comparison table in chat then ask if export needed
```

---

## 13. Error Handling

### 13.1 HTTP Status Codes

| HTTP Status | Meaning | Skill Action |
|-------------|---------|-------------|
| 200 | Success | Process normally |
| 400 | Bad request | Check parameter format and retry |
| 401 | Unauthorized | Re-authenticate with appid/secret |
| 403 | Forbidden | Re-authenticate (token expired) |
| 404 | Not found | Device SN may be invalid; verify with user |
| 500 | Server error | Retry up to 3 times with exponential backoff |

### 13.2 Script Error Handling

When a script returns `"success": false`, Agent should:
1. Parse the `error` field
2. If error contains "时间范围" or "超过限制" → explain guardrail to user and offer alternatives
3. If error contains "认证" or "token" → re-authenticate and retry
4. Otherwise → show user-friendly error message

### 13.3 User-Facing Error Messages

| Scenario | Message |
|---------|---------|
| 401 | "认证失败，请检查 appid 和 secret 是否正确" |
| 404 | "未找到该设备，请确认设备序列号或别名" |
| 500 (after retries) | "服务器暂时不可用，请稍后重试" |
| Range validation fail | 见 [Query Guardrails](#2-query-guardrails) |
| Export limit exceeded | "数据量较大（N 条），超过导出上限 50,000 条。建议缩小时间范围或分批导出。" |

---

## 14. Device Status Code Reference

| Code | Description | Applicable Device Types |
|------|-------------|------------------------|
| `Used` | 工作中 | Z, T |
| `Fault` | 故障中 | Z, T |
| `Online` | 在线 | Cloud devices |
| `Offline` | 离线 | Cloud devices |
| `Produce` | 生产中 | All |
| `ToBeDelivered` | 待发货 | All |
| `Repair` | 维修中 | All |
| `Idle` | 未部署 | All |
| `Scrap` | 已报废 | All |

---

## 15. Parameter Quick Reference

### Z — Soil / 土壤监测
| Code | Name | Unit |
|------|------|------|
| `temperature` | 土壤温度 | ℃ |
| `moisture` | 土壤水分 | % |
| `ec` | 电导率 | — |
| `battery` | 电池电压 | V |
| `outsideVoltage` | 外部电压 | V |

### T — Weather / 气象监测
| Code | Name | Unit |
|------|------|------|
| `airTemperature` | 空气温度 | ℃ |
| `relativeHumidity` | 相对湿度 | % |
| `dewPoint` | 露点温度 | ℃ |
| `atmosphericPressure` | 大气压力 | hPa |
| `maxWindSpeed` | 最大风速 | m/s |
| `averageWindSpeed` | 平均风速 | m/s |
| `windDirection` | 风向 | ° |
| `rainfall` | 降雨量 | mm |
| `rainfallDuration` | 降雨持续时间 | s |
| `solarRadiationIntensity` | 太阳辐射强度 | W/m² |
| `solarRadiationAmount` | 太阳辐射量 | MJ/m² |
| `sunshineDuration` | 日照时长 | h |
| `pm1.0` | PM1.0 | μg/m³ |
| `pm2.5` | PM2.5 | μg/m³ |
| `pm10` | PM10 | μg/m³ |
| `tvoc` | 总挥发性有机物 | — |

### J — Level / 见厘液位计
| Code | Name | Unit |
|------|------|------|
| `laserliquidLevel` | 激光液位 | m |
| `battery` | 电池电压 | V |
| `outsideVoltage` | 外部电压 | V |

---

## Notes

- **Pagination**: `page` starts at 1, not 0.
- **Values structure**: Nested object `{node_name: {parameter_code: value}}`
- **Token reuse**: Cache token for the entire conversation; do not request a new token for every API call.
- **Alias matching**: Use case-insensitive partial match on `alias` field from `/v3/devices`.
- **Parameter names**: Always prefer Chinese names from `/description` endpoint when displaying to users.
- **Script-first**: Agent should prefer calling `scripts/insentek_cli.py` over raw `curl` for all operations. Use `curl` only for `/latest` real-time queries or when scripts are unavailable.
- **Dry-run first**: When debugging or previewing data, always append `--dry-run` to `data` or `export` commands. Never output raw full sensor data to conversation.
- **Raw data prohibition**: Full sensor data must only be delivered via file export (CSV/Excel/JSON), never dumped into chat context.
- **Fallback reference**: This skill covers all common scenarios. Only consult `reference/api-doc.md` (original OpenAPI v3.1.9) if you encounter an edge case not addressed here — do not routinely read it.
