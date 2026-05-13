# Research Summary

**Project:** insentek-api-skills
**Researched:** 2026-05-13
**Domain:** Agent Skill Development for IoT Device Data API

## Key Findings

### Stack

- **Format:** Markdown + YAML Frontmatter + JSON Schema (hybrid approach)
- **Platform Strategy:** 最小公共子集，确保 OpenClaw / Hermes-Agent / Claude Code / ChatGPT 全兼容
- **Anti-pattern:** 避免 HTML、平台-specific 语法、过长 system prompt

### Table Stakes

1. 设备数据查询（核心）
2. 设备列表浏览
3. 认证引导
4. 自然语言理解

### Differentiators

1. 跨设备对比分析
2. 趋势分析
3. 异常检测
4. 行业模板报告

### Architecture Recommendation

- **Pattern:** Hybrid (Function Schema + Natural Language Prompt)
- **Structure:** skill.md 单文件 + docs/ 配套文档 + examples/ 对话示例
- **Data Flow:** User Query → Intent Recognition → Parameter Extraction → API Call → Data Transformation → Human-Readable Response

### Watch Out For

1. **API 描述不一致** — 必须严格对照 `ref/` 源码和文档
2. **Tool 过度拆分** — 按功能聚合，避免 Agent 选择困难
3. **平台兼容性** — 至少双平台验证（OpenClaw + Claude Code）
4. **输出不友好** — 始终转换原始数据为表格/总结

## Research Files

| File | Content |
|------|---------|
| STACK.md | Agent 平台规范、skill 格式标准 |
| FEATURES.md | 功能优先级、MVP 定义、反功能 |
| ARCHITECTURE.md | skill.md 结构、设计模式、数据流 |
| PITFALLS.md | 常见陷阱、预防措施、验证清单 |

---
*Research summary for: insentek-api-skills*
*Researched: 2026-05-13*
