---
name: insentek-openapi
version: 1.0.0
description: >
  通过自然语言查询 insentek（东方智感）物联网设备数据。
  支持土壤墒情仪、气象站、见厘液位计等多种设备类型的实时数据、
  历史数据、趋势分析与跨设备对比。
api_base_url: http://openapi.ecois.info
author: insentek-api-skills
---

# Insentek OpenAPI Skill

> 让终端用户用自然语言轻松查询物联网设备数据。
> 兼容平台：OpenClaw、Hermes-Agent、Claude Code、ChatGPT

---

## Authentication

Before making any API calls, authenticate using the user's `appid` and `secret`:

1. Call `GET /v3/token?appid={appid}&secret={secret}`
2. Cache the returned `token` and calculate `expires_at = now + expires_seconds`
3. Include `Authorization: {token}` header in all subsequent requests
4. When a call returns 401/403, or when token expires within 5 minutes, automatically re-authenticate

**Security Note**: Never log or display `appid`/`secret` in conversation output.

---

## Tools

### authenticate

Authenticate with the insentek API and obtain an access token.

**Parameters:**
```json
{
  "appid": {
    "type": "string",
    "description": "在 E 生态创建的应用 ID"
  },
  "secret": {
    "type": "string",
    "description": "在 E 生态创建的应用密钥"
  }
}
```

**Returns:**
```json
{
  "token": "string",
  "expires": "integer (seconds)"
}
```

**Behavior:**
- Call `GET /v3/token?appid={appid}&secret={secret}`
- Cache token for conversation-level reuse
- Auto-refresh when expiry is within 5 minutes or on 401/403

---

### query_device

Query device information: list all devices, get single device detail, or resolve alias to SN.

**Parameters:**
```json
{
  "page": {
    "type": "integer",
    "description": "页码，从 1 开始",
    "default": 1
  },
  "limit": {
    "type": "integer",
    "description": "每页数量",
    "default": 20
  },
  "sn": {
    "type": "string",
    "description": "设备序列号（唯一标识），与 alias 二选一"
  },
  "alias": {
    "type": "string",
    "description": "设备别名，支持部分匹配，与 sn 二选一"
  }
}
```

**Agent Behavior:**

```
IF alias provided:
  → Call GET /v3/devices?page=1&limit=100
  → Find device(s) where alias contains the provided text (case-insensitive partial match)
  → IF multiple matches: ask user to specify which device
  → ELSE: call GET /v3/device/{sn} + GET /v3/device/{sn}/description

ELIF sn provided:
  → Call GET /v3/device/{sn} + GET /v3/device/{sn}/description

ELSE:
  → Call GET /v3/devices?page={page}&limit={limit}
  → Return paginated device list
```

**Returns (list mode):**
```json
{
  "count": "integer (total devices)",
  "list": [
    {
      "sn": "string",
      "alias": "string",
      "type": "string (device type code)",
      "series": "string",
      "authorized": "string (own/shared)",
      "status": { "code": "string", "description": "string" },
      "location": { "lng": "number", "lat": "number", "province": "string", "city": "string" }
    }
  ]
}
```

**Returns (detail mode):**
Single device detail enriched with parameter descriptions from `/v3/device/{sn}/description`.

**Alias Resolution Example:**
```
User: "查一下 3 号设备的温度"
  → query_device(alias="3号") → sn="00000000000003"
  → query_data(sn="00000000000003", time_expression="现在")
```

**Caching Hint:** Cache the alias→sn mapping and token→device mapping for the conversation to avoid repeated queries.

---

### query_data

Query device data: real-time, historical, specific moment, or incremental sync.

**Parameters:**
```json
{
  "sn": {
    "type": "string",
    "description": "设备序列号（必填）"
  },
  "time_expression": {
    "type": "string",
    "description": "自然语言时间描述，如'现在'、'昨天'、'最近7天'。不传则默认最近24小时。"
  },
  "range": {
    "type": "string",
    "description": "时间范围，格式 YYYYMMDD,YYYYMMDD。通常由 Agent 根据 time_expression 自动计算，无需用户填写。"
  },
  "includeParameters": {
    "type": "string",
    "description": "指定返回的参数，逗号分隔（如 moisture,temperature）。不传则返回所有参数。"
  }
}
```

**Auto-Inference Rules:**

| Time Clue in User Query | API Endpoint | Range Calculation |
|------------------------|--------------|-------------------|
| "现在" / "最新" / "当前" / "实时" | `/latest` | — |
| "昨天" | `/data` | yesterday ~ yesterday |
| "最近7天" / "近一周" | `/data` | today-7d ~ today |
| "上周" | `/data` | last Monday ~ last Sunday |
| "本周" | `/data` | this Monday ~ today |
| "本月" | `/data` | 1st ~ today |
| "上月" | `/data` | 1st of last month ~ last day |
| "今年" | `/data` | Jan 1 ~ today |
| "某时刻" / "某个时间点" / "X点X分" | `/moment/{datetime}` | URL-encoded datetime |
| "同步" / "增量" / "更新" | `/incremental` | — |
| *(no time clue)* | `/data` (default) | last 24h |

**Date Format:** `YYYYMMDD,YYYYMMDD` (no separators, both inclusive)

