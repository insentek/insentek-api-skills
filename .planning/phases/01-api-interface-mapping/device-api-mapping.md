# Device API Mapping — /v3/devices, /v3/device/{sn}, /v3/device/{sn}/description

> Source: `ref/api-document-latest.pdf` §0x04, §0x05, §0x08, §0x17
> Locked Decisions: D-04, D-06

---

## 1. Endpoint Overview

| # | Endpoint | Method | Description | In Scope? |
|---|----------|--------|-------------|-----------|
| 1 | `/v3/devices` | GET | 设备列表查询（分页） | Yes |
| 2 | `/v3/device/{sn}` | GET | 单设备详情查询 | Yes |
| 3 | `/v3/device/{sn}/description` | GET | 设备参数说明（字段含义） | Yes |
| 4 | `/v3/device/{sn}/attr` | POST | 修改设备属性（名称、上报周期） | Optional |

---

## 2. GET /v3/devices — 设备列表

### 2.1 Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | Integer | Yes | 1 | 页码，从 1 开始 |
| `limit` | Integer | Yes | 20 | 每页数量 |

**Example Request:**
```
GET http://openapi.ecois.info/v3/devices?page=1&limit=20
```

### 2.2 Response Format

```json
{
  "message": "ok",
  "count": 1,
  "list": [
    {
      "sn": "00000000000000",
      "alias": "",
      "type": "",
      "series": "",
      "authorized": "own",
      "status": {
        "code": "Fault",
        "description": ""
      },
      "location": {
        "lng": 105.6846492425,
        "lat": 33.8720641309,
        "country": "",
        "province": "",
        "city": "",
        "district": ""
      },
      "widget": {
        "externalAccessUrl": "https://www.ecois.info/path/to"
      }
    }
  ]
}
```

### 2.3 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `count` | Integer | 总设备数 |
| `list` | Array | 设备列表 |
| `list[].sn` | String | 设备序列号（唯一标识） |
| `list[].alias` | String | 设备别名 |
| `list[].type` | String | 设备类型编码 |
| `list[].series` | String | 设备系列 |
| `list[].authorized` | String | 权限：`own`（自有）/ `shared`（共享） |
| `list[].status.code` | String | 状态码（见 §6 状态码表） |
| `list[].status.description` | String | 状态描述 |
| `list[].location.lng` | BigDecimal | 经度 |
| `list[].location.lat` | BigDecimal | 纬度 |
| `list[].location.country` | String | 国家 |
| `list[].location.province` | String | 省份 |
| `list[].location.city` | String | 城市 |
| `list[].location.district` | String | 区县 |
| `list[].widget.externalAccessUrl` | String | 设备外部访问 URL（iframe 嵌入用） |

### 2.4 Pagination Behavior
- `page` 从 1 开始计数
- `limit` 为每页返回的设备数量
- 总页数 = `ceil(count / limit)`
- 当 `list` 为空时表示已到达最后一页

---

## 3. GET /v3/device/{sn} — 单设备详情

### 3.1 Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sn` | String (path) | Yes | 设备序列号 |

**Example Request:**
```
GET http://openapi.ecois.info/v3/device/00000000000000
```

### 3.2 Response Format

```json
{
  "message": "ok",
  "sn": "00000000000000",
  "alias": "",
  "type": "",
  "series": "",
  "status": {
    "code": "Fault",
    "description": ""
  },
  "location": {
    "lng": 105.6846492425,
    "lat": 33.8720641309,
    "country": "",
    "province": "",
    "city": "",
    "district": ""
  },
  "authorized": "own",
  "authorizedUsers": [
    {
      "openid": "s9n3n9s1zns475a",
      "name": "",
      "headimg": "URL"
    }
  ],
  "feature": {
    "online": false,
    "rssi": -56,
    "network": "LTE"
  },
  "widget": {
    "externalAccessUrl": "https://www.ecois.info/path/to"
  }
}
```

### 3.3 Response Fields (相对于列表的增量字段)

| Field | Type | Description |
|-------|------|-------------|
| `authorizedUsers` | Array | 共享用户列表 |
| `authorizedUsers[].openid` | String | 用户 OpenID |
| `authorizedUsers[].name` | String | 用户昵称 |
| `authorizedUsers[].headimg` | String | 用户头像 URL |
| `feature` | Object | 设备特征信息（云衍/聆耘设备） |
| `feature.online` | Boolean | 在线状态 |
| `feature.rssi` | Integer | 信号强度 (dBm) |
| `feature.network` | String | 网络类型：`LTE`, `WiFi`, etc. |

**Note:** `feature` 字段仅在云衍/聆耘类型设备中存在。土壤墒情仪、气象站等设备无此字段。

---

## 4. GET /v3/device/{sn}/description — 设备参数说明

### 4.1 Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sn` | String (path) | Yes | 设备序列号 |

### 4.2 Response Format

```json
{
  "message": "ok",
  "nodes": ["", "10cm", "20cm", "30cm", "40cm"],
  "parameters": [
    {
      "moisture": {
        "name": "含水量",
        "unit": "%",
        "type": "numeric"
      },
      "temperature": {
        "name": "温度",
        "unit": "℃",
        "type": "numeric"
      }
    }
  ]
}
```

