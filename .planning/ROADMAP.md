# Roadmap

**Project:** insentek-api-skills
**Mode:** standard
**Structure:** Horizontal Layers
**Created:** 2026-05-13

---

## Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | API 接口梳理与映射 | 全面理解并映射 insentek OpenAPI 能力 | AUTH-01, AUTH-02, DEV-01, DEV-02, DATA-01, DATA-02 | 4 |
| 2 | Skill 核心文件编写 | 产出完整的 skill.md 技能文件 | SKILL-01, SKILL-02, SKILL-03, ANALYSIS-01, ANALYSIS-02, ALERT-01 | 4 |
| 3 | 配套文档编写 | 编写使用文档和平台适配指南 | DOC-01, DOC-02 | 3 |
| 4 | 示例与输出格式 | 提供对话示例和输出模板 | EXAMPLE-01, EXAMPLE-02 | 3 |
| 5 | 跨平台测试与适配 | 验证多平台兼容性并修复问题 | PLATFORM-01, PLATFORM-02 | 3 |

**Total:** 5 phases | 15 requirements mapped | 100% v1 coverage

---

### Phase 1: API 接口梳理与映射

**Goal:** 全面阅读并理解 `ref/api-document-latest.pdf` 和 `ref/api-repo/`，梳理所有可用 API endpoint，建立从 API 到 skill 功能的完整映射。

**Requirements:**
- AUTH-01: API 认证引导说明
- AUTH-02: 认证错误处理
- DEV-01: 设备列表查询能力
- DEV-02: 单设备信息查询能力
- DATA-01: 设备实时数据查询能力
- DATA-02: 设备历史数据查询能力

**Success Criteria:**
1. 所有 API endpoint（DeviceData、DeviceInfo、DeviceParam、EcoApiAuth）均已梳理并记录
2. 每个 API 的参数、响应格式、错误码已整理成结构化文档
3. API 到 skill 功能的映射表已完成
4. 认证流程（获取密钥、配置方式）已完全理解并能向用户说明

---

### Phase 2: Skill 核心文件编写

**Goal:** 基于 Phase 1 的 API 映射，编写完整的 `skill.md` 文件，包含所有功能定义、工具描述和交互模式。

**Requirements:**
- SKILL-01: 通用 skill.md 涵盖所有 API
- SKILL-02: Hybrid 设计（Schema + Prompt），兼容多平台
- SKILL-03: 多行业场景适配
- ANALYSIS-01: 数据趋势分析能力
- ANALYSIS-02: 跨设备对比分析能力
- ALERT-01: 异常数据检测能力

**Success Criteria:**
1. skill.md 包含完整的 YAML frontmatter（名称、描述、版本）
2. 所有 API 能力以 function schema 或自然语言描述形式定义
3. 包含清晰的 interaction patterns（用户如何提问、skill 如何响应）
4. 输出格式规范已定义（表格、总结、报告模板）
5. 多行业适配提示已嵌入（通过参数化或上下文提示）

---

### Phase 3: 配套文档编写

**Goal:** 编写帮助用户上手和使用 skill 的配套文档。

**Requirements:**
- DOC-01: 使用文档（参数说明、调用方式）
- DOC-02: 各 Agent 平台适配指南

**Success Criteria:**
1. `docs/getting-started.md` 完成：新用户 5 分钟内可完成配置并开始使用
2. `docs/platform-setup.md` 完成：覆盖 OpenClaw、Claude Code、ChatGPT 的配置步骤
3. `docs/api-reference.md` 完成：API 参数详细说明，作为 skill.md 的补充参考
4. 文档经过走查，非技术人员能理解

---

### Phase 4: 示例与输出格式

**Goal:** 提供丰富的对话示例和输出格式模板，降低用户学习成本。

**Requirements:**
- EXAMPLE-01: 5+ 组对话示例（查询、报告、分析）
- EXAMPLE-02: 输出格式示例（表格、总结、报告）

**Success Criteria:**
1. `examples/queries.md` 包含 3+ 组查询类对话示例
2. `examples/reports.md` 包含 2+ 组报告生成示例
3. `examples/alerts.md` 包含 2+ 组异常分析示例
4. 每组示例包含：用户输入 → skill 思考过程 → 工具调用 → 格式化输出
5. 输出示例覆盖表格、文字总结、结构化报告三种形式

---

### Phase 5: 跨平台测试与适配

**Goal:** 在目标 Agent 平台上验证 skill 行为，修复兼容性问题。

**Requirements:**
- PLATFORM-01: OpenClaw + Claude Code 双平台验证
- PLATFORM-02: ChatGPT 验证

**Success Criteria:**
1. skill.md 在 OpenClaw 上能被正确识别和加载
2. 在 Claude Code 上 function calling 正常工作
3. 在 ChatGPT（Custom Instructions / GPTs）上能正确响应
4. 跨平台输出格式一致（表格、代码块正确渲染）
5. 发现的所有兼容性问题已修复并记录

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | 1 | — |
| AUTH-02 | 1 | — |
| DEV-01 | 1 | — |
| DEV-02 | 1 | — |
| DATA-01 | 1 | — |
| DATA-02 | 1 | — |
| SKILL-01 | 2 | — |
| SKILL-02 | 2 | — |
| SKILL-03 | 2 | — |
| ANALYSIS-01 | 2 | — |
| ANALYSIS-02 | 2 | — |
| ALERT-01 | 2 | — |
| DOC-01 | 3 | — |
| DOC-02 | 3 | — |
| EXAMPLE-01 | 4 | — |
| EXAMPLE-02 | 4 | — |
| PLATFORM-01 | 5 | — |
| PLATFORM-02 | 5 | — |

---

*Roadmap created: 2026-05-13*
*Next: Run `/gsd-discuss-phase 1` to start execution*