**Default Behavior:** When no time clue provided, query last 24 hours.

**Parameter Filtering:** When user asks for specific metrics, extract parameter codes and pass to `includeParameters`.

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

## Time Expression Parsing Guide

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
| *(default)* | today - 1 day | today | `20250512,20250513` |

**Date encoding rules:**
- Use local timezone of the user's query context
- Format as `YYYYMMDD` (no dashes or slashes)
- Range format: `startYYYYMMDD,endYYYYMMDD`
- For `/moment/{datetime}`, URL-encode as `YYYY-MM-DD HH:MM:SS`

---

## Analysis Capabilities

The skill supports analytical operations through Prompt instructions. After retrieving data, the Agent should automatically perform the following analyses when relevant:

### Trend Analysis (ANALYSIS-01)

When user queries historical data over multiple data points:

1. **Calculate statistics** for each parameter across the time range:
   - Average (平均值)
   - Maximum (最大值) and timestamp
   - Minimum (最小值) and timestamp
   - Change rate (变化率) = (last - first) / first × 100%

2. **Identify trends**:
   - Rising (上升): values generally increasing
   - Falling (下降): values generally decreasing
   - Stable (平稳): values within ±10% of average
   - Fluctuating (波动): no clear direction

### Cross-Device Comparison (ANALYSIS-02)

When user asks to compare multiple devices:

1. Query each device's data using the same time range
2. Present results in a side-by-side comparison table
3. Highlight differences:
   - Calculate absolute difference for each parameter
   - Mark which device has higher/lower values
   - Note any parameters present in one device but not the other

---

## Alert Detection Rules (ALERT-01)

After retrieving data, automatically scan for anomalies and mark them:

| Parameter | Alert Condition | Severity |
|-----------|----------------|----------|
| `moisture` (土壤水分) | < 5% or > 50% | ⚠️ Warning |
| `temperature` (温度) | Change > 10°C within 1 hour | 🔴 Critical |
| `battery` (电池电压) | < 3.0V | 🔴 Critical |
| `ec` (电导率) | < 0 or > 20 | ⚠️ Warning |
| `laserliquidLevel` (激光液位) | < 0 | ⚠️ Warning |

**Alert output format:**
```
⚠️ 异常数据检测
- [参数名] 在 [节点] [时间]: [值] [单位] — [异常描述]
```

---

## Output Format Guide

Use the appropriate output format based on query type:

### Real-time Data → Concise Card
```
📍 [设备别名] ([SN后4位])
─────────────────────────
🌡️ [参数中文名]: [值] [单位]  @[时间]
💧 [参数中文名]: [值] [单位]
🔋 [参数中文名]: [值] [单位]
─────────────────────────
状态: [状态描述]  |  位置: [城市]
```

### Historical Data → Table + Trend Summary
```markdown
| 时间 | [节点1-参数1] | [节点1-参数2] | ... |
|------|--------------|--------------|-----|
| ...  | ...          | ...          | ... |

📊 趋势小结:
- [参数名]: 平均 [值], 最高 [值]@[时间], 最低 [值]@[时间], 总体[上升/下降/平稳]
```

### Comparison Analysis → Side-by-Side Table
```markdown
| 参数 | [设备A] | [设备B] | 差异 |
|------|---------|---------|------|
| ...  | ...     | ...     | ...  |
```

### Alert Report → Marked List
```
⚠️ 检测到 N 条异常数据:
1. [时间] [节点] [参数]: [值] — [异常原因]
2. ...
```

---

## Multi-Industry Adaptation

The skill auto-adapts based on device type. Do not assume a single industry context.

| Device Type Code | Industry | Typical Use Case | Key Parameters |
|-----------------|----------|-----------------|---------------|
| `Z` | Agriculture / 农业 | Soil monitoring / 土壤墒情监测 | moisture, temperature, ec |
| `T` | Meteorology / 气象 | Weather station / 气象站 | airTemperature, relativeHumidity, rainfall, wind... |
| `J` | Industry / 工业 | Liquid level monitoring / 液位监测 | laserliquidLevel, battery |

**Parameter Translation:** Use `/v3/device/{sn}/description` to translate raw parameter codes to Chinese names. Display "土壤温度" instead of "temperature" when device type is `Z`.

---

## Interaction Flow Examples

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
  → query_data(sn, time_expression="上周") → /data with range
  → Return: historical moisture data with trend analysis
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
  → Return: comparison table with difference highlighting
```

---

## Error Handling

| HTTP Status | Meaning | Skill Action |
|-------------|---------|-------------|
| 200 | Success | Process normally |
| 400 | Bad request | Check parameter format and retry |
| 401 | Unauthorized | Re-authenticate with appid/secret |
| 403 | Forbidden | Re-authenticate (token expired) |
| 404 | Not found | Device SN may be invalid; verify with user |
| 500 | Server error | Retry up to 3 times with exponential backoff |

**User-facing error messages:**
- 401 → "认证失败，请检查 appid 和 secret 是否正确"
- 404 → "未找到该设备，请确认设备序列号或别名"
- 500 (after retries) → "服务器暂时不可用，请稍后重试"

---

## Device Status Code Reference

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

## Parameter Quick Reference

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
