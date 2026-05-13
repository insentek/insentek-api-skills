# Requirements

**Project:** insentek-api-skills
**Version:** v1.0
**Defined:** 2026-05-13

## v1 Requirements

### Authentication (AUTH)

- [ ] **AUTH-01**: skill.md 包含清晰的 API 认证引导，说明如何获取和配置 API 密钥
- [ ] **AUTH-02**: 认证失败时提供明确的错误提示和解决指引

### Device Query (DEV)

- [ ] **DEV-01**: 用户可以通过自然语言查询设备列表（支持分页、筛选）
- [ ] **DEV-02**: 用户可以通过自然语言查询单个设备的详细信息

### Data Query (DATA)

- [ ] **DATA-01**: 用户可以通过自然语言查询指定设备的实时/当前数据
- [ ] **DATA-02**: 用户可以通过自然语言查询指定设备的历史数据（支持时间范围）

### Analysis (ANALYSIS)

- [ ] **ANALYSIS-01**: skill 能对设备数据进行趋势分析（变化趋势、极值、平均值）
- [ ] **ANALYSIS-02**: skill 能对比多个设备的数据差异

### Alert (ALERT)

- [ ] **ALERT-01**: skill 能识别数据异常并提醒用户（超出阈值、突变等）

### Skill File (SKILL)

- [ ] **SKILL-01**: 产出一份通用 skill.md，涵盖 insentek OpenAPI 所有可用接口
- [ ] **SKILL-02**: skill.md 采用 Hybrid 设计（Function Schema + Prompt），兼容主流 Agent 平台
- [ ] **SKILL-03**: skill.md 适配多行业场景，不绑定单一行业

### Documentation (DOC)

- [ ] **DOC-01**: 编写配套使用文档（参数说明、调用方式）
- [ ] **DOC-02**: 编写各 Agent 平台（OpenClaw、Claude Code、ChatGPT 等）适配指南

### Examples (EXAMPLE)

- [ ] **EXAMPLE-01**: 提供 5+ 组对话示例（查询类、报告类、分析类）
- [ ] **EXAMPLE-02**: 提供输出格式示例（表格、总结、报告模板）

### Platform Compatibility (PLATFORM)

- [ ] **PLATFORM-01**: skill.md 在 OpenClaw 和 Claude Code 双平台验证通过
- [ ] **PLATFORM-02**: skill.md 在 ChatGPT（Custom GPT / Instructions）验证通过

## v2 Requirements (Deferred)

- 行业模板报告（农业/制造业/能源专属报告模板）
- 数据预测能力（基于历史数据的趋势预测）
- 多语言输出优化（非中文用户的体验优化）

## Out of Scope

- ** skill 生成工具或自动化平台** — 本项目是内容产出，非工具开发
- **按行业拆分多个 skill 文件** — 坚持一个通用 skill 覆盖所有场景
- **修改或扩展底层 insentek API 功能** — 仅基于现有 API 能力包装
- **SDK、API 服务或其他非 skill.md 形式的交付物**

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| (To be filled by roadmap) | | |

---
*Requirements defined: 2026-05-13*
