---
name: thfmu-erp
description: 东方医学 ERP 系统 API 交互技能。基于 Frappe 框架，用于通过 API 批量查询、导出和管理东方医学（c.thfmu.com）的业务数据。Use when the user needs to query ERP data, export records, check inventory, view sales invoices, manage projects/tasks, or any data operation related to the 东方医学 ERP system. Triggers include "查ERP", "导出数据", "查库存", "查发票", "查物料", "ERP API", "东方医学数据", "批量获取ERP", "Frappe API".
allowed-tools: Bash(agent-browser:*), Bash(python:*), Bash(powershell:*), Bash(curl:*), Read, Write, Glob, Grep, RunCommand
---

# 东方医学 ERP 系统 API 交互技能

## 概述

本技能用于与东方医学 ERP 系统（https://c.thfmu.com/）进行 API 交互。该系统基于 **Frappe 框架**，提供完整的 REST API，支持批量查询、过滤、分页、字段选择等操作。

**系统信息：**
- 地址：https://c.thfmu.com/
- 框架：Frappe / ERPNext
- 认证方式：Cookie-based Session（通过浏览器登录获取）

## 核心工作流程

### 第一步：认证（登录）

系统使用 Cookie 认证，必须先通过浏览器登录获取 session cookie。

**方法 A：通过 agent-browser 登录（推荐）**

```bash
# 1. 打开登录页
agent-browser open https://c.thfmu.com/login

# 2. 获取页面快照找到表单元素
agent-browser snapshot -i

# 3. 填写账号密码（使用 eval + getElementById 最可靠）
agent-browser eval "document.getElementById('login_email').value = '912147659@qq.com'"
agent-browser eval "document.getElementById('login_password').value = 'PASSWORD'"
agent-browser eval "document.querySelector('button[type=\"submit\"]').click()"

# 4. 等待登录完成
agent-browser wait --url "**/app/**"
```

**方法 B：使用已保存的 session**

```bash
# 如果之前已登录并保存了 session
agent-browser --session-name thfmu-erp open https://c.thfmu.com/app/home
```

**方法 C：使用持久化 profile**

```bash
# 首次登录后保存状态
agent-browser state save thfmu-auth.json

# 后续使用
agent-browser --state thfmu-auth.json open https://c.thfmu.com/app/home
```

### 第二步：API 调用

登录后，通过浏览器内的 `fetch()` 调用 API（自动携带 cookie）。

#### 基础查询格式

```
GET /api/resource/{DocType}?参数
```

#### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `limit_page_length` | 分页大小（0=全部） | `limit_page_length=100` |
| `limit_start` | 分页偏移 | `limit_start=20` |
| `fields` | 返回字段（URL编码JSON数组） | `fields=["name","customer"]` |
| `filters` | 过滤条件（URL编码JSON数组） | `filters=[["status","=","Paid"]]` |
| `order_by` | 排序 | `order_by=creation desc` |
| `group_by` | 分组 | `group_by=customer` |

#### 在 agent-browser 中调用 API

```bash
# 列表查询
agent-browser eval "fetch('/api/resource/Item?limit_page_length=20', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"

# 带字段和过滤
agent-browser eval "fetch('/api/resource/Sales%20Invoice?limit_page_length=100&fields=%5B%22name%22%2C%22customer%22%2C%22grand_total%22%5D&filters=%5B%5B%22status%22%2C%22%3D%22%2C%22Paid%22%5D%5D', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"

# 单条记录详情
agent-browser eval "fetch('/api/resource/Sales%20Invoice/ACC-SINV-2026-00033', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"
```

> **注意**：`fields` 和 `filters` 参数中的 `[` 需要编码为 `%5B`，`]` 编码为 `%5D`，`"` 编码为 `%22`。

#### 使用 Python 脚本批量导出

对于大量数据导出，推荐使用 Python 脚本：

```bash
python scripts/export_data.py --doctype "Sales Invoice" --fields "name,customer,grand_total,status,posting_date" --filters '[["status","=","Paid"]]' --output sales_paid.csv
```

详见 [scripts/export_data.py](scripts/export_data.py)。

### 第三步：数据处理与导出

获取到 JSON 数据后，可以：
- 直接解析 JSON 进行分析
- 导出为 CSV/Excel
- 生成数据报表

## 可用 DocType 速查表

### 销售模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Customer` | 客户 | name, customer_name, customer_group, territory |
| `Lead` | 线索 | name, lead_name, status, source |
| `Quotation` | 报价单 | name, customer, grand_total, status |
| `Sales Order` | 销售订单 | name, customer, grand_total, status |
| `Sales Invoice` | 销售发票 | name, customer, grand_total, status, posting_date |
| `Delivery Note` | 交付单 | name, customer, status |
| `POS Invoice` | POS发票 | name, customer, grand_total |
| `Pricing Rule` | 定价规则 | name, title, status |

### 采购模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Supplier` | 供应商 | name, supplier_name |
| `Purchase Order` | 采购订单 | name, supplier, grand_total, status |
| `Purchase Invoice` | 采购发票 | name, supplier, grand_total, status |
| `Purchase Receipt` | 采购收货单 | name, supplier, status |
| `Material Request` | 物料需求 | name, material_request_type, status |
| `Request for Quotation` | 询价单 | name, supplier, status |
| `Supplier Quotation` | 供应商报价 | name, supplier, grand_total |

### 库存模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Item` | 物料 | name, item_name, item_group, stock_uom, standard_rate |
| `Warehouse` | 仓库 | name, warehouse_name, company |
| `Stock Entry` | 库存分录 | name, purpose, status |
| `Stock Reconciliation` | 库存盘点 | name, purpose, status |
| `Serial No` | 序列号 | name, item_code, status |
| `Batch` | 批次 | name, item, batch_qty |
| `Brand` | 品牌 | name, brand_name |
| `UOM` | 计量单位 | name, uom_name |

