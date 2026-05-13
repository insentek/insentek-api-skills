# API Reference — 参数详细说明

> `skill.md` 的补充参考文档。面向需要深入理解 API 行为的技术用户。

---

## 目录

- [认证接口](#认证接口)
- [设备接口](#设备接口)
- [数据接口](#数据接口)
- [响应结构](#响应结构)
- [错误码](#错误码)
- [设备状态码](#设备状态码)
- [参数代码表](#参数代码表)

---

## 认证接口

### `GET /v3/token`

获取 API 访问 token。

**请求参数（Query）:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `appid` | string | 是 | 应用 ID |
| `secret` | string | 是 | 应用密钥 |

**成功响应:**

```json
{
  "message": "ok",
  "token": "wj3eZGGKofgv7GyzuCmuoLukVUvUsuDq",
  "expires": 7200
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `token` | string | 访问令牌，后续请求放在 `Authorization` header 中 |
| `expires` | integer | 有效期，单位秒（默认 7200 = 2 小时） |

**错误响应:**

| HTTP 状态 | 原因 | 处理建议 |
|-----------|------|---------|
| 400 | 请求格式错误 | 检查 appid/secret 是否为空 |
| 401 | 认证失败 | 确认 appid 和 secret 正确 |
| 500 | 服务器错误 | 重试，最多 3 次 |

---

## 设备接口

### `GET /v3/devices`

查询设备列表（分页）。

**请求参数（Query）:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 是 | 1 | 页码，从 1 开始 |
| `limit` | integer | 是 | 20 | 每页数量 |

**响应字段:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | integer | 总设备数 |
| `list[].sn` | string | 设备序列号 |
| `list[].alias` | string | 设备别名 |
| `list[].type` | string | 设备类型编码（Z/T/J） |
| `list[].series` | string | 设备系列 |
| `list[].authorized` | string | `own`（自有）/ `shared`（共享） |
| `list[].status.code` | string | 状态码 |
| `list[].status.description` | string | 状态描述 |
| `list[].location.lng` | number | 经度 |
| `list[].location.lat` | number | 纬度 |
| `list[].location.province` | string | 省份 |
| `list[].location.city` | string | 城市 |

---

### `GET /v3/device/{sn}`

查询单设备详情。

**路径参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sn` | string | 是 | 设备序列号 |

**增量字段（相对于列表）:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `authorizedUsers` | array | 共享用户列表 |
| `feature.online` | boolean | 在线状态（云衍/聆耘设备） |
| `feature.rssi` | integer | 信号强度 dBm |
| `feature.network` | string | 网络类型：`LTE`, `WiFi` |

---

### `GET /v3/device/{sn}/description`

查询设备参数说明（中文名称、单位）。

**响应结构:**

```json
{
  "message": "ok",
  "nodes": ["", "10cm", "20cm", "30cm", "40cm"],
  "parameters": [
    {
      "moisture": { "name": "含水量", "unit": "%", "type": "numeric" },
      "temperature": { "name": "温度", "unit": "℃", "type": "numeric" }
    }
  ]
}
```

**索引对应规则:** `nodes[i]` 对应 `parameters[i]`，表示第 i 个监测节点上的参数定义。

---

## 数据接口

### `GET /v3/device/{sn}/data`

历史数据查询。

**请求参数（Query）:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `sn` | string | 是 | — | 设备序列号（路径参数） |
| `range` | string | 否 | today | 时间范围 `YYYYMMDD,YYYYMMDD` |
| `includeParameters` | string | 否 | all | 指定参数，逗号分隔 |
| `includeNodes` | string | 否 | all | 指定节点，逗号分隔 |

---

### `GET /v3/device/{sn}/latest`

最新实时数据。

**路径参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sn` | string | 是 | 设备序列号 |

**响应增量字段:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `lng` | number | 经度 |
| `lat` | number | 纬度 |

---

### `GET /v3/device/{sn}/data/moment/{datetime}`

指定时刻数据。

**路径参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sn` | string | 是 | 设备序列号 |
| `datetime` | string | 是 | 时刻，需 URL 编码，格式 `YYYY-MM-DD HH:MM:SS` |

**示例:**
```
GET /v3/device/00000000000000/data/moment/2018-12-12%2009:32:22
```

---

### `GET /v3/device/{sn}/data/incremental`

增量数据同步。

**行为:**
- 首次调用：返回最近 3 个月数据
- 后续调用：返回自 `lastSync` 以来的增量数据

**响应字段:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `lastSync` | string | 上次同步时间 `YYYY-MM-DD HH:MM:SS` |
| `increments` | array | 增量数据点列表 |

---

## 响应结构

### 通用响应包装

所有 API 返回：

```json
{
  "message": "ok",
  "...": "endpoint-specific fields"
}
```

| message 值 | 含义 |
|-----------|------|
| `"ok"` | 成功 |
| `"error"` 或其他 | 错误，检查 HTTP 状态码 |

### 数据点结构

```json
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
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | integer | Unix 时间戳（秒） |
| `datetime` | string | 格式化时间 `YYYY-MM-DD HH:MM:SS` |
| `values` | object | 嵌套数据对象 |
| `values.{node}` | object | 节点/深度层 |
| `values.{node}.{parameter}` | number/string | 参数值 |

---

## 错误码

### HTTP 状态码

| 状态码 | 含义 | 适用方法 |
|--------|------|---------|
| 200 | 成功 | GET |
| 201 | 已创建 | POST / PUT / PATCH |
| 204 | 无内容 | DELETE |
| 400 | 请求格式错误 | POST / PUT / PATCH |
| 401 | 认证失败 | — |
| 403 | 禁止访问 | — |
| 404 | 资源不存在 | — |
| 406 | 不可接受 | GET |
| 410 | 资源已删除 | GET |
| 422 | 验证错误 | POST / PUT / PATCH |
| 500 | 服务器内部错误 | — |

### Skill 层错误处理

| 场景 | Agent 行为 |
|------|-----------|
| 401/403 | 自动重新认证（用缓存的 appid/secret） |
| 404 | 提示用户检查设备 SN 或别名 |
| 500 | 指数退避重试 3 次，然后报告失败 |

---

## 设备状态码

| 状态码 | 中文 | 适用设备 |
|--------|------|---------|
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

## 参数代码表

### Z — 土壤监测

| 代码 | 中文名 | 单位 | 类型 |
|------|--------|------|------|
| `temperature` | 土壤温度 | ℃ | numeric |
| `moisture` | 土壤水分/含水量 | % | numeric |
| `ec` | 电导率 | — | numeric |
| `battery` | 电池电压 | V | numeric |
| `outsideVoltage` | 外部电压 | V | numeric |

### T — 气象监测

| 代码 | 中文名 | 单位 | 类型 |
|------|--------|------|------|
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

| 代码 | 中文名 | 单位 | 类型 |
|------|--------|------|------|
| `laserliquidLevel` | 激光液位 | m | numeric |
| `battery` | 电池电压 | V | numeric |
| `outsideVoltage` | 外部电压 | V | numeric |

---

## 时间范围格式

| 格式 | 示例 | 说明 |
|------|------|------|
| `YYYYMMDD,YYYYMMDD` | `20250506,20250513` | 历史数据查询，两端包含 |
| `YYYY-MM-DD HH:MM:SS` | `2018-12-12 09:32:22` | 指定时刻，需 URL 编码 |

---

## 分页规则

- `page` 从 **1** 开始计数
- `limit` 为每页返回数量
- 总页数 = `ceil(count / limit)`
- `list` 为空时表示已到最后一页
