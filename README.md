# thfmu-erp-skill

东方医学 ERP 系统（https://c.thfmu.com/）API 交互 Skill，基于 Frappe 框架，用于通过 API 批量查询、导出和管理业务数据。

## 功能

- 批量查询销售发票、物料、项目、任务等业务数据
- 支持字段选择、条件过滤、分页、排序
- 统计分析（按状态汇总、按客户汇总、按月汇总等）
- 数据导出为 CSV / JSON

## 安装

### 前提条件

- 已安装 [SOLO](https://solo.ai) 桌面应用
- 拥有东方医学 ERP 系统账号（https://c.thfmu.com/）

### 安装步骤

1. 下载或 clone 本仓库：
   `ash
   git clone https://github.com/yuwenxuan01/thfmu-erp-skill.git
   `

2. 将 `thfmu-erp` 文件夹复制到 SOLO 的 skills 目录：
   `
   C:\Users\{你的用户名}\.trae-cn\skills\thfmu-erp\
   `

   最终目录结构：
   `
   .trae-cn\skills\thfmu-erp\
   ├── SKILL.md                    # 技能定义文件（核心）
   ├── references\
   │   └── api-reference.md        # API 完整参考文档
   └── scripts\
       └── export_data.py          # Python 数据导出脚本
   `

3. 重启 SOLO，skill 会自动加载。

## 快速开始

### 1. 登录 ERP 系统

在 SOLO 中执行以下命令登录：

`ash
agent-browser open https://c.thfmu.com/login
agent-browser snapshot -i
agent-browser eval "document.getElementById('login_email').value = '你的邮箱'"
agent-browser eval "document.getElementById('login_password').value = '你的密码'"
agent-browser eval "document.querySelector('button[type=""submit""]').click()"
agent-browser wait --url "**/app/**"
`

### 2. 查询数据

登录成功后，通过浏览器内的 fetch API 调用：

`ash
# 查询物料列表
agent-browser eval "fetch('/api/resource/Item?limit_page_length=20', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"

# 查询已付款的销售发票
agent-browser eval "fetch('/api/resource/Sales%20Invoice?limit_page_length=100&fields=%5B%22name%22%2C%22customer%22%2C%22grand_total%22%2C%22posting_date%22%5D&filters=%5B%5B%22status%22%2C%22%3D%22%2C%22Paid%22%5D%5D', {headers: {'Accept': 'application/json'}}).then(r => r.json()).then(d => JSON.stringify(d))"
`

### 3. 触发关键词

在 SOLO 对话中提到以下关键词会自动触发此 skill：

- 查ERP、导出数据、查库存、查发票、查物料
- ERP API、东方医学数据、批量获取ERP、Frappe API

## 可用数据模块

| 模块 | DocType | 说明 |
|------|---------|------|
| 销售 | Sales Invoice, Customer, Quotation, Sales Order, Delivery Note | 发票、客户、报价、订单 |
| 采购 | Purchase Order, Purchase Invoice, Supplier, Material Request | 采购订单、供应商 |
| 库存 | Item, Warehouse, Stock Entry, Brand, UOM | 物料、仓库、库存 |
| 项目 | Project, Task, Meetings, Proposals | 项目、任务、会议 |
| 财务 | Journal Entry, Payment Entry, Bank Account | 日记账、付款 |
| 人事 | Employee, Department, Expense Claim, Salary Slip | 员工、部门、报销 |

> 注意：不同账号权限不同，可访问的模块可能有差异。

## API 参数速查

| 参数 | 说明 | 示例 |
|------|------|------|
| limit_page_length | 每页数量（0=全部） | limit_page_length=100 |
| fields | 返回字段（URL编码JSON） | fields=%5B%22name%22%2C%22customer%22%5D |
| filters | 过滤条件（URL编码JSON） | filters=%5B%5B%22status%22%2C%22%3D%22%2C%22Paid%22%5D%5D |
| order_by | 排序 | order_by=posting_date%20desc |

## 注意事项

1. **Cookie 时效**：登录 session 会过期，长时间不用需重新登录
2. **URL 编码**：DocType 中的空格需编码为 %20（如 Sales%20Invoice）
3. **PowerShell**：避免用 && 链接命令，用分号 ; 代替
4. **引号问题**：复杂 JS 表达式建议用 base64 编码：agent-browser eval -b <base64>

## 文件说明

| 文件 | 说明 |
|------|------|
| SKILL.md | 技能定义文件，包含触发条件、使用模式、DocType 速查表 |
| references/api-reference.md | API 完整参考：端点、参数、错误处理、编码速查 |
| scripts/export_data.py | Python 导出工具，支持 CSV/JSON 输出 |

## License

MIT
