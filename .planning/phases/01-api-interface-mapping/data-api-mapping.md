# Data Query API Mapping — /v3/device/{sn}/data, /latest, /moment/{datetime}, /incremental

> Source: `ref/api-document-latest.pdf` §0x07, §0x09, §0x10, §0x11
> Locked Decisions: D-04, D-05, D-07, D-08, D-09

---

## 1. Endpoint Overview

| # | Endpoint | Method | Description | In Scope? |
|---|----------|--------|-------------|-----------|
| 1 | `/v3/device/{sn}/data` | GET | 历史数据查询（时间范围） | Yes |
| 2 | `/v3/device/{sn}/latest` | GET | 最新实时数据 | Yes |
| 3 | `/v3/device/{sn}/data/moment/{datetime}` | GET | 指定时刻数据 | Yes |
| 4 | `/v3/device/{sn}/data/incremental` | GET | 增量数据同步 | Yes |

---

## 2. GET /v3/device/{sn}/data — 历史数据

### 2.1 Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sn` | String (path) | Yes | — | 设备序列号 |
| `range` | String | No | today | 时间范围，格式 `YYYYMMDD,YYYYMMDD` |
| `includeParameters` | String | No | all | 指定返回的参数，逗号分隔（如 `moisture,temperature`） |
| `includeNodes` | String | No | all | 指定返回的节点，逗号分隔 |

**Example Request:**
```
GET http://openapi.ecois.info/v3/device/00000000000000/data?range=20180102,20181112&includeParameters=moisture,temperature
```

### 2.2 Response Format

```json
{
  "message": "ok",
  "total": 1,
  "list": [
    {
      "timestamp": 1541169181,
      "datetime": "2018-11-02 22:33:01",
      "values": {
        "10cm": {
          "moisture": 12.3,
          "temperature": 10.7
        },
        "20cm": {
          "moisture": 12.3,
          "temperature": 9.9
        },
        "30cm": {
          "moisture": 12.3,
          "temperature": 9.8
        },
        "40cm": {
          "moisture": 12.3,
          "temperature": 8.5
        }
      }
    }
  ]
}
```

### 2.3 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total` | Integer | 数据点总数 |
| `list` | Array | 数据点列表 |
| `list[].timestamp` | Timestamp | Unix 时间戳（秒） |
| `list[].datetime` | DateTime | 格式化时间 `YYYY-MM-DD HH:MM:SS` |
| `list[].values` | Object | 嵌套数据对象 |

### 2.4 Values Structure (Nested Object)

```
values: {
  "{node_name}": {           // 节点名称（如 "10cm", "20cm", "地表"）
    "{parameter}": {value},  // 参数名称（如 moisture, temperature）
    ...
  },
  ...
}
```

- **Top level keys**: 节点名称（来自 `/v3/device/{sn}/description` 的 `nodes` 数组）
- **Second level keys**: 参数名称（来自 `/v3/device/{sn}/description` 的 `parameters` 对象）
- **Values**: 数值（Float）或文本（String）

---

## 3. GET /v3/device/{sn}/latest — 最新实时数据

### 3.1 Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sn` | String (path) | Yes | 设备序列号 |

**Example Request:**
```
GET http://openapi.ecois.info/v3/device/00000000000000/latest
```

### 3.2 Response Format

```json
{
  "message": "ok",
  "timestamp": 1541169181,
  "datetime": "2018-11-02 22:33:01",
  "lng": 105.6846492425,
  "lat": 33.8720641309,
  "values": {
    "10cm": {
      "moisture": 12.3,
      "temperature": 8.2
    },
    "20cm": {
      "moisture": 12.3,
      "temperature": 7.6
    },
    "30cm": {
      "moisture": 12.3,
      "temperature": 7.6
    },
    "40cm": {
      "moisture": 12.3,
      "temperature": 7.5
    }
  }
}
```

### 3.3 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | Timestamp | Unix 时间戳 |
| `datetime` | DateTime | 格式化时间 |
| `lng` | BigDecimal | 经度 |
| `lat` | BigDecimal | 纬度 |
| `values` | Object | 同 `/data` 的嵌套结构 |

**Use case:** "现在/最新/当前/实时" queries → this endpoint

---

## 4. GET /v3/device/{sn}/data/moment/{datetime} — 指定时刻数据

### 4.1 Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sn` | String (path) | Yes | 设备序列号 |
| `datetime` | DateTime (path) | Yes | 指定时刻，URL-encoded |

**Example Request:**
```
GET http://openapi.ecois.info/v3/device/00000000000000/moment/2018-12-12%2009:32:22
```

### 4.2 Response Format

```json
{
  "message": "ok",
  "timestamp": 1541169181,
  "datetime": "2018-11-02 22:33:01",
  "values": {
    "10cm": {
      "moisture": 12.3,
      "temperature": 8.2
    },
    "20cm": {
      "moisture": 12.3,
      "temperature": 7.6
    }
  }
}
```

**Use case:** "某时刻/某个时间点/12月12日9点32分" queries → this endpoint

---

## 5. GET /v3/device/{sn}/data/incremental — 增量数据

### 5.1 Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sn` | String (path) | Yes | 设备序列号 |

**Example Request:**
```
GET http://openapi.ecois.info/v3/device/00000000000000/data/incremental
```

### 5.2 Response Format

