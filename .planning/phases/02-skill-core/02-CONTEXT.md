# Phase 2: Skill 核心文件编写 - Context

**Gathered:** 2026-05-13
**Status:** Ready for planning

## Phase Boundary

基于 Phase 1 产出的 API 映射文档，编写完整的 `skill.md` 文件。该文件是终端用户在各 Agent 平台（OpenClaw、Hermes-Agent、Claude Code、ChatGPT）上直接对话使用 insentek API 的核心技能定义。

## Implementation Decisions

### skill.md 格式规范
- **D-13:** 采用 **Hybrid 设计**（YAML frontmatter + Function Schema + Prompt），兼容主流 Agent 平台
- **D-14:** YAML frontmatter 包含：名称、描述、版本、作者、API base URL
- **D-15:** Function Schema 区定义 3 个核心工具（`authenticate`, `query_device`, `query_data`）的 JSON Schema
- **D-16:** Prompt 区包含自然语言描述、时间推断规则、链式调用逻辑、输出格式要求

### 分析能力实现
- **D-17:** 趋势分析（ANALYSIS-01）通过 **Prompt 指令**实现，Agent 获取数据后自行计算平均值、最大值、最小值、变化率
- **D-18:** 跨设备对比（ANALYSIS-02）通过 **Prompt 指令**实现，Agent 并排比较相同指标并计算差异
- 不增加额外的 `analyze_trend` 或 `compare_devices` 工具

### 异常检测实现
- **D-19:** 异常数据检测（ALERT-01）通过 **Prompt 规则**实现，Agent 分析返回数据时自动标记异常
- 异常规则示例：moisture < 5% 或 > 50% 标记为异常；温度 1 小时内变化 > 10°C 标记为突变
- 不增加额外的 `check_alerts` 工具

### 输出格式规范
- **D-20:** 采用**智能格式模式**，根据查询类型自动选择输出格式：
  - 实时数据 → 简洁关键指标卡片
  - 历史数据 → Markdown 表格 + 趋势小结
  - 对比分析 → 并排表格 + 差异高亮
  - 异常报告 → 带标记的异常列表

### 多行业适配
- **D-21:** 通过**参数化上下文提示**实现多行业适配，不绑定单一行业
- skill.md 中包含行业参数说明（农业→土壤墒情、气象站；制造业→环境监测；能源→能耗监控）
- Agent 根据设备类型自动识别行业场景

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 1 产出（核心输入）
- `.planning/phases/01-api-interface-mapping/auth-mapping.md` — 认证 API 完整映射
- `.planning/phases/01-api-interface-mapping/device-api-mapping.md` — 设备 API 完整映射
- `.planning/phases/01-api-interface-mapping/data-api-mapping.md` — 数据查询 API 完整映射
- `.planning/phases/01-api-interface-mapping/api-skill-mapping.md` — 统一 API-to-Skill 映射

### 项目规划文档
- `.planning/phases/01-api-interface-mapping/01-CONTEXT.md` — Phase 1 决策（D-01 至 D-12）
- `.planning/PROJECT.md` — 项目定义和约束
- `.planning/REQUIREMENTS.md` — v1 需求清单
- `.planning/ROADMAP.md` — 路线图

## Specific Ideas

- **设备类型自动识别**: Z（土壤）、T（气象）、J（见厘）——Agent 根据设备参数自动识别行业场景
- **参数翻译**: 利用 `/v3/device/{sn}/description` 返回的中文名称，在输出中显示"土壤温度"而非 "temperature"
- **别名解析**: 用户说"3号设备"时，Agent 先用 query_device 解析别名到 sn，再查数据
- **缓存提示**: skill.md 中明确提示 Agent 缓存 token 和设备 sn 映射，避免重复查询

## Deferred Ideas

- 行业模板报告（农业/制造业/能源专属报告模板）— v2 需求，Phase 4+
- 数据预测能力 — v2 需求
- Pluviometer / Lingyun 专用 skill 工具 — Phase 2+ 扩展

---

*Phase: 2-Skill 核心文件编写*
*Context gathered: 2026-05-13*
