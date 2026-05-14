# 东方医学 ERP API 完整参考

## 基础信息

- **Base URL**: `https://c.thfmu.com`
- **API Prefix**: `/api/resource/`
- **框架**: Frappe (ERPNext)
- **认证**: Cookie-based Session
- **数据格式**: JSON

## 认证机制

系统使用 Cookie 认证。登录后浏览器会自动携带 `sid` cookie。

### Cookie 字段

| Cookie | 说明 |
|--------|------|
| `sid` | Session ID，登录后由服务器设置 |
| `user_id` | 当前登录用户 ID |
| `system_user` | 是否为系统用户 |

### Session 有效期

默认 session 有效期较长，但长时间不活动会过期。过期后需要重新登录。

## API 端点

### 1. 列表查询 (GET)

```
GET /api/resource/{DocType}
```

**参数：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `limit_page_length` | int | 每页记录数，0 表示全部 | 20 |
| `limit_start` | int | 分页起始偏移量 | 0 |
| `fields` | JSON array | 返回字段列表 | 全部字段 |
| `filters` | JSON array | 过滤条件 | 无 |
| `order_by` | string | 排序字段和方向 | `name asc` |
| `group_by` | string | 分组字段 | 无 |
| `as_dict` | bool | 返回字典格式 | true |
| `debug` | bool | 调试模式 | false |

**fields 参数格式：**

URL 编码的 JSON 数组字符串：
```
fields=["name", "customer", "grand_total"]
```

URL 编码后：
```
fields=%5B%22name%22%2C%22customer%22%2C%22grand_total%22%5D
```

**filters 参数格式：**

URL 编码的 JSON 数组，支持多种操作符：

```json
// 等于
[["status", "=", "Paid"]]

// 不等于
[["status", "!=", "Cancelled"]]

// 大于
[["grand_total", ">", 100]]

// 小于等于
[["grand_total", "<=", 1000]]

// IN (属于)
[["status", "in", ["Paid", "Submitted"]]]

// LIKE (模糊匹配)
[["customer", "like", "%THO%"]]

// 多条件 AND
[["status", "=", "Paid"], ["posting_date", ">", "2025-01-01"]]
```

**响应格式：**

```json
{
  "data": [
    {"name": "ACC-SINV-2026-00033", "customer": "零售-宁波tho", "grand_total": 1382.31}
  ]
}
```

### 2. 单条记录查询 (GET)

```
GET /api/resource/{DocType}/{record_id}
```

**响应格式：**
```json
{
  "data": {
    "name": "ACC-SINV-2026-00033",
    "owner": "sh@thfmu.com",
    "creation": "2026-05-14 16:43:39.146521",
    "docstatus": 1,
    "customer": "零售-宁波tho",
    "grand_total": 1382.31
  }
}
```

### 3. 计数查询 (GET)

```
GET /api/resource/{DocType}?limit_page_length=0&fields=["name"]
```

返回的 `data` 数组长度即为记录总数。

### 4. RPC 调用 (POST)

```
POST /api/method/{method_path}
Content-Type: application/json
```

**示例 - frappe.client.get_list：**
```json
POST /api/method/frappe.client.get_list
{
  "doctype": "Sales Invoice",
  "fields": ["name", "customer", "grand_total"],
  "filters": [["status", "=", "Paid"]],
  "limit_page_length": 100,
  "order_by": "posting_date desc"
}
```

**示例 - frappe.client.get_count：**
```json
POST /api/method/frappe.client.get_count
{
  "doctype": "Sales Invoice",
  "filters": [["status", "=", "Paid"]]
}
```

### 5. 搜索 (GET)

```
GET /api/resource/{DocType}?filters=[["name", "like", "%关键词%"]]
```

## 错误处理

### 权限错误
```json
{
  "exception": "frappe.exceptions.PermissionError",
  "exc_type": "PermissionError",
  "_error_message": "无权限操作单据类型"
}
```

### 不存在错误
```json
{
  "errors": [{"type": "DoesNotExistError"}]
}
```

### Session 过期
如果返回登录页面 HTML 而非 JSON，说明 session 已过期，需要重新登录。

## agent-browser 调用技巧

### 技巧 1：直接 fetch
```javascript
fetch('/api/resource/Item?limit_page_length=20', {
  headers: {'Accept': 'application/json'}
}).then(r => r.json()).then(d => JSON.stringify(d))
```

### 技巧 2：POST 调用 RPC
```javascript
fetch('/api/method/frappe.client.get_count', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
  body: JSON.stringify({doctype: 'Sales Invoice', filters: [['status', '=', 'Paid']]})
}).then(r => r.json()).then(d => JSON.stringify(d))
```

### 技巧 3：链式数据处理
```javascript
fetch('/api/resource/Sales%20Invoice?limit_page_length=0&fields=%5B%22status%22%2C%22grand_total%22%5D', {
  headers: {'Accept': 'application/json'}
}).then(r => r.json()).then(d => {
  const result = {};
  d.data.forEach(i => {
    if (!result[i.status]) result[i.status] = {count: 0, total: 0};
    result[i.status].count++;
    result[i.status].total += i.grand_total;
  });
  return JSON.stringify(result);
})
```

### 技巧 4：截断长输出
```javascript
fetch('/api/resource/Item?limit_page_length=0', {
  headers: {'Accept': 'application/json'}
}).then(r => r.json()).then(d => JSON.stringify(d).substring(0, 3000))
```

### 技巧 5：base64 编码避免引号问题
```bash
$js = 'fetch("/api/resource/Item?limit_page_length=5").then(r => r.json()).then(d => JSON.stringify(d))'
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($js))
agent-browser eval -b $b64
```

## URL 编码速查

| 字符 | 编码 |
|------|------|
| 空格 | `%20` |
| `[` | `%5B` |
| `]` | `%5D` |
| `"` | `%22` |
| `,` | `%2C` |
| `=` | `%3D` |
| `&` | `%26` |

## DocType 名称编码示例

| DocType | 编码后 |
|---------|--------|
| `Sales Invoice` | `Sales%20Invoice` |
| `Purchase Order` | `Purchase%20Order` |
| `Stock Entry` | `Stock%20Entry` |
| `Payment Entry` | `Payment%20Entry` |
| `Delivery Note` | `Delivery%20Note` |
| `Purchase Invoice` | `Purchase%20Invoice` |
| `Expense Claim` | `Expense%20Claim` |
| `Serial No` | `Serial%20No` |
| `Material Request` | `Material%20Request` |
| `Stock Reconciliation` | `Stock%20Reconciliation` |
| `Daily Work Summary` | `Daily%20Work%20Summary` |
| `Request for Quotation` | `Request%20for%20Quotation` |
| `Supplier Quotation` | `Supplier%20Quotation` |
