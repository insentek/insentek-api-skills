# Unified API-to-Skill Mapping

> Synthesized from: `auth-mapping.md` + `device-api-mapping.md` + `data-api-mapping.md`
> Purpose: Phase 2 skill.md writer should be able to write the complete skill file using ONLY this document + the three source mapping documents
> Locked Decisions: D-01 through D-12

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| **Total endpoints in scope** | 10 general + 1 optional webhook |
| **Total skill tools** | 3 core (`authenticate`, `query_device`, `query_data`) + 1 optional (`config_webhook`) |
| **Aggregation strategy** | Scene-based, NOT 1:1 endpoint mapping |
| **Deferred endpoints** | 4 (pluviometer ×3, lingyun) — Phase 2+ extensions |

**Design Philosophy:** Users speak in natural language about devices and data. The skill translates user intent into the minimal set of API calls, handling alias resolution, time parsing, and token management automatically.

---

## 2. Endpoint Inventory Table

| # | Endpoint | Method | In Scope? | Skill Tool | Notes |
|---|----------|--------|-----------|------------|-------|
| 1 | `/v3/token` | GET | Yes | `authenticate` | Auth entry point |
| 2 | `/v3/devices` | GET | Yes | `query_device` | Device list |
| 3 | `/v3/device/{sn}` | GET | Yes | `query_device` | Single device detail |
| 4 | `/v3/device/{sn}/description` | GET | Yes | `query_device` | Parameter meanings |
| 5 | `/v3/device/{sn}/data` | GET | Yes | `query_data` | Historical data |
| 6 | `/v3/device/{sn}/latest` | GET | Yes | `query_data` | Real-time data |
| 7 | `/v3/device/{sn}/data/moment/{datetime}` | GET | Yes | `query_data` | Specific moment data |
| 8 | `/v3/device/{sn}/data/incremental` | GET | Yes | `query_data` | Incremental sync |
| 9 | `/v3/device/{sn}/attr` | POST | Optional | — | Advanced config (write op) |
| 10 | `/v3/device/webhook` | GET/POST | Optional | `config_webhook` | Webhook configuration |
| 11 | `/v3/device/pluviometer/{sn}/data/stats` | GET | **Deferred** | — | Phase 2+ |
| 12 | `/v3/device/pluviometer/{sn}/data/history` | GET | **Deferred** | — | Phase 2+ |
| 13 | `/v3/device/pluviometer/{sn}/data/latest` | GET | **Deferred** | — | Phase 2+ |
| 14 | `/v3/device/lingyun/{sn}/service` | GET | **Deferred** | — | Phase 2+ |

---

## 3. Skill Tool Definitions

### 3.1 authenticate

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Obtain and manage API access token |
| **Mapped Endpoint** | `GET /v3/token` |
| **Parameters** | `appid` (String, required), `secret` (String, required) |
| **Returns** | `token` (String), `expires` (Integer, seconds) |
| **Behavior** | 1. Call `/v3/token` with appid + secret → 2. Cache token + expires → 3. Reuse for all subsequent calls |
| **Auto-Refresh** | On 401/403 or when expiry is within 5 minutes |
| **Error Handling** | 401 → "认证失败，请检查 appid 和 secret 是否正确"; 500 → retry 3x then fail |

**Prompt Instruction:**
```markdown
Before making any API calls, authenticate using the user's appid and secret:
1. Call `GET /v3/token?appid={appid}&secret={secret}`
2. Cache the returned `token` and calculate `expires_at = now + expires_seconds`
3. Include `Authorization: {token}` header in all subsequent requests
4. When a call returns 401/403, or when token expires within 5 minutes, automatically re-authenticate
```

**References:** D-10, D-11, D-12, AUTH-01, AUTH-02

---

### 3.2 query_device

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Query device information (list, detail, parameter meanings) |
| **Mapped Endpoints** | `/v3/devices` + `/v3/device/{sn}` + `/v3/device/{sn}/description` |
| **Parameters** | `page` (Integer, opt, default 1), `limit` (Integer, opt, default 20), `sn` (String, opt), `alias` (String, opt) |
| **Returns** | Device list or single device detail with parameter meanings |

**Agent Behavior:**

```
IF alias provided:
  → Call /v3/devices → find matching device by alias
  → Call /v3/device/{sn} + /v3/device/{sn}/description
  
ELIF sn provided:
  → Call /v3/device/{sn} + /v3/device/{sn}/description
  
ELSE:
  → Call /v3/devices with page/limit
  → Return paginated device list
```

