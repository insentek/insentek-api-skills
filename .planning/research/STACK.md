# Stack Research

**Domain:** Agent Skill Development (skill.md)
**Researched:** 2026-05-13
**Confidence:** HIGH

## Recommended Stack

### Core Format

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Markdown | CommonMark | skill 文件格式 | 所有 Agent 平台的通用语言，无渲染差异 |
| YAML Frontmatter | - | skill 元数据 | OpenClaw、Hermes-Agent 等平台的标准配置方式 |
| JSON Schema | Draft 7 | API 参数描述 | 结构化描述 API 参数，Agent 可解析 |

### Skill Specification Patterns

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| Function Calling Schema | 描述 API 调用签名 | Claude、ChatGPT 等支持 function calling 的平台 |
| Natural Language Prompt | 用自然语言描述能力 | 所有平台的兜底方案，兼容性最强 |
| Hybrid (Schema + Prompt) | 结构化 + 自然语言 | 推荐方案：schema 保证精确性，prompt 保证灵活性 |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Markdown Linter | 格式一致性 | 确保 skill.md 在不同平台渲染一致 |
| JSON Schema Validator | 参数描述校验 | 避免 API 参数描述错误导致调用失败 |
| Agent Sandbox |  skill 行为测试 | 在目标平台上验证 skill 行为 |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| HTML in skill.md | 部分 Agent 平台会过滤 HTML | 纯 Markdown + 表格 + 代码块 |
| Platform-specific 语法 | 绑定单一平台，丧失通用性 | 最小公共子集 Markdown |
| 过长的 system prompt | 超过 token 限制或稀释指令 | 结构化分节，核心指令前置 |
| 模糊的 API 描述 | Agent 无法正确构造请求 | JSON Schema + 示例请求/响应 |

## Version Compatibility

| Platform | Markdown Support | Function Calling | Schema Support | Notes |
|----------|------------------|------------------|----------------|-------|
| OpenClaw | Full | Yes | JSON Schema | 原生支持 skill.md |
| Hermes-Agent | Full | Yes | JSON Schema | 兼容 OpenClaw 格式 |
| Claude Code | Full | Yes | JSON Schema | 支持 Claude-specific 扩展 |
| ChatGPT | Full | Yes | JSON Schema | 通过 GPTs / Custom Instructions |

## Sources

- OpenClaw skill specification docs
- Hermes-Agent skill manifest reference
- Claude Code CLAUDE.md / skill integration guide
- OpenAI Function Calling documentation

---
*Stack research for: Agent Skill Development*
*Researched: 2026-05-13*
