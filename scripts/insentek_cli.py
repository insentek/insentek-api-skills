#!/usr/bin/env python3
"""
Insentek OpenAPI Unified CLI

封装所有 API 调用、认证管理、边界检查与数据导出能力。
Agent 通过调用此脚本执行所有操作，而非直接使用 curl。

Usage:
    python insentek_cli.py auth --appid APPID --secret SECRET
    python insentek_cli.py devices --token TOKEN [--page 1] [--limit 20]
    python insentek_cli.py device --sn SN --token TOKEN
    python insentek_cli.py data --sn SN --range START,END --token TOKEN [--include-params moisture,temperature] [--dry-run]
    python insentek_cli.py export --sn SN --range START,END --format csv --token TOKEN --output file.csv [--dry-run]
    python insentek_cli.py report --sn SN --range START,END --token TOKEN --output report.html [--dry-run]
    python insentek_cli.py chart --sn SN --range START,END --type scatter --params airTemperature,relativeHumidity --title "标题" --conclusion "分析结论" --token TOKEN --output chart.html [--dry-run]
"""

import argparse
import csv
import html
import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

API_BASE_URL = os.environ.get("INSENTEK_API_BASE", "http://openapi.ecois.info")

# 边界限制常量
MAX_RANGE_DAYS = 365
MAX_HISTORY_YEARS = 3
MAX_CHAT_ROWS = 200
MAX_EXPORT_ROWS = 50000
DRY_RUN_PREVIEW_ROWS = 5


def api_request(path, headers=None, params=None, method="GET", data=None):
    """发送 HTTP 请求并返回 JSON 响应。"""
    url = f"{API_BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data and method in ("POST", "PUT", "PATCH"):
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err = json.loads(body)
        except json.JSONDecodeError:
            err = {"message": body}
        return {"_http_error": True, "status": e.code, "error": err}
    except Exception as e:
        return {"_http_error": True, "status": 0, "error": {"message": str(e)}}


def authenticate(appid, secret):
    """获取 access token。"""
    result = api_request("/v3/token", params={"appid": appid, "secret": secret})
    if result.get("_http_error"):
        print(json.dumps({"success": False, "error": result["error"]}, ensure_ascii=False, indent=2))
        sys.exit(1)
    print(json.dumps({"success": True, "token": result.get("token"), "expires": result.get("expires")}, ensure_ascii=False, indent=2))


def list_devices(token, page=1, limit=20):
    """查询设备列表。"""
    result = api_request("/v3/devices", headers={"Authorization": token}, params={"page": page, "limit": limit})
    print(json.dumps(result, ensure_ascii=False, indent=2))


def get_device(token, sn):
    """查询单个设备详情及参数描述。"""
    detail = api_request(f"/v3/device/{sn}", headers={"Authorization": token})
    desc = api_request(f"/v3/device/{sn}/description", headers={"Authorization": token})
    print(json.dumps({"detail": detail, "description": desc}, ensure_ascii=False, indent=2))


def parse_range(range_str):
    """解析 range 字符串为 (start_date, end_date)。"""
    parts = range_str.split(",")
    if len(parts) != 2:
        return None
    try:
        start = datetime.strptime(parts[0], "%Y%m%d").date()
        end = datetime.strptime(parts[1], "%Y%m%d").date()
        return start, end
    except ValueError:
        return None


def validate_range(range_str):
    """
    验证时间范围是否符合边界限制。
    返回 (ok: bool, error_msg: str, start_date, end_date)
    """
    parsed = parse_range(range_str)
    if parsed is None:
        return False, "时间范围格式错误，应为 YYYYMMDD,YYYYMMDD", None, None

    start, end = parsed
    today = date.today()

    if start > end:
        return False, "开始日期不能晚于结束日期", start, end

    span_days = (end - start).days + 1
    if span_days > MAX_RANGE_DAYS:
        return (
            False,
            f"查询跨度为 {span_days} 天，超过最大限制 {MAX_RANGE_DAYS} 天。"
            f"建议拆分为多次查询（如每次查询 3 个月），或缩小时间范围。",
            start,
            end,
        )

    max_history = today - timedelta(days=365 * MAX_HISTORY_YEARS)
    if end < max_history:
        return (
            False,
            f"结束日期 {end} 超过最大历史回溯限制（{MAX_HISTORY_YEARS} 年）。"
            f"最早支持查询到 {max_history.strftime('%Y-%m-%d')}。",
            start,
            end,
        )

    return True, "", start, end


def query_data(token, sn, range_str, include_params=None, include_nodes=None):
    """
    查询设备历史数据，含边界检查。
    返回原始 API 响应字典。
    """
    ok, err_msg, _, _ = validate_range(range_str)
    if not ok:
        return {"_validation_error": True, "message": err_msg}

    params = {"range": range_str}
    if include_params:
        params["includeParameters"] = include_params
    if include_nodes:
        params["includeNodes"] = include_nodes

    return api_request(f"/v3/device/{sn}/data", headers={"Authorization": token}, params=params)