**Alias Resolution:** Use partial matching on `alias` field from `/v3/devices` response. If multiple matches, ask user to specify.

**Chain Pattern:** Often called before `query_data` to resolve `sn` from `alias`:
```
User: "查一下 3 号设备的温度"
  → query_device(alias="3号") → sn="00000000000003"
  → query_data(sn="00000000000003", time_expression="现在")
```

**References:** D-04, D-06, DEV-01, DEV-02

---

### 3.3 query_data

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Query device data (historical, real-time, moment, incremental) |
| **Mapped Endpoints** | `/data` + `/latest` + `/moment/{datetime}` + `/incremental` |
| **Parameters** | `sn` (String, req), `time_expression` (String, opt), `range` (String, opt), `includeParameters` (String, opt) |
| **Returns** | Data points with timestamp, datetime, and nested values |

**Auto-Inference Rules (per D-05, D-07, D-08):**

| Time Clue in User Query | Endpoint | Range |
|------------------------|----------|-------|
| "现在" / "最新" / "当前" / "实时" | `/latest` | — |
| "昨天" | `/data` | yesterday ~ yesterday |
| "最近7天" / "近一周" | `/data` | today-7d ~ today |
| "上周" | `/data` | last Monday ~ last Sunday |
| "本周" | `/data` | this Monday ~ today |
| "本月" | `/data` | 1st ~ today |
| "上月" | `/data` | 1st of last month ~ last day |
| "今年" | `/data` | Jan 1 ~ today |
| "某时刻" / "某个时间点" | `/moment/{datetime}` | URL-encoded datetime |
| "同步" / "增量" / "更新" | `/incremental` | — |
| *(no time clue)* | `/data` (default) | last 24h |

**Date Format:** `YYYYMMDD,YYYYMMDD` (per D-09)

**Default Behavior (per D-08):** When no time clue provided, query last 24 hours.

**Parameter Filtering:** When user asks for specific metrics (e.g., "土壤湿度"), extract parameter codes and pass to `includeParameters`.

**Chain Pattern (per D-06):**
```
User: "查一下 3 号设备的温度"
  → query_device(alias="3号") → resolve sn
  → query_data(sn=resolved_sn, time_expression="现在")
```

**References:** D-04, D-05, D-06, D-07, D-08, D-09, DATA-01, DATA-02

---

### 3.4 config_webhook (Optional)

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Configure data push webhook URL |
| **Mapped Endpoints** | `GET /v3/device/webhook` (query), `POST /v3/device/webhook` (set) |
| **Parameters** | `notifyUrl` (URL, required for POST) |
| **Returns** | Current webhook URL and last modified time |
| **Note** | Optional — advanced configuration, not core data query |

**References:** D-02

---

## 4. Interaction Flow Diagrams

### Flow 1: "查看我的设备列表"

```
User: "查看我的设备"
  → authenticate (if token not cached)
  → query_device (no sn/alias → list)
  → Return: paginated device list with status and location
```

### Flow 2: "查询某设备最新数据"

```
User: "3号设备现在温度多少"
  → authenticate (if needed)
  → query_device(alias="3号") → resolve sn
  → query_data(sn, time_expression="现在") → /latest
  → Return: latest temperature reading with timestamp
```

### Flow 3: "查询某设备上周历史数据"

```
User: "3号设备上周的土壤湿度"
  → authenticate (if needed)
  → query_device(alias="3号") → resolve sn
  → query_data(sn, time_expression="上周") → /data with calculated range
  → Return: historical moisture data points for last week
```

### Flow 4: "查询某时刻数据"

```
User: "3号设备昨天中午12点的数据"
  → authenticate (if needed)
  → query_device(alias="3号") → resolve sn
  → query_data(sn, time_expression="昨天中午12点") → /moment/{datetime}
  → Return: data at specified moment
```

### Flow 5: "多设备对比"

```
User: "对比一下1号和2号设备的温度"
  → authenticate (if needed)
  → query_device(alias="1号") → sn1
  → query_device(alias="2号") → sn2
  → query_data(sn1, time_expression="现在")
  → query_data(sn2, time_expression="现在")
  → Return: comparison table of temperatures
```

---

## 5. Deferred Endpoints Reference

