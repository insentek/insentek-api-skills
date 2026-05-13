# Phase 2: Skill 核心文件编写 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-13
**Phase:** 2-Skill 核心文件编写
**Areas discussed:** skill.md 格式规范, 分析能力实现方式, 异常检测实现方式, 输出格式规范

---

## skill.md 格式规范 — Function Schema vs Prompt vs Hybrid

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid 设计（YAML + Schema + Prompt） | YAML frontmatter + Function Schema 定义工具 + Prompt 补充推理逻辑 | ✓ |
| Function Schema 模式 | 纯结构化工具定义 | |
| Prompt-only 模式 | 纯自然语言描述 | |

**User's choice:** Hybrid 设计
**Notes:** YAML frontmatter（名称/描述/版本）+ Function Schema 区（3 个核心工具）+ Prompt 区（时间推断、链式调用、输出格式）。

---

## 分析能力实现方式 — Agent 自行分析 vs 定义分析工具

| Option | Description | Selected |
|--------|-------------|----------|
| Prompt 指令实现 | Agent 获取数据后自行计算趋势和对比 | ✓ |
| 定义分析工具 | 增加 analyze_trend / compare_devices 工具 | |

**User's choice:** Prompt 指令实现
**Notes:** ANALYSIS-01（趋势分析）和 ANALYSIS-02（跨设备对比）通过 Prompt 指令实现，不增加额外工具。Agent 自行计算平均值、最大值、最小值、变化率。

---

## 异常检测实现方式 — Prompt 规则 vs 阈值工具

| Option | Description | Selected |
|--------|-------------|----------|
| Prompt 规则实现 | skill.md 中嵌入异常识别规则，Agent 自动标记 | ✓ |
| 定义 check_alerts 工具 | 增加异常检测工具，需要用户提供阈值 | |

**User's choice:** Prompt 规则实现
**Notes:** ALERT-01 通过 Prompt 规则实现。异常规则：moisture < 5% 或 > 50% 标记为异常；温度 1 小时内变化 > 10°C 标记为突变。

---

## 输出格式规范 — Markdown 表格 vs 结构化报告

| Option | Description | Selected |
|--------|-------------|----------|
| 智能格式模式 | 根据查询类型自动选择输出格式 | ✓ |
| 统一 Markdown 表格 | 所有查询结果统一用表格呈现 | |

**User's choice:** 智能格式模式
**Notes:** 实时数据→简洁卡片，历史数据→表格+趋势小结，对比分析→并排表格+差异高亮，异常报告→带标记的列表。

---

## Claude's Discretion

无 — 所有关键决策均由用户明确选择。

## Deferred Ideas

- 行业模板报告（农业/制造业/能源专属报告模板）— v2 需求
- 数据预测能力 — v2 需求
- Pluviometer / Lingyun 专用 skill 工具 — Phase 2+ 扩展
