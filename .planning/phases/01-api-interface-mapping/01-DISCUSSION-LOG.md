# Phase 1: API 接口梳理与映射 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-13
**Phase:** 1-API 接口梳理与映射
**Areas discussed:** API 覆盖范围, 功能映射粒度, 时间范围表达, 认证处理

---

## API 覆盖范围 — 专用端点是否纳入

| Option | Description | Selected |
|--------|-------------|----------|
| 纳入所有端点 | skill 包含全部 14 个端点，覆盖最完整 | |
| 仅纳入通用端点（推荐） | 只保留 10 个通用端点，专用端点留待后续扩展 | ✓ |
| 条件纳入 | 主结构含通用端点，扩展功能以提示词形式提供 | |

**User's choice:** 仅纳入通用端点（推荐）
**Notes:** 专用端点（pluviometer ×3、lingyun）暂不纳入，保持 skill 简洁通用。

### 后续问题: webhook 配置端点

| Option | Description | Selected |
|--------|-------------|----------|
| 纳入，作为可选工具 | skill.md 包含 webhook 配置工具 | ✓ |
| 不纳入，仅在使用文档中提及 | 不定义 webhook 工具，仅在参考文档中说明 | |
| You decide | 由 Claude 判断 | |

**User's choice:** 纳入，作为可选工具
**Notes:** Webhook 作为可选的高级配置工具，不纳入核心查询流程。

---

## 功能映射粒度 — 1:1 工具 vs 场景聚合

| Option | Description | Selected |
|--------|-------------|----------|
| 1:1 精确映射 | 每个 API 一个独立工具，调用零歧义 | |
| 场景聚合（推荐） | 按用户意图聚合为 query_device + query_data | ✓ |
| 混合策略 | 高频聚合，低频/配置类保持独立 | |

**User's choice:** 场景聚合（推荐）
**Notes:** 核心决策：query_device（列表/详情/属性）+ query_data（历史/实时/指定时刻/增量）。

### 后续问题 1: query_data 如何区分实时 vs 历史查询？

| Option | Description | Selected |
|--------|-------------|----------|
| Agent 自动推断（推荐） | skill.md 提示词含时间线索规则，Agent 自动判断 | ✓ |
| query_data 必填 query_type 参数 | Agent 必须判断并填入查询类型 | |
| 同时调用多个 API 综合返回 | 同时调用 latest + data，统一输出 | |

**User's choice:** Agent 自动推断（推荐）
**Notes:** 提示词规则："现在/最新"→latest，"昨天/上周"→data，"某个时间点"→moment。

### 后续问题 2: 多意图语句走哪个聚合工具？

| Option | Description | Selected |
|--------|-------------|----------|
| 统一走 query_data | query_data 同时接受 device_identifier | |
| query_device → query_data 链式调用 | Agent 先定位设备再查数据 | ✓ |
| 由你根据设计简洁性判断 | Claude 自行决定 | |

**User's choice:** query_device → query_data 链式调用
**Notes:** 两个工具各司其职，query_device 负责设备定位，query_data 负责数据查询。

---

## 时间范围表达 — 自然语言解析 vs 固定格式

| Option | Description | Selected |
|--------|-------------|----------|
| 自然语言解析（推荐） | skill.md 定义相对时间解析规则，Agent 自动计算 | ✓ |
| 自然语言为主 + 格式兜底 | 优先自然语言，给出标准格式示例 | |
| 仅固定格式 | 要求用户用 YYYY-MM-DD 到 YYYY-MM-DD 格式 | |

**User's choice:** 自然语言解析（推荐）
**Notes:** 用户完全用自然语言交互，Agent 内部做日期计算。

### 后续问题: 用户未指定时间范围时的默认行为？

| Option | Description | Selected |
|--------|-------------|----------|
| 最近 24 小时（推荐） | 默认查询最近24小时，平衡数据量和实用性 | ✓ |
| 最近 7 天 | 适合周趋势分析，但数据量可能较大 | |
| 必须追问 | Agent 主动追问用户时间段 | |

**User's choice:** 最近 24 小时（推荐）
**Notes:** 默认最近24小时，适合大多数实时分析场景。

---

## 认证处理 — 仅配置引导 vs 含 token 刷新

| Option | Description | Selected |
|--------|-------------|----------|
| 完整认证流程（推荐） | skill.md 定义 authenticate 工具 + 自动刷新 | ✓ |
| 仅配置引导 | 只在前置说明中告诉用户如何获取 token | |
| 混合策略 | 包含 authenticate 工具，但刷新需用户手动触发 | |

**User's choice:** 完整认证流程（推荐）
**Notes:** 用户只需配置 appid/secret，后续 token 管理完全自动。

### 后续问题: token 在对话期间的管理策略？

| Option | Description | Selected |
|--------|-------------|----------|
| 对话级复用（推荐） | 对话开始时获取一次 token，缓存复用，过期自动刷新 | ✓ |
| 每次调用前检查 | 每次调用前检查过期时间，过期则刷新 | |
| 无状态模式 | 不缓存 token，每次需要时重新获取 | |

**User's choice:** 对话级复用（推荐）
**Notes:** 减少 token 请求次数，提升响应速度。

---

## Claude's Discretion

无 — 所有关键决策均由用户明确选择。

## Deferred Ideas

- 雨量计专用端点（`/v3/device/pluviometer/{sn}/data/*` ×3）— 当前暂不纳入，未来可考虑作为扩展包
- 灵云服务调用（`/v3/device/lingyun/{sn}/service`）— 生态扩展能力，非核心数据查询