| Endpoint | Method | Description | Proposed Future Skill Tool |
|----------|--------|-------------|---------------------------|
| `/v3/device/pluviometer/{sn}/data/stats` | GET | 雨量计统计 | `query_pluviometer_stats` |
| `/v3/device/pluviometer/{sn}/data/history` | GET | 雨量计历史 | `query_pluviometer_history` |
| `/v3/device/pluviometer/{sn}/data/latest` | GET | 雨量计最新 | `query_pluviometer_latest` |
| `/v3/device/lingyun/{sn}/service` | GET | 灵云服务调用 | `call_lingyun_service` |

**Note:** These endpoints are device-type-specific and not included in the general skill. They may be added as extension packs in Phase 2+.

**References:** D-03

---

## 6. Cross-Reference Index

### Document → Skill Tool Mapping

| Source Document | Skill Tool | Section |
|-----------------|------------|---------|
| `auth-mapping.md` | `authenticate` | §3.1 |
| `device-api-mapping.md` | `query_device` | §3.2 |
| `data-api-mapping.md` | `query_data` | §3.3 |

### Requirement → Skill Tool Mapping

| Requirement | Description | Skill Tool |
|-------------|-------------|------------|
| AUTH-01 | API 认证引导说明 | `authenticate` |
| AUTH-02 | 认证错误处理 | `authenticate` (error handling) |
| DEV-01 | 设备列表查询能力 | `query_device` |
| DEV-02 | 单设备信息查询能力 | `query_device` |
| DATA-01 | 设备实时数据查询能力 | `query_data` |
| DATA-02 | 设备历史数据查询能力 | `query_data` |

### Decision → Skill Tool Mapping

| Decision | Description | Skill Tool |
|----------|-------------|------------|
| D-01 | 10 general endpoints in scope | All tools |
| D-02 | Webhook as optional tool | `config_webhook` |
| D-03 | 4 specialized endpoints deferred | — (Phase 2+) |
| D-04 | Scene aggregation | `query_device` + `query_data` |
| D-05 | Agent auto-infers query type | `query_data` |
| D-06 | Chain calling | `query_device` → `query_data` |
| D-07 | Natural language time parsing | `query_data` |
| D-08 | Default last 24h | `query_data` |
| D-09 | Range format "YYYYMMDD,YYYYMMDD" | `query_data` |
| D-10 | `authenticate` tool with appid + secret | `authenticate` |
| D-11 | Token expiry detection + auto-refresh | `authenticate` |
| D-12 | Conversation-level token reuse | `authenticate` |

---

## 7. Data Type Reference

### Common Response Wrapper

All API responses follow this wrapper structure:

```json
{
  "message": "ok",
  // ... endpoint-specific fields
}
```

| message value | Meaning |
|---------------|---------|
| `"ok"` | Success |
| `"error"` or other | Error (check HTTP status) |

### Timestamp vs DateTime

| Field | Format | Example |
|-------|--------|---------|
| `timestamp` | Unix timestamp (seconds) | `1541169181` |
| `datetime` | `YYYY-MM-DD HH:MM:SS` | `"2018-11-02 22:33:01"` |

### Values Nested Structure

```json
{
  "{node_name}": {
    "{parameter_code}": {numeric_value},
    "{parameter_code}": {numeric_value}
  }
}
```

Example:
```json
{
  "10cm": {
    "moisture": 12.3,
    "temperature": 10.7
  },
  "20cm": {
    "moisture": 12.3,
    "temperature": 9.9
  }
}
```

---

## 8. Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    insentek API Skill                        │
├─────────────────────────────────────────────────────────────┤
│ authenticate(appid, secret) → token, expires               │
├─────────────────────────────────────────────────────────────┤
│ query_device(page?, limit?, sn?, alias?)                   │
│   → list: /v3/devices                                      │
│   → detail: /v3/device/{sn} + /description                 │
├─────────────────────────────────────────────────────────────┤
│ query_data(sn, time_expression?, includeParameters?)       │
│   → "现在" → /latest                                       │
│   → "某时刻" → /moment/{datetime}                          │
│   → "同步" → /incremental                                  │
│   → default → /data with last 24h                          │
├─────────────────────────────────────────────────────────────┤
│ config_webhook(notifyUrl?) → webhook config (optional)     │
└─────────────────────────────────────────────────────────────┘
```

---

*This document is self-contained. Phase 2 skill.md writer should be able to write the complete skill file using ONLY this document + the three source mapping documents, without reading the PDF or source code.*
