# Insentek OpenAPI Scripts

本目录包含 Insentek OpenAPI 的参考实现脚本。Agent 通过调用这些脚本完成 API 交互、数据导出和报告生成，而非直接使用 `curl` 命令。

## 设计原则

1. **统一入口**: `insentek_cli.py` 封装所有 API 调用，Agent 只需学习一套参数风格
2. **边界内置**: 脚本内部实现时间范围限制、数据量检查，Agent 无需重复实现
3. **结构化输出**: 所有脚本输出 JSON 到 stdout，便于 Agent 解析和决策
4. **零配置运行**: 仅依赖 Python 标准库（Excel 导出除外）

## 脚本列表

| 脚本 | 功能 | 依赖 |
|------|------|------|
| `insentek_cli.py` | 统一 CLI：认证、设备查询、数据查询、CSV/JSON 导出 | Python 3.8+ |
| `write_html.py` | HTML 文件写入：将 AI 生成的 HTML 内容安全落盘 | Python 3.8+ |
| `export_excel.py` | Excel 导出（多 sheet：原始数据 + 统计摘要） | Python 3.8+, openpyxl |

## 使用示例

### 环境检查（首次使用前必做）
```bash
python insentek_cli.py check
```

输出示例：
```json
{
  "success": true,
  "all_checks_passed": true,
  "checks": {
    "python": {"ok": true, "version": "3.11.0", "message": "Python 3.11.0 满足要求 (>=3.8)"},
    "scripts_cli": {"ok": true, "path": "...", "message": "核心脚本 insentek_cli.py 已找到"},
    "scripts_excel": {"ok": true, "path": "...", "message": "Excel 脚本 export_excel.py 已找到"},
    "scripts_write_html": {"ok": true, "path": "...", "message": "HTML 写入脚本 write_html.py 已找到"},
    "openpyxl": {"ok": true, "version": "3.1.2", "message": "openpyxl 3.1.2 已安装，Excel 导出可用"},
    "curl": {"ok": true, "message": "curl 可用，可作为脚本不可用时的 fallback"},
    "api_reachable": {"ok": true, "status": 400, "message": "API 服务可访问（HTTP 400，未提供认证参数）"}
  },
  "summary": {
    "critical": "通过",
    "optional": "全部通过",
    "message": "环境检查通过，所有功能可用。"
  }
}
```

### 认证
```bash
python insentek_cli.py auth --appid YOUR_APPID --secret YOUR_SECRET
```

### 查询设备列表
```bash
python insentek_cli.py devices --token YOUR_TOKEN --page 1 --limit 20
```

### 查询数据（含边界检查）
```bash
python insentek_cli.py data --token YOUR_TOKEN --sn 00000000000000 --range 20250101,20250131
```

### 导出 CSV
```bash
python insentek_cli.py export --token YOUR_TOKEN --sn 00000000000000 --range 20250101,20250131 --format csv --output data.csv
```

### 导出 Excel
```bash
python export_excel.py --token YOUR_TOKEN --sn 00000000000000 --range 20250101,20250131 --output data.xlsx
```

### 写入 HTML 报告（AI 动态生成内容后落盘）
```bash
python write_html.py --content "<html>...</html>" --output report.html
```

## 输出格式

所有脚本成功时输出：
```json
{
  "success": true,
  "total": 1000,
  "file": "/path/to/file.csv",
  "message": "成功导出 1000 条数据到 data.csv"
}
```

失败时输出：
```json
{
  "success": false,
  "error": "单次查询最多支持 1 年范围..."
}
```

## 边界限制

| 限制项 | 值 | 说明 |
|--------|-----|------|
| 单次最大跨度 | 365 天 | 超过则拒绝并提示拆分 |
| 最大历史回溯 | 3 年 | 基于当前日期 |
| 对话展示上限 | 200 条 | 超过则展示摘要+抽样 |
| 文件导出上限 | 50,000 条 | 超过则拒绝并建议缩小范围 |
