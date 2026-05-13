# Feature Research

**Domain:** Agent Skill for IoT Device Data API
**Researched:** 2026-05-13
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| 设备数据查询 | 用户最基本需求：查看设备当前/历史数据 | LOW | 单接口调用，返回结构化数据 |
| 设备列表浏览 | 用户需要知道有哪些设备可用 | LOW | 支持分页、筛选 |
| 认证引导 | API 需要认证，skill 必须引导用户完成 | LOW | 首次使用时的 onboarding |
| 自然语言理解 | 用户用中文/英文提问，skill 解析意图 | MEDIUM | 核心能力，决定用户体验 |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| 跨设备对比分析 | 同时查询多个设备，生成对比报告 | MEDIUM | 需要编排多个 API 调用 |
| 趋势预测 | 基于历史数据预测未来趋势 | HIGH | 需要数据分析和简单建模 |
| 异常检测与告警 | 自动识别数据异常并提醒用户 | MEDIUM | 规则引擎 + 阈值判断 |
| 行业模板报告 | 农业/制造业/能源等行业专属报告模板 | MEDIUM | 预置 prompt 模板 |
| 多语言输出 | 根据用户语言自动切换输出语言 | LOW | 利用 LLM 自身能力 |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| 实时流数据推送 | 用户想要"实时监控" | skill.md 无持久连接能力，无法实现真实时 | 轮询式"准实时"查询，或引导用户使用 WebSocket 原生客户端 |
| 复杂数据可视化 | 用户想要图表 | Markdown 内嵌图片能力有限，各平台支持不一 | 输出结构化数据（表格/JSON），由客户端渲染；或生成 Mermaid 图表 |
| 设备控制/下发指令 | 扩展 API 能力 | 超出当前 OpenAPI 范围，且涉及安全风险 | 明确告知只读查询能力，控制功能通过其他渠道 |

## Feature Dependencies

```
自然语言理解
    └──requires──> 设备列表浏览（知道查什么）
                       └──requires──> 认证引导（先能连上 API）

趋势预测 ──enhances──> 设备数据查询
行业模板报告 ──enhances──> 跨设备对比分析
```

## MVP Definition

### Launch With (v1)

- [ ] 认证引导与 API 连接 — 用户能成功配置 API 凭证
- [ ] 设备列表查询 — 用户能查看所有可用设备
- [ ] 单设备数据查询 — 用户能查询指定设备的数据
- [ ] 自然语言对话 — 用户能用中文提问获取数据

### Add After Validation (v1.x)

- [ ] 跨设备对比分析 — 当用户需要比较多个设备时
- [ ] 趋势分析 — 当用户需要看数据变化趋势时
- [ ] 异常检测 — 当数据量足够支撑异常识别时

### Future Consideration (v2+)

- [ ] 行业模板报告 — 需要积累行业-specific 的 prompt 模板
- [ ] 预测能力 — 需要更复杂的数据分析

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| 认证引导 | HIGH | LOW | P1 |
| 设备列表查询 | HIGH | LOW | P1 |
| 单设备数据查询 | HIGH | LOW | P1 |
| 自然语言对话 | HIGH | MEDIUM | P1 |
| 跨设备对比 | MEDIUM | MEDIUM | P2 |
| 趋势分析 | MEDIUM | MEDIUM | P2 |
| 异常检测 | MEDIUM | MEDIUM | P2 |
| 行业模板 | MEDIUM | MEDIUM | P2 |

---
*Feature research for: Agent Skill for IoT Device Data API*
*Researched: 2026-05-13*