### 4.3 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `nodes` | Array<String> | 监测节点名称（如深度、位置） |
| `parameters` | Array<Object> | 参数定义列表，与 nodes 按索引对应 |
| `parameters[].{key}` | Object | 参数对象，key 为参数代码 |
| `parameters[].{key}.name` | String | 参数中文名称 |
| `parameters[].{key}.unit` | String | 单位 |
| `parameters[].{key}.type` | Enum | 数据类型：`text` / `numeric` / `binary` |

**Index Correspondence:** `nodes[i]` 对应 `parameters[i]`，表示第 i 个监测节点上的参数定义。

**Purpose for skill:** Agent 使用此接口理解数据字段含义，以便在回答用户时显示中文名称而非原始参数代码。

---

## 5. POST /v3/device/{sn}/attr — 修改设备属性（可选）

### 5.1 Request Body

```json
{
  "name": "新设备名称",
  "reportCycle": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | No | 设备新名称 |
| `reportCycle` | Integer | No | 数据上报周期（分钟） |

### 5.2 Valid reportCycle Values

`[5, 10, 20, 30, 60, 120]` — 单位：分钟

### 5.3 Response

```json
{ "message": "ok" }
```

**Note:** 此端点为写操作，在 skill 中标记为"可选 — 高级配置"。

---

## 6. Device Status Code Reference

| Status Code | Description | Applicable Device Types |
|-------------|-------------|------------------------|
| `Used` | 工作中 | 土壤墒情仪、气象站 |
| `Fault` | 故障中 | 土壤墒情仪、气象站 |
| `Online` | 在线 | 云衍、聆耘 |
| `Offline` | 离线 | 云衍、聆耘 |
| `Produce` | 生产中 | 通用 |
| `ToBeDelivered` | 待发货 | 通用 |
| `Repair` | 维修中 | 通用 |
| `Idle` | 未部署 | 通用 |
| `Scrap` | 已报废 | 通用 |

---

## 7. Parameter Name Reference by Device Type

### Z — 土壤监测设备

| Parameter Code | Chinese Name | Unit | Type |
|----------------|--------------|------|------|
| `temperature` | 土壤温度 | ℃ | numeric |
| `moisture` | 土壤水分/含水量 | % | numeric |
| `ec` | 电导率 | — | numeric |
| `battery` | 电池电压 | V | numeric |
| `outsideVoltage` | 外部电压 | V | numeric |

### T — 气象监测设备

| Parameter Code | Chinese Name | Unit | Type |
|----------------|--------------|------|------|
| `airTemperature` | 空气温度 | ℃ | numeric |
| `relativeHumidity` | 相对湿度 | % | numeric |
| `dewPoint` | 露点温度 | ℃ | numeric |
| `atmosphericPressure` | 大气压力 | hPa | numeric |
| `maxWindSpeed` | 最大风速 | m/s | numeric |
| `averageWindSpeed` | 平均风速 | m/s | numeric |
| `windDirection` | 风向 | ° | numeric |
| `rainfall` | 降雨量 | mm | numeric |
| `rainfallDuration` | 降雨持续时间 | s | numeric |
| `solarRadiationIntensity` | 太阳辐射强度 | W/m² | numeric |
| `solarRadiationAmount` | 太阳辐射量 | MJ/m² | numeric |
| `sunshineDuration` | 日照时长 | h | numeric |
| `pm1.0` | PM1.0 | μg/m³ | numeric |
| `pm2.5` | PM2.5 | μg/m³ | numeric |
| `pm10` | PM10 | μg/m³ | numeric |
| `tvoc` | 总挥发性有机物 | — | numeric |

### J — 见厘液位计

| Parameter Code | Chinese Name | Unit | Type |
|----------------|--------------|------|------|
| `laserliquidLevel` | 激光液位 | m | numeric |
| `battery` | 电池电压 | V | numeric |
| `outsideVoltage` | 外部电压 | V | numeric |

---

## 8. Skill Mapping (query_device)

### Skill Tool: `query_device`

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Query device information (list, detail, parameter meanings) |
| **Mapped Endpoints** | `/v3/devices` + `/v3/device/{sn}` + `/v3/device/{sn}/description` |
| **Parameters** | `page` (Integer, opt, default 1), `limit` (Integer, opt, default 20), `sn` (String, opt), `alias` (String, opt) |
| **Returns** | Device list or single device detail with parameter meanings |

### Agent Behavior Rules

1. **If `alias` provided:**
   - Call `/v3/devices` to find matching device
   - Use `alias` field matching (partial match supported)
   - Once `sn` resolved, call `/v3/device/{sn}` + `/v3/device/{sn}/description`

2. **If `sn` provided:**
   - Call `/v3/device/{sn}` + `/v3/device/{sn}/description`
   - Skip list query

3. **If neither provided:**
   - Call `/v3/devices` with page/limit
   - Return paginated device list

4. **Always enrich with description:**
   - When returning single device detail, also call `/v3/device/{sn}/description`
   - Use parameter names to translate raw codes to Chinese names

### Chain Pattern

`query_device` is often called before `query_data` to resolve `sn` from `alias`:
```
User: "查一下 3 号设备的温度"
  → query_device(alias="3号") → resolve sn="00000000000003"
  → query_data(sn="00000000000003", time_expression="现在")
```

---

*Referenced Decisions: D-04 (scene aggregation), D-06 (chain calling)*
*Requirements: DEV-01 (设备列表查询), DEV-02 (单设备信息查询)*