```json
{
  "message": "ok",
  "lastSync": "2018-11-12 12:33:12",
  "increments": [
    {
      "timestamp": 1541169181,
      "datetime": "2018-11-02 22:33:01",
      "values": {
        "10cm": {
          "moisture": 12.3,
          "temperature": 8.2
        }
      }
    }
  ]
}
```

### 5.3 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `lastSync` | DateTime | 上次同步时间 |
| `increments` | Array | 增量数据点列表 |
| `increments[].timestamp` | Timestamp | Unix 时间戳 |
| `increments[].datetime` | DateTime | 格式化时间 |
| `increments[].values` | Object | 同 `/data` 的嵌套结构 |

### 5.4 Behavior

- **First call**: Returns data from last 3 months
- **Subsequent calls**: Returns data since `lastSync`
- Use `lastSync` from response to track sync state

**Use case:** "同步/增量/更新" queries → this endpoint

---

## 6. Data Response Structure Deep Dive

### 6.1 Nested Values Object

All 4 data endpoints return the same nested `values` structure:

```
values: {
  "{node_name}": {              // 节点/深度（如 "10cm", "20cm", "地表"）
    "{parameter_code}": value,  // 参数代码（如 moisture, temperature）
    ...
  },
  ...
}
```

### 6.2 Cross-Reference with Description

Use `/v3/device/{sn}/description` to translate parameter codes:

| Parameter Code | Name | Unit | Device Type |
|----------------|------|------|-------------|
| `moisture` | 含水量 | % | Z |
| `temperature` | 温度 | ℃ | Z/T |
| `ec` | 电导率 | — | Z |
| `battery` | 电池电压 | V | Z/J |
| `outsideVoltage` | 外部电压 | V | Z/J |
| `airTemperature` | 空气温度 | ℃ | T |
| `relativeHumidity` | 相对湿度 | % | T |
| `rainfall` | 降雨量 | mm | T |
| `laserliquidLevel` | 激光液位 | m | J |

### 6.3 见厘 (J) Device Example

```json
{
  "total": 132,
  "list": [
    {
      "timestamp": 1651939200,
      "datetime": "2022-05-08 00:00:00",
      "values": {
        "": {
          "laserliquidLevel": 117.0,
          "battery": 3.288,
          "outsideVoltage": 4.845
        }
      }
    }
  ]
}
```

Note: J-type devices have a single empty-string node `""` with liquid level, battery, and voltage parameters.

---

## 7. Time Expression Mapping

### 7.1 Natural Language → API Endpoint + Range

| User Says | Inferred Type | API Endpoint | Range Calculation |
|-----------|---------------|--------------|-------------------|
| "现在" / "最新" / "当前" / "实时" | realtime | `/latest` | — |
| "昨天" | history | `/data` | yesterday 00:00 ~ yesterday 23:59 |
| "最近7天" / "近一周" | history | `/data` | today-7d ~ today |
| "上周" | history | `/data` | last Monday ~ last Sunday |
| "本周" | history | `/data` | this Monday ~ today |
| "本月" | history | `/data` | 1st of month ~ today |
| "上月" | history | `/data` | 1st of last month ~ last day of last month |
| "今年" | history | `/data` | Jan 1 ~ today |
| "某个时间点" / "某时刻" | moment | `/moment/{datetime}` | URL-encoded datetime |
| "同步" / "增量" / "更新" | incremental | `/incremental` | — |
| *(no time clue)* | history (default) | `/data` | last 24h |

### 7.2 Date Calculation Rules

Agent must convert natural language to `YYYYMMDD,YYYYMMDD` format:

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

### 7.3 Range Parameter Format

- Format: `YYYYMMDD,YYYYMMDD` (no separators)
- Example: `range=20250506,20250513`
- Both dates are inclusive

---

## 8. Skill Mapping (query_data)

### Skill Tool: `query_data`

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Query device data (historical, real-time, moment, incremental) |
| **Mapped Endpoints** | `/data` + `/latest` + `/moment/{datetime}` + `/incremental` |
| **Parameters** | `sn` (String, req), `time_expression` (String, opt), `range` (String, opt), `includeParameters` (String, opt) |
| **Returns** | Data points with timestamp, datetime, and nested values |

### Auto-Inference Rules (per D-05, D-07, D-08)

Agent analyzes user's natural language time clues:

```
IF "现在/最新/当前/实时" in query → call /latest
ELIF "某时刻/某个时间点" in query → call /moment/{datetime}
ELIF "同步/增量/更新" in query → call /incremental
ELSE → call /data with calculated range
```

### Default Behavior (per D-08)

When user provides no time clue:
- Call `/data` with default range = last 24 hours
- `range = {(today-1d)YYYYMMDD},{(today)YYYYMMDD}`

### Parameter Filtering

When user asks for specific metrics:
- Extract parameter names from query
- Map to parameter codes using `/v3/device/{sn}/description`
- Pass to `includeParameters` to limit response size

Example: "查一下土壤湿度" → `includeParameters=moisture`

### Chain Pattern (per D-06)

`query_data` requires `sn`. If user provides alias:
```
User: "3号设备的温度"
  → query_device(alias="3号") → sn="00000000000003"
  → query_data(sn="00000000000003", time_expression="现在")
```

---

*Referenced Decisions: D-04 (scene aggregation), D-05 (auto-inference), D-07 (natural language time parsing), D-08 (default last 24h), D-09 (range format)*
*Requirements: DATA-01 (实时数据查询), DATA-02 (历史数据查询)*
