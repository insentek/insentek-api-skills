# insentek-api-skills

## What This Is

基于 insentek OpenAPI 工程仓库和接口文档，产出一份通用 `skill.md` 技能文件及配套文档与示例。终端用户（非技术人员）可在 OpenClaw、Hermes-Agent、Claude Code、ChatGPT 等 Agent 平台上直接对话使用，通过自然语言调用 insentek API 完成设备数据查询、报告生成与实时分析，适配多行业场景。

## Core Value

让终端用户用自然语言轻松查询设备数据 —— 如果只做对一件事，那就是这件事。

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 产出一个通用 `skill.md` 文件，涵盖 insentek OpenAPI 所有可用接口和典型使用场景
- [ ] skill.md 支持终端用户通过自然语言完成：设备数据对话式查询、报告生成、实时分析
- [ ] skill.md 适配多行业场景（农业、制造业、能源等），不绑定单一行业
- [ ] 编写配套使用文档（参数说明、调用方式、平台适配指南）
- [ ] 提供对话示例与输出示例，降低用户上手门槛
- [ ] skill.md 兼容主流 Agent 平台（OpenClaw、Hermes-Agent、Claude Code、ChatGPT 等）

### Out of Scope

- 不开发 skill 生成工具或自动化平台 —— 本项目是内容产出，非工具开发
- 不按行业拆分多个 skill 文件 —— 坚持一个通用 skill 覆盖所有场景
- 不修改或扩展底层 insentek API 功能 —— 仅基于现有 API 能力包装
- 不输出 SDK、API 服务或其他非 skill.md 形式的交付物

## Context

- **参考源**：`ref/api-repo/`（Spring Boot 3.5.4 + Java 21 + MyBatis-Plus OpenAPI 工程）、`ref/api-document-latest.pdf`（接口文档）
- **API 覆盖范围**：设备数据（DeviceData）、设备信息（DeviceInfo）、设备参数（DeviceParam）、生态 API 认证（EcoApiAuth）
- **目标平台生态**：OpenClaw、Hermes-Agent、Claude Code、OpenAI ChatGPT 等支持 skill.md 的 Agent 平台
- **用户画像**：非技术人员，需要通过自然语言与设备数据交互

## Constraints

- **Timeline**：1-2 周内交付完整版
- **Tech Stack**：基于现有 API 能力，不引入新的后端技术栈
- **Format**：交付物为 Markdown 格式的 skill.md 及配套文档
- **Platform**：需兼容多种 Agent 平台的 skill 解析规范

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 一个通用 skill.md 而非多文件拆分 | 降低用户选择成本，终端用户无需理解技能边界 | — Pending |
| 内容产出而非工具开发 | 当前需求是快速产出可用技能，工具化是后续可能的演进方向 | — Pending |
| 适配多行业而非行业定制 | 最大化 skill 的复用范围，通过参数化实现行业切换 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-13 after initialization*
