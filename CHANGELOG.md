Changelog
=========

[1.0.3] - 2026-05-22
--------------------

Added
-----

- 数据可用性校验 (skill.md Section 2.5)
  - `query_data` 返回后 Agent 必须检查实际数据范围 vs 用户请求范围
  - 若实际覆盖比例 < 50% 或天数 < 7 天，必须 STOP 并向用户确认
  - 确认消息包含：请求范围、实际范围、可能原因（设备未部署/离线）
  - 用户确认后才允许继续生成报告

- 报告时间范围标注规范 (skill.md Section 8.3)
  - 实际范围 = 请求范围：正常标注
  - 实际范围 < 请求范围：必须注明 "基于实际可用数据: [actual_range]"
  - 绝不允许用请求范围替代实际范围，避免误导用户

- Flow 7 数据范围不匹配处理示例 (skill.md Section 12)
  - 新增完整交互示例：用户请求近3个月，实际仅13天
  - 展示 Agent 如何向用户说明情况并等待确认

Changed
-------

- 报告生成流程 (skill.md Section 8.3)
  - 在 `query_data` 与 `Agent analyzes data` 之间插入数据可用性校验步骤
  - Flow 6 增加 `[数据可用性校验] → PASS` 标注

- 版本号统一 bumped 1.0.2 → 1.0.3
  - skill.md, README.md, PLATFORM-TEST.md, docs/platform-setup.md

Why
---

- 用户实际测试发现：请求近3个月数据时，设备仅有13天数据
- 旧版本直接生成报告并标注"近3个月"，对用户产生严重误导
- 新增校验机制确保报告时间范围真实反映数据可用性

[1.0.2] - 2026-05-21
--------------------

Added
-----

- `scripts/write_html.py` — HTML file writer utility
  - Receives AI-generated HTML content and writes it to disk
  - No templating or data processing; purely a safe file-writing tool
  - Supports `--content`, `--input-file`, and stdin input
  - Minimal HTML structure validation (warnings only, non-blocking)
  - Structured JSON output for Agent consumption

Changed
-------

- Removed deprecated `report` / `chart` / `export --format html` from `scripts/insentek_cli.py`
  - Deleted `generate_report()`, `generate_chart()`, `get_device_info()`, `extract_param_names()` (~480 lines)
  - HTML reports are now fully Agent-generated; no hard-coded templates
  - Updated docstring and argparse to reflect only csv/json export

- Updated `skill.md`
  - Replaced Section 6.4 `generate_report (DEPRECATED)` with 6.4 `write_html`
  - Added `write_html.py` to environment check items (non-critical)
  - Changed API doc reference from active guidance to fallback note in Notes
  - Updated `--dry-run` note to remove `report` and `chart`

- Updated `.planning/STATE.md`
  - Added `write_html.py` to Utility Scripts list
  - Removed HTML export from `insentek_cli.py` description

Why
---

- User requirements for reports are diverse; fixed templates cannot cover all scenarios
- Delegate report generation to AI for flexibility (dynamic analysis, custom visualizations)
- Provide a clean, single-purpose tool for HTML file output rather than monolithic report generators

[1.0.1] - 2026-05-21
--------------------

Added
-----

- --dry-run preview mode (scripts/insentek_cli.py)
  - data, export (csv/json/html), report, chart subcommands all support --dry-run
  - Only outputs record count, time range, field summary (nodes/parameters), and first 5 sample rows
  - Does not write files or output full data, preventing context explosion during debugging

- --dry-run preview mode (scripts/export_excel.py)
  - Added --dry-run parameter, behavior consistent with CLI script
  - Does not generate Excel file, only returns structured JSON preview

- Raw data output prohibition (skill.md)
  - Added Section 2.4 "Raw Data Output Prohibition"
  - Explicitly prohibits Agent from outputting raw sensor full data directly into conversation
  - Specifies handling for four common scenarios: summary sampling, --dry-run, guided export, direct refusal

- YAML Guardrails declaration (skill.md frontmatter)
  - Added guardrails.raw_data_output: PROHIBITED
  - Added guardrails.dry_run_preview_rows: 5
  - Added guardrails.max_chat_rows: 200
  - Added guardrails.max_export_rows: 50000

- Dry-run documentation (skill.md)
  - Added Section 6.0 "dry-run preview mode (common to all export scripts)"
  - Added --dry-run example in query_data Agent Action
  - Added "Dry-run first" and "Raw data prohibition" development guidelines in Notes

Changed
-------

- Version bumped from 1.0.0 to 1.0.1 (skill.md, README.md, PLATFORM-TEST.md, .planning/STATE.md)

Why
---

- Prevent accidental full sensor data injection into conversation context
- Save Token consumption and improve model processing efficiency
- Promote as Skill development standard: summaries in chat, full data in files


[1.0.0] - 2026-05-14
--------------------

Added
-----

- Initial release with intent resolution, query guardrails, and export scripts
- Three-layer intent model (L1 core -> L2 output -> L3 format)
- Query guardrails: max 365 days span, max 3 years history, max 200 chat rows, max 50000 export rows
- Utility scripts: insentek_cli.py (unified CLI), export_excel.py (Excel export)
- Environment prerequisites check command
- Session-based authentication caching
- Multi-industry adaptation (agriculture, meteorology, industrial level monitoring)
