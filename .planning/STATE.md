---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: Phase 6
status: Phase 6 completed, v1.0.1 skill enhanced
last_updated: "2026-05-14T00:00:00.000Z"
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 4
  completed_plans: 4
---

﻿# State

**Project:** insentek-api-skills
**Current Phase:** Phase 6
**Status:** Phase 6 completed, v1.0.1 enhanced

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-13)

**Core value:** 让终端用户用自然语言轻松查询设备数据
**Current focus:** Phase 6 — Skill 能力扩展（意图识别、查询边界、脚本导出）

## Phase Status

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| 1: API 接口梳理与映射 | Completed | 2026-05-13 | 2026-05-13 |
| 2: Skill 核心文件编写 | Completed | 2026-05-13 | 2026-05-13 |
| 3: 配套文档编写 | Completed | 2026-05-13 | 2026-05-13 |
| 4: 示例与输出格式 | Completed | 2026-05-13 | 2026-05-13 |
| 5: 跨平台测试与适配 | Completed | 2026-05-13 | 2026-05-13 |
| 6: Skill 能力扩展 | Completed | 2026-05-14 | 2026-05-14 |

## v1.0.1 核心能力

### Intent Resolution（意图识别与确认）
- 三层意图模型：L1 核心意图 → L2 输出意图 → L3 格式意图
- 关键词自动映射
- 意图不明确时主动询问，不自作主张

### Query Guardrails（查询边界限制）
- 单次查询最大跨度：365 天
- 历史数据最大回溯：3 年
- 对话展示上限：200 条（超限自动摘要）
- 文件导出上限：50,000 条（超限拒绝并建议缩小范围）

### Utility Scripts（实用脚本）
- `scripts/insentek_cli.py` — 统一 CLI（认证、设备查询、数据查询、CSV/JSON/HTML 导出、环境检查）
- `scripts/export_excel.py` — Excel 导出（多 sheet：原始数据 + 统计摘要）
- 脚本内置边界检查，结构化 JSON 输出

### Environment Prerequisites（环境前置检查）
- `insentek_cli.py check` — 一键检查 Python 版本、脚本完整性、依赖安装、API 可达性
- 首次交互前自动执行，避免中途因环境问题失败
- 区分关键检查（必须满足）和可选检查（影响部分功能）

## Active Decisions

- 一个通用 skill.md 覆盖所有场景（非多文件拆分）
- 内容产出而非工具开发
- Horizontal Layers 项目结构
- Agent 通过脚本调用 API，替代直接 curl

## Blockers

None.

## Notes

Project initialized via `/gsd-new-project`.
v1.0.1 adds dry-run preview mode and raw data output guardrails.

---
*State updated: 2026-05-14*
