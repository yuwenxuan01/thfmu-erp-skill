#!/usr/bin/env python3
"""
东方医学 ERP 数据导出脚本

通过 agent-browser 浏览器会话中的 fetch API 获取数据并导出为 CSV。
也可以使用 --sid 参数独立运行（需要先获取 session cookie）。

使用方法:
    # 生成 agent-browser eval 命令
    python export_data.py --doctype "Sales Invoice" --fields "name,customer,grand_total" --generate-js

    # 使用 cookie 独立导出
    python export_data.py --doctype "Item" --sid "your-session-id" --output items.csv
"""

import argparse
import csv
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path


BASE_URL = "https://c.thfmu.com"


def build_url(doctype, fields=None, filters=None, limit=0, start=0, order_by=None):
    """构建 API 查询 URL"""
    params = {"limit_page_length": str(limit), "limit_start": str(start)}
    if fields:
        params["fields"] = json.dumps(fields)
    if filters:
        params["filters"] = json.dumps(filters)
    if order_by:
        params["order_by"] = order_by
    encoded = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    doctype_encoded = urllib.parse.quote(doctype, safe="")
    return f"{BASE_URL}/api/resource/{doctype_encoded}?{encoded}"


def fetch_data(url, sid=None):
    """通过 API 获取数据"""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    if sid:
        req.add_header("Cookie", f"sid={sid}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def export_to_csv(data, fields, output_path):
    """导出数据到 CSV"""
    if not data:
        print("警告：没有数据可导出")
        return
    if fields:
        fieldnames = [f.strip() for f in fields]
    else:
        fieldnames = list(data[0].keys())
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    print(f"已导出 {len(data)} 条记录到 {path}")


def export_to_json(data, output_path):
    """导出数据到 JSON"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已导出 {len(data)} 条记录到 {path}")


def generate_js_fetch(doctype, fields=None, filters=None, limit=0, start=0, order_by=None):
    """生成可在 agent-browser eval 中使用的 JavaScript fetch 代码"""
    params = {"limit_page_length": str(limit), "limit_start": str(start)}
    if fields:
        params["fields"] = json.dumps(fields)
    if filters:
        params["filters"] = json.dumps(filters)
    if order_by:
        params["order_by"] = order_by
    encoded = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    doctype_encoded = urllib.parse.quote(doctype, safe="")
    url = f"/api/resource/{doctype_encoded}?{encoded}"
    js = f"fetch('{url}', {{headers: {{'Accept': 'application/json'}}}}).then(r => r.json()).then(d => JSON.stringify(d))"
    return js


def main():
    parser = argparse.ArgumentParser(
        description="东方医学 ERP 数据导出工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python export_data.py --doctype "Sales Invoice" --fields "name,customer,grand_total" --filters '[["status","=","Paid"]]' --output paid.csv
  python export_data.py --doctype "Item" --output items.json --format json
  python export_data.py --doctype "Sales Invoice" --fields "name,customer" --generate-js
  python export_data.py --doctype "Item" --sid "your-session-id" --output items.csv"""
    )
    parser.add_argument("--doctype", required=True, help="DocType 名称")
    parser.add_argument("--fields", help="导出字段，逗号分隔")
    parser.add_argument("--filters", help="过滤条件，JSON 格式")
    parser.add_argument("--limit", type=int, default=0, help="每页记录数（0=全部）")
    parser.add_argument("--start", type=int, default=0, help="分页偏移")
    parser.add_argument("--order-by", help="排序字段")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="输出格式")
    parser.add_argument("--sid", help="Session ID cookie")
    parser.add_argument("--generate-js", action="store_true", help="生成 agent-browser eval 代码")
    args = parser.parse_args()

    fields_list = [f.strip() for f in args.fields.split(",")] if args.fields else None
    filters_list = json.loads(args.filters) if args.filters else None

    if args.generate_js:
        js = generate_js_fetch(args.doctype, fields_list, filters_list, args.limit, args.start, args.order_by)
        print("=== agent-browser eval ===")
        print(f'agent-browser eval "{js}"')
        print()
        print("=== JavaScript ===")
        print(js)
        return

    if not args.sid:
        print("错误：独立运行需要 --sid 参数")
        print("提示：使用 --generate-js 生成可在 agent-browser 中执行的代码")
        sys.exit(1)

    url = build_url(args.doctype, fields_list, filters_list, args.limit, args.start, args.order_by)
    print(f"正在获取: {args.doctype}")
    result = fetch_data(url, sid=args.sid)

    if "exception" in result:
        print(f"错误: {result.get('exc_type', 'Unknown')}")
        print(f"消息: {result.get('_error_message', '')}")
        sys.exit(1)

    data = result.get("data", [])
    print(f"获取到 {len(data)} 条记录")

    if args.output:
        if args.format == "csv":
            export_to_csv(data, fields_list, args.output)
        else:
            export_to_json(data, args.output)
    else:
        if args.format == "json":
            print(json.dumps(data, ensure_ascii=False, indent=2))
        elif data:
            fn = fields_list or list(data[0].keys())
            writer = csv.DictWriter(sys.stdout, fieldnames=fn, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)


if __name__ == "__main__":
    main()
