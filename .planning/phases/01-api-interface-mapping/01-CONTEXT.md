# Phase 1: API 接口梳理与映射 - Context

**Gathered:** 2026-05-13
**Status:** Ready for planning

## Phase Boundary

全面阅读并理解 `ref/api-document-latest.pdf` 和 `ref/api-repo/`，梳理所有可用 API endpoint，建立从 API 到 skill 功能的完整映射。产出结构化的 API 映射文档，为 Phase 2 的 skill.md 编写提供完整输入。

## Implementation Decisions

### API 覆盖范围
- **D-01:** 仅纳入 10 个通用端点，覆盖认证、设备查询、数据查询的核心能力
- **D-02:** Webhook 配置端点 (`/v3/device/webhook`) 纳入为**可选工具**，在 skill.md 中标注为高级配置功能
- **D-03:** 以下 4 个专用端点**暂不纳入**通用 skill，作为 Deferred Ideas 留待后续：
  - `/v3/device/pluviometer/{sn}/data/stats`
  - `/v3/device/pluviometer/{sn}/data/history`
  - `/v3/device/pluviometer/{sn}/data/latest`
  - `/v3/device/lingyun/{sn}/service`

### 功能映射粒度
- **D-04:** 采用**场景聚合**设计，将 10 个通用端点聚合为 2 个核心工具：
  - `query_device`: 聚合 `/v3/devices` + `/v3/device/{sn}` + `/v3/device/{sn}/attr`
  - `query_data`: 聚合 `/v3/device/{sn}/data` + `/v3/device/{sn}/latest` + `/v3/device/{sn}/data/moment/{datetime}` + `/v3/device/{sn}/data/incremental`
- **D-05:** Agent **自动推断**数据查询类型：从用户自然语言中的时间线索判断调用哪个底层 API（"现在/最新"→latest，"昨天/上周"→data，"某个时间点"→moment）
- **D-06:** 采用**链式调用**模式：`query_device` 先定位设备（解析 sn/alias），再调用 `query_data` 查询数据，各司其职

### 时间范围表达
- **D-07:** 支持**自然语言解析**，skill.md 提示词中定义相对时间解析规则（"最近N天"、"本周"、"昨天"等→自动计算日期范围）
- **D-08:** 用户未指定时间范围时，**默认查询最近 24 小时**数据
- **D-09:** API 的 `range` 参数格式为 `YYYYMMDD,YYYYMMDD`，Agent 负责将解析后的日期转换为该格式

### 认证处理
- **D-10:** 采用**完整认证流程**：skill.md 定义 `authenticate` 工具，支持通过 `appid` + `secret` 获取 token
- **D-11:** skill.md 提示词中包含 **token 过期检测**和**自动刷新**逻辑
- **D-12:** **对话级 token 复用**：对话开始时获取一次 token 并缓存到上下文，所有后续 API 调用复用，返回 401/403 时自动刷新

### Claude's Discretion
- 无 — 所有关键决策均已明确

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### API 文档与源码
- `ref/api-document-latest.pdf` — 完整的 API 接口文档（含所有端点定义、参数、响应格式、错误码）
- `ref/api-repo/src/main/java/com/insentek/openapi/` — OpenAPI 工程源码（Spring Boot 3.5.4 + Java 21 + MyBatis-Plus）
- `ref/api-repo/src/main/java/com/insentek/openapi/common/model/R.java` — 通用返回结果模型
- `ref/api-repo/src/main/java/com/insentek/openapi/model/EcoApiAuth.java` — 认证模型（appid/appsecret/token/expires）

### 项目规划文档
- `.planning/PROJECT.md` — 项目定义、核心价值和范围约束
- `.planning/REQUIREMENTS.md` — v1 需求清单（AUTH/DEV/DATA/ANALYSIS/ALERT/SKILL/DOC/EXAMPLE/PLATFORM）
- `.planning/ROADMAP.md` — 5 阶段路线图和 Success Criteria
- `.planning/STATE.md` — 当前项目状态

## Existing Code Insights

### API 端点梳理（已确认）
| # | 端点 | 方法 | 说明 | Skill 映射 |
|---|------|------|------|-----------|
| 1 | `/v3/token` | GET | appid+secret → token+expires(7200s) | `authenticate` |
| 2 | `/v3/devices` | GET | 设备列表，参数 page/limit | `query_device` |
| 3 | `/v3/device/{sn}` | GET | 单设备详情 | `query_device` |
| 4 | `/v3/device/{sn}/attr` | GET | 设备属性 | `query_device` |
| 5 | `/v3/device/{sn}/data` | GET | 历史数据，参数 range/includeParameters | `query_data` |
| 6 | `/v3/device/{sn}/description` | GET | 设备参数说明 | `query_device` |
| 7 | `/v3/device/{sn}/data/incremental` | GET | 增量数据 | `query_data` |
| 8 | `/v3/device/{sn}/latest` | GET | 最新实时数据 | `query_data` |
| 9 | `/v3/device/{sn}/data/moment/{datetime}` | GET | 指定时刻数据 | `query_data` |
| 10 | `/v3/device/webhook` | GET | Webhook 配置 | `config_webhook`（可选） |

### 关键数据模型
- **设备状态码**: `Fault`, `Online`, `Offline`, `Produce`, `ToBeDelivered`, `Repair`, `Idle`, `Scrap`
- **认证返回**: `{message, token, expires}` — expires 单位为秒（7200）
- **设备列表返回**: `{count, list[]}` — list 包含 sn/alias/type/series/location/status/widget
- **数据查询返回**: `{total, list[]}` — list 包含 timestamp/datetime/values（嵌套对象，键为深度如 "10cm"）

## Specific Ideas

- **参数说明**: `/v3/device/{sn}/description` 返回字段含义（如 moisture=土壤湿度，temperature=温度），应在 skill.md 中利用此能力帮助 Agent 理解数据含义
- **设备定位**: 用户可能用 alias（别名）而非 sn（序列号）指代设备，skill.md 应提示 Agent 优先用 `query_device` 解析别名到 sn

## Deferred Ideas

### Phase 2+ 扩展端点
- 雨量计专用端点（`/v3/device/pluviometer/{sn}/data/*` ×3）— 当前为通用 skill，专用设备能力待扩展
- 灵云服务调用（`/v3/device/lingyun/{sn}/service`）— 属于生态扩展能力，非核心数据查询

### Phase 4+ 扩展
- 行业模板报告（农业/制造业/能源专属报告模板）— v2 需求
- 数据预测能力（基于历史数据的趋势预测）— v2 需求

---

*Phase: 1-API 接口梳理与映射*
*Context gathered: 2026-05-13*