def flatten_data(api_response):
    """
    将 API 嵌套结构扁平化为行列表，便于 JSON 导出。
    输入: {list: [{timestamp, datetime, values: {node: {param: value}}}]}
    输出: [{timestamp, datetime, node, param, value}, ...]
    """
    rows = []
    for item in api_response.get("list", []):
        ts = item.get("timestamp")
        dt = item.get("datetime")
        values = item.get("values", {})
        for node, params in values.items():
            for param, value in params.items():
                rows.append({
                    "timestamp": ts,
                    "datetime": dt,
                    "node": node,
                    "parameter": param,
                    "value": value,
                })
    return rows


def pivot_data(api_response, sn):
    """
    将 API 嵌套结构转换为宽格式（时间 × 参数）。
    输入: {list: [{timestamp, datetime, values: {node: {param: value}}}]}, sn
    输出: (fieldnames: [str], rows: [dict])
    每行代表一个时间点，列包括 SN、datetime、node 和各参数。
    """
    # 收集所有唯一的参数名（按字母序稳定排序）
    param_names = set()
    for item in api_response.get("list", []):
        for node, params in item.get("values", {}).items():
            param_names.update(params.keys())
    param_names = sorted(param_names)

    fieldnames = ["SN", "datetime", "node"] + param_names

    rows = []
    for item in api_response.get("list", []):
        dt = item.get("datetime")
        values = item.get("values", {})
        for node, params in values.items():
            row = {
                "SN": f"{sn}",
                "datetime": dt,
                "node": node,
            }
            for param in param_names:
                row[param] = params.get(param, "")
            rows.append(row)

    return fieldnames, rows


