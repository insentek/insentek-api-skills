Changelog
=========

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