### 项目管理

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Project` | 项目 | name, project_name, status |
| `Task` | 任务 | name, subject, status, priority, project |
| `Project Type` | 项目类型 | name, project_type_name |
| `Meetings` | 会议 | name, title, status, date |
| `Proposals` | 提案 | name, status |
| `POA` | 授权委托书 | name, status |
| `Signing of MAA` | 章程签署件 | name, status |

### 财务模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Journal Entry` | 日记账分录 | name, voucher_type, total_debit, total_credit |
| `Payment Entry` | 付款分录 | name, payment_type, paid_amount, party |
| `Bank Account` | 银行账户 | name, account_name, bank |
| `Account` | 会计科目 | name, account_name, account_type |
| `Cost Center` | 成本中心 | name, cost_center_name |
| `Tax Category` | 税类别 | name, title |
| `Price List` | 价格表 | name, price_list_name, currency |

### HR 模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Employee` | 员工 | name, employee_name, department, designation |
| `Department` | 部门 | name, department_name |
| `Designation` | 职位 | name, designation_name |
| `Expense Claim` | 费用报销 | name, employee, total_claimed_amount, status |
| `Employee Advance` | 员工预支 | name, employee, advance_amount, status |
| `Salary Slip` | 工资条 | name, employee, gross_pay, net_pay |
| `Leave Application` | 请假申请 | name, employee, leave_type, status |
| `Daily Work Summary` | 每日工作总结 | name, user |

### 生产模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `BOM` | 物料清单 | name, item, quantity, is_active |
| `Work Order` | 工单 | name, production_item, qty, status |
| `Job Card` | 作业卡 | name, work_order, status |
| `Production Plan` | 生产计划 | name, status |

### 资产模块

| DocType | 说明 | 常用字段 |
|---------|------|---------|
| `Asset` | 资产 | name, asset_name, asset_category, status |
| `Asset Category` | 资产类别 | name, asset_category_name |

## 常见使用模式

### 模式 1：快速查询单个模块数据

```bash
# 1. 确保已登录
agent-browser --session-name thfmu-erp open https://c.thfmu.com/app/home
agent-browser wait --load networkidle

# 2. 查询数据
agent-browser eval "fetch('/api/resource/Item?limit_page_length=50&fields=%5B%22name%22%2C%22item_name%22%2C%22item_group%22%2C%22standard_rate%22%5D', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"
```

### 模式 2：带条件过滤查询

```bash
# 查询已付款的销售发票
agent-browser eval "fetch('/api/resource/Sales%20Invoice?limit_page_length=0&fields=%5B%22name%22%2C%22customer%22%2C%22grand_total%22%2C%22posting_date%22%5D&filters=%5B%5B%22status%22%2C%22%3D%22%2C%22Paid%22%5D%5D&order_by=posting_date%20desc', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"
```

### 模式 3：分页获取全量数据

```bash
# 第一页
agent-browser eval "fetch('/api/resource/Item?limit_page_length=100&limit_start=0', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"

# 第二页
agent-browser eval "fetch('/api/resource/Item?limit_page_length=100&limit_start=100', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"
```

### 模式 4：获取单条记录详情

```bash
agent-browser eval "fetch('/api/resource/Sales%20Invoice/ACC-SINV-2026-00033', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"
```

### 模式 5：使用 Python 脚本批量导出到 CSV

```bash
# 导出销售发票到 CSV
python scripts/export_data.py --doctype "Sales Invoice" --fields "name,customer,grand_total,status,posting_date" --filters '[["status","=","Paid"]]' --output paid_invoices.csv

# 导出物料清单到 CSV
python scripts/export_data.py --doctype "Item" --fields "name,item_name,item_group,stock_uom,standard_rate" --output items.csv
```

### 模式 6：统计数据

```bash
# 统计各状态的销售发票数量
agent-browser eval "fetch('/api/resource/Sales%20Invoice?limit_page_length=0&fields=%5B%22status%22%5D', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => { const counts = {}; d.data.forEach(i => counts[i.status] = (counts[i.status]||0)+1); return JSON.stringify(counts); })"

# 计算已付款发票总额
agent-browser eval "fetch('/api/resource/Sales%20Invoice?limit_page_length=0&fields=%5B%22grand_total%22%5D&filters=%5B%5B%22status%22%2C%22%3D%22%2C%22Paid%22%5D%5D', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => { const total = d.data.reduce((s,i) => s+i.grand_total, 0); return JSON.stringify({count: d.data.length, total: total}); })"
```

## 注意事项

1. **认证时效**：Cookie session 有时效限制，长时间不操作可能需要重新登录
2. **权限限制**：当前用户（912147659@qq.com）无权访问 DocType、Role、Workflow 等系统管理类表
3. **URL 编码**：DocType 名称中的空格必须编码为 `%20`（如 `Sales%20Invoice`）
4. **fields/filters 编码**：JSON 数组参数必须进行 URL 编码
5. **分页**：大量数据时建议分页获取，避免单次请求超时
6. **PowerShell 兼容**：在 PowerShell 中使用 agent-browser 时，避免使用 `&&` 链接命令，改用分号 `;`
7. **eval 引号**：复杂的 JavaScript 表达式建议使用 `agent-browser eval -b <base64>` 避免引号转义问题

## 详细参考

- [API 完整参考文档](references/api-reference.md)
- [数据导出脚本](scripts/export_data.py)