def dry_run_summary(result, sn, range_str):
    """
    生成 --dry-run 预览输出：数据条数、时间范围、字段摘要、前 N 条预览。
    不写入文件，仅输出结构化 JSON。
    """
    if result.get("_validation_error") or result.get("_http_error"):
        print(json.dumps({"success": False, "error": result.get("message") or result.get("error")}, ensure_ascii=False, indent=2))
        sys.exit(1)

    total = result.get("total", 0)
    flat = flatten_data(result)

    nodes = sorted(set(r["node"] for r in flat))
    params = sorted(set(r["parameter"] for r in flat))
    preview = flat[:DRY_RUN_PREVIEW_ROWS]

    output = {
        "dry_run": True,
        "total": total,
        "time_range": {
            "start": range_str.split(",")[0] if "," in range_str else "",
            "end": range_str.split(",")[1] if "," in range_str else ""
        },
        "fields": {
            "nodes": nodes,
            "parameters": params
        },
        "preview": preview,
        "message": f"Dry run: {total} records, {len(nodes)} nodes, {len(params)} parameters. First {len(preview)} rows shown. Use without --dry-run to export full data."
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def export_csv(token, sn, range_str, output_path, include_params=None, dry_run=False):
    """导出数据为 CSV 文件（宽格式：每行一个时间点，参数作为列）。"""
    result = query_data(token, sn, range_str, include_params)
    if result.get("_validation_error") or result.get("_http_error"):
        print(json.dumps({"success": False, "error": result.get("message") or result.get("error")}, ensure_ascii=False, indent=2))
        sys.exit(1)

    total = result.get("total", 0)
    if total > MAX_EXPORT_ROWS:
        print(json.dumps({
            "success": False,
            "error": f"数据量 {total} 条超过导出上限 {MAX_EXPORT_ROWS} 条，建议缩小时间范围或分批导出。"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    if dry_run:
        dry_run_summary(result, sn, range_str)
        return

    fieldnames, rows = pivot_data(result, sn)
    if not rows:
        print(json.dumps({"success": True, "total": 0, "file": output_path, "message": "无数据"}, ensure_ascii=False, indent=2))
        return

    # UTF-8 BOM for Excel compatibility
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({
        "success": True,
        "total": total,
        "file": str(Path(output_path).resolve()),
        "message": f"成功导出 {total} 条数据到 {output_path}"
    }, ensure_ascii=False, indent=2))


def export_json(token, sn, range_str, output_path, include_params=None, dry_run=False):
    """导出原始 API 响应为 JSON 文件。"""
    result = query_data(token, sn, range_str, include_params)
    if result.get("_validation_error") or result.get("_http_error"):
        print(json.dumps({"success": False, "error": result.get("message") or result.get("error")}, ensure_ascii=False, indent=2))
        sys.exit(1)

    total = result.get("total", 0)
    if total > MAX_EXPORT_ROWS:
        print(json.dumps({
            "success": False,
            "error": f"数据量 {total} 条超过导出上限 {MAX_EXPORT_ROWS} 条，建议缩小时间范围或分批导出。"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    if dry_run:
        dry_run_summary(result, sn, range_str)
        return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "success": True,
        "total": total,
        "file": str(Path(output_path).resolve()),
        "message": f"成功导出 {total} 条数据到 {output_path}"
    }, ensure_ascii=False, indent=2))


def generate_report(token, sn, range_str, output_path, include_params=None, dry_run=False):
    """生成简单的 HTML 报告，含数据表格和趋势统计。"""
    result = query_data(token, sn, range_str, include_params)
    if result.get("_validation_error") or result.get("_http_error"):
        print(json.dumps({"success": False, "error": result.get("message") or result.get("error")}, ensure_ascii=False, indent=2))
        sys.exit(1)

    total = result.get("total", 0)
    if total > MAX_EXPORT_ROWS:
        print(json.dumps({
            "success": False,
            "error": f"数据量 {total} 条超过报告上限 {MAX_EXPORT_ROWS} 条，建议缩小时间范围。"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    if dry_run:
        dry_run_summary(result, sn, range_str)
        return

    # 统计数据仍用长格式
    flat_rows = flatten_data(result)

    # 按时间聚合的宽格式数据（与 CSV 一致）
    fieldnames, pivot_rows = pivot_data(result, sn)

    # 统计每个参数
    stats = {}
    for r in flat_rows:
        key = f"{r['node']} - {r['parameter']}"
        if key not in stats:
            stats[key] = []
        try:
            stats[key].append(float(r["value"]))
        except (TypeError, ValueError):
            pass

    stat_rows = []
    for key, vals in stats.items():
        if vals:
            stat_rows.append({
                "metric": key,
                "count": len(vals),
                "avg": round(sum(vals) / len(vals), 3),
                "min": round(min(vals), 3),
                "max": round(max(vals), 3),
            })

    # 构建 HTML 表头（宽格式，参数作为列）
    header_cells = "".join(f"<th>{fn}</th>" for fn in fieldnames)

    # 分页参数
    PAGE_SIZE = 50
    display_rows = pivot_rows[:5000]
    total_pages = max(1, (len(display_rows) + PAGE_SIZE - 1) // PAGE_SIZE)

    # 构建数据行（带 data-page 属性，用于 JS 分页）
    data_rows_html = ""
    for idx, row in enumerate(display_rows):
        page_num = (idx // PAGE_SIZE) + 1
        cells = "".join(f"<td>{row.get(fn, '')}</td>" for fn in fieldnames)
        bg = ' style="background:#fafafa;"' if idx % 2 == 1 else ""
        data_rows_html += f'<tr data-page="{page_num}"{bg}>{cells}</tr>\n'

    if len(pivot_rows) > 5000:
        data_rows_html += f"<tr><td colspan='{len(fieldnames)}' style='text-align:center;color:#999;'>... 共 {len(pivot_rows)} 条时间点数据，此处展示前 5000 条 ...</td></tr>\n"

    # 构建 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>设备 {sn} 数据报告</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #333; }}
h1 {{ border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
.info {{ color: #666; margin-bottom: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f2f2f2; font-weight: 600; position: sticky; top: 0; }}
tr:nth-child(even) {{ background: #fafafa; }}
.summary {{ background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0; }}
.raw-data {{ overflow-x: auto; }}
.pagination {{ margin: 15px 0; display: flex; align-items: center; gap: 10px; font-size: 14px; }}
.pagination button {{ padding: 6px 14px; border: 1px solid #ddd; background: #fff; cursor: pointer; border-radius: 4px; }}
.pagination button:hover {{ background: #f2f2f2; }}
.pagination button:disabled {{ opacity: 0.4; cursor: not-allowed; }}
.pagination .page-info {{ color: #666; }}
.pagination .page-jump {{ display: flex; align-items: center; gap: 6px; }}
.pagination input[type="number"] {{ width: 60px; padding: 5px; border: 1px solid #ddd; border-radius: 4px; }}
</style>
</head>
<body>
<h1>设备数据报告</h1>
<div class="info">
  <p><strong>设备 SN:</strong> {html.escape(sn)}</p>
  <p><strong>时间范围:</strong> {html.escape(range_str)}</p>
  <p><strong>数据条数:</strong> {total}</p>
  <p><strong>时间点数:</strong> {len(pivot_rows)}</p>
  <p><strong>生成时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
</div>

<div class="summary">
<h2>统计摘要</h2>
<table>
<tr><th>指标</th><th>样本数</th><th>平均值</th><th>最小值</th><th>最大值</th></tr>
"""
    for s in stat_rows:
        html += f"<tr><td>{s['metric']}</td><td>{s['count']}</td><td>{s['avg']}</td><td>{s['min']}</td><td>{s['max']}</td></tr>\n"

    html += f"""</table>
</div>

<h2>原始数据（按时间聚合，参数为列）</h2>
<div class="pagination">
  <button id="prevBtn" onclick="goPage(currentPage - 1)">上一页</button>
  <span class="page-info">第 <span id="currentPage">1</span> / <span id="totalPages">{total_pages}</span> 页（每页 {PAGE_SIZE} 条）</span>
  <button id="nextBtn" onclick="goPage(currentPage + 1)">下一页</button>
  <div class="page-jump">
    <span>跳到</span>
    <input type="number" id="jumpInput" min="1" max="{total_pages}" value="1" onkeydown="if(event.key==='Enter'){{jumpPage()}}">
    <button onclick="jumpPage()">GO</button>
  </div>
</div>
<div class="raw-data">
<table id="dataTable">
<thead><tr>{header_cells}</tr></thead>
<tbody>
{data_rows_html}</tbody>
</table>
</div>

<script>
const PAGE_SIZE = {PAGE_SIZE};
const totalPages = {total_pages};
let currentPage = 1;

function renderPage(page) {{
  if (page < 1 || page > totalPages) return;
  currentPage = page;
  document.querySelectorAll('#dataTable tbody tr[data-page]').forEach(function(tr) {{
    tr.style.display = (parseInt(tr.getAttribute('data-page')) === page) ? '' : 'none';
  }});
  document.getElementById('currentPage').textContent = page;
  document.getElementById('jumpInput').value = page;
  document.getElementById('prevBtn').disabled = (page === 1);
  document.getElementById('nextBtn').disabled = (page === totalPages);
}}

function goPage(page) {{ renderPage(page); }}

function jumpPage() {{
  const input = document.getElementById('jumpInput');
  let p = parseInt(input.value, 10);
  if (isNaN(p) || p < 1) p = 1;
  if (p > totalPages) p = totalPages;
  renderPage(p);
}}

renderPage(1);
</script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(json.dumps({
        "success": True,
        "total": total,
        "file": str(Path(output_path).resolve()),
        "message": f"成功生成报告 {output_path}"
    }, ensure_ascii=False, indent=2))



def get_device_info(token, sn):
    detail = api_request(f"/v3/device/{sn}", headers={"Authorization": token})
    desc = api_request(f"/v3/device/{sn}/description", headers={"Authorization": token})
    return detail, desc


def extract_param_names(description):
    mapping = {}
    for param_group in description.get("parameters", []):
        for code, info in param_group.items():
            mapping[code] = info.get("name", code)
    return mapping


def generate_chart(token, sn, range_str, chart_type, params, title, conclusion, output_path, include_params=None, dry_run=False):
    result = query_data(token, sn, range_str, include_params)
    if result.get("_validation_error") or result.get("_http_error"):
        print(json.dumps({"success": False, "error": result.get("message") or result.get("error")}, ensure_ascii=False, indent=2))
        sys.exit(1)

    total = result.get("total", 0)
    if total > MAX_EXPORT_ROWS:
        print(json.dumps({"success": False, "error": f"数据量 {total} 条超过报告上限 {MAX_EXPORT_ROWS} 条"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    if dry_run:
        dry_run_summary(result, sn, range_str)
        return

    data_list = result.get("list", [])
    if not data_list:
        print(json.dumps({"success": True, "total": 0, "file": output_path, "message": "无数据"}, ensure_ascii=False, indent=2))
        return

    detail, desc = get_device_info(token, sn)
    param_name_map = extract_param_names(desc)
    alias = detail.get("alias", sn) if not detail.get("_http_error") else sn
    device_type = detail.get("type", "") if not detail.get("_http_error") else ""
    location = detail.get("location", {}) if not detail.get("_http_error") else {}
    city = location.get("city", "")
    province = location.get("province", "")
    param_list = [p.strip() for p in params.split(",")] if params else []

    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    assets_path = project_root / "assets" / "echarts.min.js"
    output_dir = Path(output_path).parent.resolve()
    try:
        echarts_rel = os.path.relpath(assets_path, output_dir).replace("\\", "/")
    except ValueError:
        echarts_rel = "./assets/echarts.min.js"
    if not assets_path.exists():
        echarts_rel = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"

    colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4"]

    if chart_type == "scatter":
        x_param = param_list[0] if len(param_list) > 0 else ""
        y_param = param_list[1] if len(param_list) > 1 else param_list[0] if len(param_list) > 0 else ""
        scatter_data = []
        for item in data_list:
            for node, params_dict in item.get("values", {}).items():
                xv = params_dict.get(x_param)
                yv = params_dict.get(y_param)
                if xv not in (None, "") and yv not in (None, ""):
                    try:
                        scatter_data.append([float(xv), float(yv)])
                    except (ValueError, TypeError):
                        pass
        option = {
            "title": {"text": title or f"{param_name_map.get(x_param, x_param)} vs {param_name_map.get(y_param, y_param)}", "left": "center"},
            "tooltip": {"trigger": "item", "formatter": f"{param_name_map.get(x_param, x_param)}: {{c[0]}}\n{param_name_map.get(y_param, y_param)}: {{c[1]}}"},
            "xAxis": {"name": param_name_map.get(x_param, x_param), "type": "value", "scale": True},
            "yAxis": {"name": param_name_map.get(y_param, y_param), "type": "value", "scale": True},
            "series": [{"type": "scatter", "symbolSize": 10, "data": scatter_data, "itemStyle": {"color": colors[0]}}]
        }

    elif chart_type == "dual":
        p1 = param_list[0] if len(param_list) > 0 else ""
        p2 = param_list[1] if len(param_list) > 1 else ""
        times = [item.get("datetime", "") for item in data_list]
        s1_data, s2_data = [], []
        for item in data_list:
            for node, params_dict in item.get("values", {}).items():
                v1 = params_dict.get(p1)
                v2 = params_dict.get(p2)
                s1_data.append(float(v1) if v1 not in (None, "") else None)
                s2_data.append(float(v2) if v2 not in (None, "") else None)
        option = {
            "title": {"text": title or f"{param_name_map.get(p1, p1)} & {param_name_map.get(p2, p2)}", "left": "center"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "legend": {"data": [param_name_map.get(p1, p1), param_name_map.get(p2, p2)], "top": 30},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {"type": "category", "boundaryGap": False, "data": times, "axisLabel": {"rotate": 30, "fontSize": 11}},
            "yAxis": [
                {"type": "value", "name": param_name_map.get(p1, p1), "position": "left", "axisLine": {"lineStyle": {"color": colors[0]}}},
                {"type": "value", "name": param_name_map.get(p2, p2), "position": "right", "axisLine": {"lineStyle": {"color": colors[1]}}}
            ],
            "series": [
                {"name": param_name_map.get(p1, p1), "type": "line", "yAxisIndex": 0, "data": s1_data, "itemStyle": {"color": colors[0]}, "smooth": True},
                {"name": param_name_map.get(p2, p2), "type": "line", "yAxisIndex": 1, "data": s2_data, "itemStyle": {"color": colors[1]}, "smooth": True}
            ]
        }

    else:
        all_params = set()
        for item in data_list:
            for node, params_dict in item.get("values", {}).items():
                all_params.update(params_dict.keys())
        all_params = sorted(all_params)
        if param_list:
            all_params = [p for p in all_params if p in param_list]
        times = [item.get("datetime", "") for item in data_list]
        series = []
        for i, p in enumerate(all_params):
            data_vals = []
            for item in data_list:
                val = None
                for node, params_dict in item.get("values", {}).items():
                    if p in params_dict:
                        try:
                            val = float(params_dict[p])
                        except (ValueError, TypeError):
                            val = None
                        break
                data_vals.append(val)
            series.append({
                "name": param_name_map.get(p, p),
                "type": "line",
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 4,
                "data": data_vals,
                "itemStyle": {"color": colors[i % len(colors)]}
            })
        option = {
            "title": {"text": title or "趋势分析", "left": "center"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "legend": {"data": [s["name"] for s in series], "top": 30},
            "grid": {"left": "3%", "right": "4%", "bottom": 80, "containLabel": True},
            "toolbox": {"feature": {"saveAsImage": {"title": "保存图片"}, "dataZoom": {"title": {"zoom": "区域缩放", "back": "还原"}}, "restore": {"title": "还原"}}},
            "dataZoom": [
                {"type": "slider", "show": True, "xAxisIndex": [0], "start": 0, "end": 100, "bottom": 30, "height": 28,
                 "borderColor": "#ddd", "fillerColor": "rgba(102, 126, 234, 0.15)", "handleStyle": {"color": "#667eea"},
                 "textStyle": {"color": "#666", "fontSize": 11}, "brushSelect": False},
                {"type": "inside", "xAxisIndex": [0], "start": 0, "end": 100}
            ],
            "xAxis": {"type": "category", "boundaryGap": False, "data": times, "axisLabel": {"rotate": 30, "fontSize": 11}},
            "yAxis": {"type": "value", "axisLabel": {"formatter": "{value}"}},
            "series": series
        }

    option_json = json.dumps(option, ensure_ascii=False).replace("</script", r"<\/script")

    # Data table
    all_params = set()
    for item in data_list:
        for node, params_dict in item.get("values", {}).items():
            all_params.update(params_dict.keys())
    all_params = sorted(all_params)
    if param_list:
        all_params = [p for p in all_params if p in param_list]

    PAGE_SIZE = 50
    fieldnames = ["datetime", "node"] + all_params
    header_cells = "".join(f'<th>{param_name_map.get(fn, fn)}</th>' for fn in fieldnames)

    rows = []
    for item in data_list:
        dt = item.get("datetime", "")
        for node, params_dict in item.get("values", {}).items():
            row = {"datetime": dt, "node": node}
            for p in all_params:
                row[p] = params_dict.get(p, "")
            rows.append(row)

    display_rows = rows[:5000]
    total_pages = max(1, (len(display_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
    data_rows_html = ""
    for idx, row in enumerate(display_rows):
        page_num = (idx // PAGE_SIZE) + 1
        cells = "".join(f'<td>{row.get(fn, "")}</td>' for fn in fieldnames)
        bg = ' style="background:#fafafa;"' if idx % 2 == 1 else ""
        data_rows_html += f'<tr data-page="{page_num}"{bg}>{cells}</tr>\n'
    if len(rows) > 5000:
        data_rows_html += f'<tr><td colspan="{len(fieldnames)}" style="text-align:center;color:#999;">... 共 {len(rows)} 条时间点数据，此处展示前 5000 条 ...</td></tr>\n'

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build HTML with string formatting (avoid f-string nesting)
    html = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>' + html.escape(title or "数据分析图表") + '</title>\n'
        '<script src="' + echarts_rel + '"></script>\n'
        '<style>\n'
        '* { margin: 0; padding: 0; box-sizing: border-box; }\n'
        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }\n'
        '.container { max-width: 1400px; margin: 0 auto; padding: 20px; }\n'
        '.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }\n'
        '.header h1 { font-size: 24px; margin-bottom: 10px; }\n'
        '.header .meta { opacity: 0.9; font-size: 14px; }\n'
        '.header .meta span { margin-right: 20px; }\n'
        '.card { background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }\n'
        '.card h2 { font-size: 18px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #f0f0f0; color: #1a1a1a; }\n'
        '#chart { width: 100%; height: 500px; }\n'
        '.conclusion { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; font-size: 14px; line-height: 1.8; }\n'
        'table { width: 100%; border-collapse: collapse; font-size: 13px; }\n'
        'th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }\n'
        'th { background: #f8f9fa; font-weight: 600; color: #555; position: sticky; top: 0; }\n'
        'tr:hover { background: #f8f9fa; }\n'
        '.table-wrap { max-height: 600px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px; }\n'
        '.pagination { margin: 15px 0; display: flex; align-items: center; gap: 10px; font-size: 14px; }\n'
        '.pagination button { padding: 6px 14px; border: 1px solid #ddd; background: #fff; cursor: pointer; border-radius: 4px; }\n'
        '.pagination button:hover { background: #f2f2f2; }\n'
        '.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }\n'
        '.pagination .page-info { color: #666; }\n'
        '.pagination input[type="number"] { width: 60px; padding: 5px; border: 1px solid #ddd; border-radius: 4px; }\n'
        '.footer { text-align: center; color: #999; font-size: 12px; padding: 20px; }\n'
        '@media (max-width: 768px) { .container { padding: 10px; } .header { padding: 20px; } #chart { height: 350px; } }\n'
        '</style>\n</head>\n<body>\n'
        '<div class="container">\n'
        '    <div class="header">\n'
        '        <h1>' + html.escape(title or "数据分析图表") + '</h1>\n'
        '        <div class="meta">\n'
        '            <span>设备: ' + html.escape(alias or sn) + '</span>\n'
        '            <span>SN: ' + html.escape(sn) + '</span>\n'
        '            <span>类型: ' + html.escape(device_type) + '</span>\n'
        '            <span>位置: ' + html.escape(province) + ' ' + html.escape(city) + '</span>\n'
        '            <span>时间: ' + html.escape(range_str) + '</span>\n'
        '        </div>\n'
        '    </div>\n'
        '    <div class="card">\n'
        '        <h2>分析图表</h2>\n'
        '        <div id="chart"></div>\n'
        '    </div>\n'
        '    <div class="card">\n'
        '        <h2>分析结论</h2>\n'
        '        <div class="conclusion">' + html.escape(conclusion or "暂无分析结论。") + '</div>\n'
        '    </div>\n'
        '    <div class="card">\n'
        '        <h2>原始数据</h2>\n'
        '        <div class="pagination">\n'
        '            <button id="prevBtn" onclick="goPage(currentPage - 1)">上一页</button>\n'
        '            <span class="page-info">第 <span id="currentPage">1</span> / <span id="totalPages">' + str(total_pages) + '</span> 页（每页 ' + str(PAGE_SIZE) + ' 条）</span>\n'
        '            <button id="nextBtn" onclick="goPage(currentPage + 1)">下一页</button>\n'
        '            <div class="page-jump">\n'
        '                <span>跳到</span>\n'
        '                <input type="number" id="jumpInput" min="1" max="' + str(total_pages) + '" value="1" onkeydown="if(event.key===\'Enter\'){jumpPage()}">\n'
        '                <button onclick="jumpPage()">GO</button>\n'
        '            </div>\n'
        '        </div>\n'
        '        <div class="table-wrap">\n'
        '            <table id="dataTable">\n'
        '                <thead><tr>' + header_cells + '</tr></thead>\n'
        '                <tbody>\n' + data_rows_html + '\n'
        '                </tbody>\n'
        '            </table>\n'
        '        </div>\n'
        '    </div>\n'
        '    <div class="footer">\n'
        '        <p>生成时间: ' + now_str + ' | 数据点数: ' + str(len(rows)) + ' | Insentek OpenAPI Chart</p>\n'
        '    </div>\n'
        '</div>\n'
        '<script>\n'
        'const PAGE_SIZE = ' + str(PAGE_SIZE) + ';\n'
        'const totalPages = ' + str(total_pages) + ';\n'
        'let currentPage = 1;\n'
        'function renderPage(page) {\n'
        '  if (page < 1 || page > totalPages) return;\n'
        '  currentPage = page;\n'
        '  document.querySelectorAll(\'#dataTable tbody tr[data-page]\').forEach(function(tr) {\n'
        '    tr.style.display = (parseInt(tr.getAttribute(\'data-page\')) === page) ? \'\' : \'none\';\n'
        '  });\n'
        '  document.getElementById(\'currentPage\').textContent = page;\n'
        '  document.getElementById(\'jumpInput\').value = page;\n'
        '  document.getElementById(\'prevBtn\').disabled = (page === 1);\n'
        '  document.getElementById(\'nextBtn\').disabled = (page === totalPages);\n'
        '}\n'
        'function goPage(page) { renderPage(page); }\n'
        'function jumpPage() {\n'
        '  const input = document.getElementById(\'jumpInput\');\n'
        '  let p = parseInt(input.value, 10);\n'
        '  if (isNaN(p) || p < 1) p = 1;\n'
        '  if (p > totalPages) p = totalPages;\n'
        '  renderPage(p);\n'
        '}\n'
        'renderPage(1);\n'
        'const chartDom = document.getElementById(\'chart\');\n'
        'const myChart = echarts.init(chartDom);\n'
        'const option = ' + option_json + ';\n'
        'myChart.setOption(option);\n'
        'window.addEventListener(\'resize\', () => myChart.resize());\n'
        '</script>\n'
        '</body>\n</html>\n'
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(json.dumps({
        "success": True,
        "total": total,
        "file": str(Path(output_path).resolve()),
        "message": f"成功生成图表 {output_path}"
    }, ensure_ascii=False, indent=2))


def check_environment(api_base=API_BASE_URL):
    """检查运行环境是否满足要求，返回结构化 JSON。"""
    results = {}
    script_dir = Path(__file__).parent.resolve()

    # 1. Python 版本
    py_version = sys.version_info
    py_ok = py_version >= (3, 8)
    results["python"] = {
        "ok": py_ok,
        "version": platform.python_version(),
        "message": f"Python {platform.python_version()} {'满足要求 (>=3.8)' if py_ok else '版本过低，需要 >=3.8'}"
    }

    # 2. 核心脚本存在性
    cli_path = script_dir / "insentek_cli.py"
    results["scripts_cli"] = {
        "ok": cli_path.exists(),
        "path": str(cli_path) if cli_path.exists() else None,
        "message": "核心脚本 insentek_cli.py 已找到" if cli_path.exists() else "未找到 insentek_cli.py"
    }

    # 3. Excel 脚本存在性
    excel_path = script_dir / "export_excel.py"
    results["scripts_excel"] = {
        "ok": excel_path.exists(),
        "path": str(excel_path) if excel_path.exists() else None,
        "message": "Excel 脚本 export_excel.py 已找到" if excel_path.exists() else "未找到 export_excel.py（Excel 导出不可用）"
    }

    # 4. openpyxl 依赖
    try:
        import openpyxl
        results["openpyxl"] = {
            "ok": True,
            "version": openpyxl.__version__,
            "message": f"openpyxl {openpyxl.__version__} 已安装，Excel 导出可用"
        }
    except ImportError:
        results["openpyxl"] = {
            "ok": False,
            "message": "openpyxl 未安装，Excel 导出不可用。安装命令: pip install openpyxl"
        }

    # 5. curl 可用性（fallback）
    try:
        subprocess.run(["curl", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        results["curl"] = {
            "ok": True,
            "message": "curl 可用，可作为脚本不可用时的 fallback"
        }
    except (FileNotFoundError, subprocess.CalledProcessError):
        results["curl"] = {
            "ok": False,
            "message": "curl 不可用，建议安装以保证 fallback 能力"
        }

    # 6. API 可达性（不带认证，只检查服务是否在线）
    try:
        req = urllib.request.Request(f"{api_base}/v3/token", method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            # 400 是正常的（缺少参数），说明服务在线
            results["api_reachable"] = {
                "ok": True,
                "status": resp.status,
                "message": f"API 服务可访问（HTTP {resp.status}）"
            }
    except urllib.error.HTTPError as e:
        # 400/401 说明服务在线只是缺少认证参数
        if e.code in (400, 401, 403):
            results["api_reachable"] = {
                "ok": True,
                "status": e.code,
                "message": f"API 服务可访问（HTTP {e.code}，未提供认证参数）"
            }
        else:
            results["api_reachable"] = {
                "ok": False,
                "status": e.code,
                "message": f"API 服务异常（HTTP {e.code}）"
            }
    except Exception as e:
        results["api_reachable"] = {
            "ok": False,
            "message": f"无法连接到 API 服务: {str(e)}"
        }

    # 汇总
    critical_ok = results["python"]["ok"] and results["scripts_cli"]["ok"]
    all_ok = all(r["ok"] for r in results.values())

    output = {
        "success": critical_ok,
        "all_checks_passed": all_ok,
        "checks": results,
        "summary": {
            "critical": "通过" if critical_ok else "未通过",
            "optional": "全部通过" if all_ok else "部分未通过",
            "message": (
                "环境检查通过，所有功能可用。" if all_ok else
                "核心环境满足要求，但部分可选功能不可用。" if critical_ok else
                "核心环境未满足要求，请先安装 Python >=3.8 并确保脚本文件存在。"
            )
        }
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


def cmd_data(args):
    """data 子命令：查询数据并以 JSON 输出到 stdout。"""
    result = query_data(args.token, args.sn, args.range, args.include_params, args.include_nodes)
    if args.dry_run:
        dry_run_summary(result, args.sn, args.range)
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    global API_BASE_URL
    parser = argparse.ArgumentParser(description="Insentek OpenAPI CLI")
    parser.add_argument("--api-base", default=API_BASE_URL, help="API 基础 URL")
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    auth_p = sub.add_parser("auth", help="获取 access token")
    auth_p.add_argument("--appid", required=True)
    auth_p.add_argument("--secret", required=True)

    # devices
    devs_p = sub.add_parser("devices", help="查询设备列表")
    devs_p.add_argument("--token", required=True)
    devs_p.add_argument("--page", type=int, default=1)
    devs_p.add_argument("--limit", type=int, default=20)

    # device
    dev_p = sub.add_parser("device", help="查询设备详情")
    dev_p.add_argument("--token", required=True)
    dev_p.add_argument("--sn", required=True)

    # data
    data_p = sub.add_parser("data", help="查询设备历史数据（含边界检查）")
    data_p.add_argument("--token", required=True)
    data_p.add_argument("--sn", required=True)
    data_p.add_argument("--range", required=True, help="格式: YYYYMMDD,YYYYMMDD")
    data_p.add_argument("--include-params", default=None)
    data_p.add_argument("--include-nodes", default=None)
    data_p.add_argument("--dry-run", action="store_true", help="仅预览数据摘要，不输出全量数据")
    data_p.set_defaults(func=cmd_data)

    # export
    exp_p = sub.add_parser("export", help="导出数据为文件")
    exp_p.add_argument("--token", required=True)
    exp_p.add_argument("--sn", required=True)
    exp_p.add_argument("--range", required=True)
    exp_p.add_argument("--format", choices=["csv", "json", "html"], required=True)
    exp_p.add_argument("--output", required=True)
    exp_p.add_argument("--include-params", default=None)
    exp_p.add_argument("--dry-run", action="store_true", help="仅预览数据摘要，不写入文件")

    # report
    rep_p = sub.add_parser("report", help="生成 HTML 数据报告")
    rep_p.add_argument("--token", required=True)
    rep_p.add_argument("--sn", required=True)
    rep_p.add_argument("--range", required=True)
    rep_p.add_argument("--output", required=True)
    rep_p.add_argument("--include-params", default=None)
    rep_p.add_argument("--dry-run", action="store_true", help="仅预览数据摘要，不生成报告")

    # chart
    chart_p = sub.add_parser("chart", help="生成动态图表 HTML（由 AI 决定图表类型）")
    chart_p.add_argument("--token", required=True)
    chart_p.add_argument("--sn", required=True)
    chart_p.add_argument("--range", required=True)
    chart_p.add_argument("--type", choices=["line", "scatter", "dual"], default="line", help="图表类型")
    chart_p.add_argument("--params", default="", help="要分析的参数，逗号分隔")
    chart_p.add_argument("--title", default="", help="图表标题")
    chart_p.add_argument("--conclusion", default="", help="分析结论文字")
    chart_p.add_argument("--output", required=True)
    chart_p.add_argument("--include-params", default=None)
    chart_p.add_argument("--dry-run", action="store_true", help="仅预览数据摘要，不生成图表")

    # check
    check_p = sub.add_parser("check", help="环境前置检查")
    check_p.add_argument("--api-base", default=API_BASE_URL, help="API 基础 URL")

    args = parser.parse_args()

    API_BASE_URL = args.api_base

    if args.command == "check":
        check_environment(args.api_base)
    elif args.command == "auth":
        authenticate(args.appid, args.secret)
    elif args.command == "devices":
        list_devices(args.token, args.page, args.limit)
    elif args.command == "device":
        get_device(args.token, args.sn)
    elif args.command == "data":
        args.func(args)
    elif args.command == "export":
        if args.format == "csv":
            export_csv(args.token, args.sn, args.range, args.output, args.include_params, args.dry_run)
        elif args.format == "json":
            export_json(args.token, args.sn, args.range, args.output, args.include_params, args.dry_run)
        elif args.format == "html":
            generate_report(args.token, args.sn, args.range, args.output, args.include_params, args.dry_run)
    elif args.command == "report":
        generate_report(args.token, args.sn, args.range, args.output, args.include_params, args.dry_run)
    elif args.command == "chart":
        generate_chart(args.token, args.sn, args.range, args.type, args.params, args.title, args.conclusion, args.output, args.include_params, args.dry_run)


if __name__ == "__main__":
    main()
