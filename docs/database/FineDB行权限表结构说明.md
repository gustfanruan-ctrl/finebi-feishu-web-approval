# 行权限相关接口与 FineDB 表字段说明

- 版本：2026-11-23
- 用途：给方案设计（fable）使用；涵盖 FineBI 行权限 OpenAPI、FineDB `fine_pack_filter` 表、字段结构、已实测行为与设计约束
- 依据：`docs/finebi/开放平台 FineBI接口（对外）.md`、`docs/design/授权页改版说明.md`、项目现有实现（`src/executor/finebi/client.py`、`src/executor/web/finedb.py`、`src/executor/services/grant.py`、`src/executor/web/service.py`）、客户环境只读实测
- 不含客户业务数据、凭证与密钥

---

## 0. 一句话结论

- **写/查行权限必须走开放平台接口**：用户 / 角色 / 部门职务三套 set/get，入参是“数据集 GUID + 行权限 filter”。
- **set 是“全量覆盖”**：要给某用户追加规则，必须先 get 当前规则、合并、再整体写回。
- **get 返回的是数字 `filterType` 的 JSON 串**，set 入参用的是 `and/or/strIn/strNotIn` 的 JSON 对象，两者需要转换。
- **“数据集是否开了行权限”没有单接口**：只能按主体（角色/部门/用户）批量查，或直接读 FineDB `fine_pack_filter`。
- **全量候选值（几百个店铺/枚举）API 拿不全**：根部门全局规则的 `assist` 只存在 FineDB；现有实现是“API 查用户已有规则 + FineDB 全局 `assist` 合并”。
- FineDB 里存在 **`filterType=11` 的动态规则**（按登录用户/角色属性过滤），接口文档未定义，不能当普通值列表复制或反序列化。

---

## 1. OpenAPI 基础信息

- 基础地址：`http://{host}:{port}/webroot/decision/sp/client/api`
- 认证 Header：`clientId: <开放平台应用ID>`、`secret: <密钥>`；可选 `decUser` query 参数
- 所有接口为 `POST`，`Content-Type: application/json`
- 批量接口的 body 是**数组**，响应也是数组；单项失败时 `item.status=false`，项目客户端会抛 `BATCH` 异常

### 1.1 行权限接口清单

| 用途 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 设置用户行权限 | POST | `/v3/bi/authority/row/filter/user` | **全量覆盖**该用户在该表上的全部规则 |
| 查询用户行权限 | POST | `/v3/bi/authority/row/filter/user/get` | 返回 JSON 字符串；无规则返回空字符串 |
| 设置角色行权限 | POST | `/v3/bi/authority/row/filter/role` | 全量覆盖该角色规则 |
| 查询角色行权限 | POST | `/v3/bi/authority/row/filter/role/get` | 同上 |
| 设置部门/职务行权限 | POST | `/v3/bi/authority/row/filter/depost` | body 需要 `department` + `position` |
| 查询部门/职务行权限 | POST | `/v3/bi/authority/row/filter/depost/get` | 同上 |
| 查询角色列表 | GET | `/v3/role?role=&exact=false` | 用于主体枚举 |
| 查询部门/职务树 | GET | `/v3/department?department=[]` | 返回扁平节点（department / position），含 id/pId/name |
| 查询用户列表 | GET | `/v3/user?page=&count=` | 返回 `{total, items:[{id,username,realName,enable}]}` |
| 查询数据集字段 | GET | `/v3/bi/table/info?tables=[...]` | 返回 `fields[].fieldId/name/transferName`，用于构造 fieldId |

### 1.2 请求/响应示例

**设置用户行权限**

```json
POST /v3/bi/authority/row/filter/user
[
  {
    "user": "test",
    "tableName": "<id>",
    "filter": {
      "type": "or",
      "filterValue": [
        {
          "type": "strIn",
          "fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
          "filterValue": ["A1"]
        },
        {
          "type": "strIn",
          "fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
          "filterValue": ["B"]
        }
      ]
    }
  }
]
```

```json
{"data":[{"status":true,"data":"success"}]}
```

**查询用户行权限**

```json
POST /v3/bi/authority/row/filter/user/get
[{"user":"test","tableName":"<id>"}]
```

有规则时：

```json
{
  "data": [{
    "status": true,
    "data": "{\"id\":\"737968e152a74190\",\"filterType\":34,\"filterValue\":[{\"id\":\"562a329931644711\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"be7b0dc4072b46f6\",\"filterType\":12,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
  }]
}
```

无规则时：

```json
{"data":[{"status":true,"data":""}]}
```

**角色**：`role` 字段替代 `user`；**部门职务**：`department` + `position` 替代 `user`。

### 1.3 字段/结构说明

`filter`（set 入参）节点类型：

| type | 含义 | 子节点 |
| --- | --- | --- |
| `or` | 组间并集 | `filterValue` 数组，元素为条件或 `and` 组 |
| `and` | 组内交集 | `filterValue` 数组，元素为 `strIn/strNotIn` 条件 |
| `strIn` | 字段值属于列表 | `fieldId` + `filterValue`（字符串数组） |
| `strNotIn` | 字段值不属于列表 | 同上 |

`filter`（get 返回）数字 `filterType` 映射（文档明确给出）：

| filterType | 含义 |
| --- | --- |
| 34 | and |
| 35 | or |
| 10 | strIn |
| 12 | strNotIn |
| **11（实测出现，文档未定义）** | 动态规则：如“字段 = 登录用户所在角色/登录用户属性”，`filterValue` 可能是角色 ID、`..._REALNAME` 之类，不是固定值列表 |

单条件 get 叶子示例：

```json
{"filterType":10,"fieldId":"表GUID_字段编码","filterValue":{"type":1,"value":["A1"],"assist":["A1","A2"]}}
```

- `value`：当前已选值；
- `assist`：该规则可选的候选值（仅部分规则返回，且**根部门全局规则拿不到**）。

### 1.4 已实测的批量能力与耗时

| 查询 | 客户环境规模 | 单次批量 | 耗时（参考） |
| --- | --- | --- | --- |
| 角色行权限 get | 19 个角色 | 19 个 item 一次请求 | ~0.1s |
| 部门/职务行权限 get | 178 个部门 + 6 个职务 | 178 个 item 一次请求 | ~0.42s |
| 用户行权限 get | 565 个用户 | 565 个 item 一次请求 | ~1.24s |

结论：单数据集“是否有行权限”约 3 类批量请求、2 秒左右；但官方未承诺批量上限，生产实现建议按 500/批分块并缓存。

---

## 2. FineDB `fine_pack_filter` 表

### 2.1 连接与只读约定

- 项目 `.env`：`FINE_DB_HOST/PORT/USER/PASSWORD/NAME`（FineDB MySQL，默认库 `finedb`）
- 仅执行 `SELECT`；不要写 FineDB
- 远端偶发 `Lost connection (2013/2006)`，项目已有建连/查询重试与本地缓存兜底

### 2.2 已知字段（项目代码在用的列）

| 字段 | 含义 | 备注 |
| --- | --- | --- |
| `tableId` | 数据集 GUID（数据集原始名） | 如 `<id>`；**不是显示名** |
| `enable` | 是否启用 | 只统计 `enable=1` |
| `roleType` | 主体类型 | 实测：`3` = 用户级规则；`1` = 角色/全局规则（如 `decision-dep-role-root`） |
| `roleId` | 主体 ID | `roleType=3` 时是 `fine_user.id`；全局规则下可能是角色 ID/`decision-dep-role-root` |
| `filter` | 行权限 JSON | 可能是 JSON 字符串，也可能被二次编码（需要 parse 两次） |
| `departmentId` / `postId` | 部门/职务 ID | 设计记录显示根部门全局规则这两个字段为空；以服务器 `DESCRIBE` 为准 |

> `roleType` 其他取值（角色/部门职务/岗位）与 `roleId/departmentId/postId` 的准确对应关系，请在服务器执行 `DESCRIBE fine_pack_filter` 与 `SELECT DISTINCT roleType` 后确认，再写进方案；不要仅凭接口文档推断。

### 2.3 `filter` JSON 结构

从 FineDB 读出的 `filter` 是**集合格式**（不是 get 接口的数字格式），典型字段：

```json
{
  "id": "1961f6c01f217d5a",
  "engineType": "spider",
  "fieldName": "示例数据集.示例字段",
  "fieldIdType": 0,
  "fieldId": "c80d..._[56e2][961f][4e3b][7ba1]",
  "fieldFormula": {"engineType": "spider"},
  "fieldFormulaType": 16,
  "filterType": 11,
  "filterValueType": 0,
  "filterValue": "5a7e4fe2ff764ae195bed4f1e3c..."
}
```

- `filterType=10/12` 时，`filterValue` 常为 `{"value":[...],"assist":[...]}`；`assist` 是候选值全集；
- `filterType=11` 时，`filterValue` 直接是角色 ID / `..._REALNAME` 等动态引用；
- `fieldId` 是 `<tableGUID>_<字段名编码>`；字段编码规则如中文按 `[9500][552e]` 形式转义，必须从 `/v3/bi/table/info` 或已有规则里取，不要手拼。

### 2.4 常用查询

```sql
-- 1) 数据集是否配置了行权限（按主体类型计数）
SELECT roleType, COUNT(*) AS cnt
FROM fine_pack_filter
WHERE tableId = %s AND enable = 1
GROUP BY roleType;

-- 2) 列出该数据集所有启用规则
SELECT roleType, roleId, departmentId, postId, filter
FROM fine_pack_filter
WHERE tableId = %s AND enable = 1;

-- 3) 某用户在该数据集上的用户级规则
SELECT filter
FROM fine_pack_filter
WHERE tableId = %s AND enable = 1 AND roleType = 3 AND roleId = (
  SELECT id FROM fine_user WHERE username = %s LIMIT 1
) LIMIT 1;

-- 4) 角色/全局规则里的候选值 assist（全量枚举来源）
SELECT filter
FROM fine_pack_filter
WHERE tableId = %s AND enable = 1 AND roleType <> 3;

-- 5) 用户名 → fine_user.id
SELECT id, username FROM fine_user WHERE username = %s LIMIT 1;

-- 6) 探查 schema（首次接入时执行）
SHOW TABLES LIKE '%filter%';
DESCRIBE fine_pack_filter;
SELECT roleType, COUNT(*) FROM fine_pack_filter GROUP BY roleType;
SELECT roleType, roleId, departmentId, postId
FROM fine_pack_filter WHERE tableId = %s AND enable = 1 LIMIT 20;
```

辅助表（项目已使用/目录中出现）：

- `fine_user`：`id`、`username`、`mobile` 等；用户名 ↔ 用户 ID 映射；
- `fine_feishu_user_relation`：飞书 user_id ↔ FineBI 用户名（与行权限无直接关系）；
- `fine_user_role_middle`：用户-角色关系（`userId/roleId/roleType`），可用于角色主体解析；
- 角色/部门名称表以 `SHOW TABLES` 为准（项目未强依赖，名称建议走平台 API）。

### 2.5 重要限制

1. `tableId` 必须是 GUID/原始名；传显示名会查不到。
2. `filter` 可能二次编码；解析失败应记录原始值，不要静默当空规则。
3. 全局/根部门规则（`roleType=1`，如 `decision-dep-role-root`）**无法通过开放平台 depost/get 寻址**（实测 `decision-dep-root` 会报 NPE / department not exist），只能读 FineDB。
4. 不同 FineBI 版本字段可能变化；首次接入务必 `DESCRIBE` 并做兼容判断（缺列时降级到 API 方案）。

---

## 3. 现有实现可复用的代码

| 能力 | 位置 | 说明 |
| --- | --- | --- |
| 行权限 set/get 客户端 | `src/executor/finebi/client.py` | `set_row_filter`、`get_row_filter`、`get_row_filters_roles`、`get_row_filters_deposts`、`get_row_filters_users` |
| 数字 filterType ↔ set 结构转换 | `src/executor/finebi/rowfilter.py` | 默认映射 `10/12/34/35`；未知类型抛 `RowFilterError` 转人工 |
| 规则合并/序列化 | `src/executor/services/grant.py` | `request_rule_groups`、`merge_rule_groups`、`groups_to_set_payload`；组间 OR 合并 |
| FineDB 只读 | `src/executor/web/finedb.py` | `row_filter_options` 读取用户规则 + 全局 assist；只 SELECT |
| 行权限枚举 API | `src/executor/web/service.py::row_values` | API + FineDB + 缓存合并，前端 `/api/row-values` |
| 行权限状态检测 | `src/executor/web/service.py::row_permission_status` | 角色/部门/用户三类批量 get，缓存 5 分钟 |
| 审批人补行/列权限 | `src/executor/web/service.py::set_approver_scope`、`/requests/{id}/scope` | 保存到申请单，最终审批时 table→row→field 顺序执行 |

---

## 4. 给方案设计的约束（重点）

1. **全量覆盖**：set 接口不是“追加”。任何“给用户加一条规则”的动作都必须先读现状再合并写回，否则会清掉原有规则。
2. **行权限要在数据权限之后**：客户环境反馈，先没有数据集使用权限（`usePrivilege`）时直接写行权限会报错；方案执行顺序应为“数据权限（table）→ 行权限（row）→ 列权限（field）”。具体错误信息/版本差异需在联调时确认。
3. **候选值来源不是单一的**：
   - 用户/角色/部门 get 接口只返回该主体规则里的值；
   - 几百个店铺的全量枚举只在 FineDB 全局规则 `assist` 里；
   - 设计时要明确“候选值快照”从哪里来、多久刷新、FineDB 不可用时如何降级（现有方案：本地缓存 `data/row_value_cache.json`）。
4. **动态规则不可复制**：`filterType=11` 的规则是“按登录用户属性”动态生效，不能反序列化成固定值列表，也不能一键复制给另一个用户；审批人只能手工选值。
5. **合并语义**：项目现有 `merge_rule_groups` 是“组间 OR 合并”，可能扩大可见范围；如果新方案要求“以本次选择覆盖”，需要单独定义覆盖/并集策略。
6. **多主体**：同一用户可能同时命中用户级规则 + 角色规则 + 部门规则；最终可见范围由 FineBI 产品规则决定，方案需说明优先级/并集关系（需产品确认）。
7. **数量与性能**：电商客户几百个店铺；单表候选值可能上千。接口批量 get 可行但需分块/缓存；UI 必须是可搜索多选（当前已是搜索式多选下拉）。
8. **写后校验**：set 成功后应 `get` 回读校验；若回读不一致，重写一次，仍不一致转人工。
9. **审计**：行权限变更需要记录“谁、何时、把什么范围写给了谁”，现有申请单/台账字段可复用。

---

## 5. 需要 fable 确认/设计的问题

1. “数据集已配置行权限”的判定口径：任意主体有规则？只统计角色/部门？用户级规则算不算？
2. 候选值快照方案：FineDB 实时查 / 定时快照 / 开放平台 + 缓存兜底，三选一或组合？
3. 覆盖 vs 并集：审批人本次配置与用户原有用户级规则冲突时怎么处理？
4. 动态规则（filterType=11）在产品上如何展示、是否允许“复制为固定值规则”？
5. 角色/部门规则与用户级规则同时存在时的最终可见范围，是否需要在审批页展示提示？
6. 写失败/部分失败的重试与人工兜底流程。
7. 是否需要区分“用户级行权限”与“角色/部门级行权限”的审批权限（谁能改哪一类）？

---

## 6. 设计结论（fable，2026-11-23）

> 前提：帆软官方文档写明“部门、角色、用户同时设置行权限时，最终结果取『或』”
> 来源：https://help.fanruan.com/finebi/doc-view-1019.html（文档标注 7.0，需客户环境实测）

由此推断（**推断，非定论**）：用户级规则只能放大可见范围，不能把用户收窄到角色/部门规则以下。
**但注意“空即是真”配置会打破这条推断**，详见 6.5。

### 6.1 七个问题的结论

| # | 问题 | 结论 |
| --- | --- | --- |
| 1 | “已配置行权限”判定 | 任意主体（含用户级）有启用规则即算已配置；展示拆分为“角色/部门/全局 N 条、用户级 M 条”；命中后审批人必须显式选择范围，“全部数据”也要作为明确选项，不能留空默认 |
| 2 | 候选值快照 | 组合方案：定时 FineDB 读全局 `assist`（主来源）+ 手动刷新；合并开放平台该用户已有值；FineDB 不可用用本地缓存并显示快照时间；`assist` 是否等于全量需实测 |
| 3 | 覆盖 vs 并集 | 以“审批人确认的终态覆盖”，不做后台静默 OR；预填“原有规则 ∪ 本次申请”；同字段值合并进同一个 `strIn`；写入前再 get 一次，与审批时现状比对，不一致重新确认 |
| 4 | 动态规则 filterType=11 | 只读展示“动态规则：字段 = 登录用户属性”，不提供复制为固定值；目标用户级规则含 11/未知类型时禁止自动写入，转人工 |
| 5 | 多主体并存提示 | 必须提示：“最终可见范围 = 本次配置 ∪ 所属角色/部门规则”；同时考虑“空即是真”、部门层级“且”、关联表“且”等官方规则 |
| 6 | 失败与兜底 | 网络错误退避重试 3 次（set 全量覆盖，重复写安全）；回读不一致重写 1 次仍不一致转人工；**表权限成功、行权限失败时立即回收本单刚授予的表权限**，回收失败高优先级告警；步骤级记录 table/row/field 状态，支持从失败步骤续跑 |
| 7 | 审批权限区分 | 区分：本流程只写用户级规则；角色/部门/全局规则在审批页只读，由 FineBI 管理员在平台修改（根部门规则开放平台无法寻址） |

### 6.2 最关键的一个反例：`roleEmptyFilterAsTrueFilter`

官方文档中的“空即是真”：

- 角色/部门有表权限但**没有配置行权限**时，视为“可看全部”，参与“或”运算；
- 用户单独配置了行权限后，这个“全部”不再并入；
- 6.0 新工程默认开启，5.x 升级工程默认关闭，配置项：`SystemOptimizationConfig.roleEmptyFilterAsTrueFilter`。

**因此，开启“空即是真”时，给用户写用户级规则，可能让他从“看全部”变成“只看所选”**——这与“用户级只能放大”的推断相反。
联调前必须先查客户环境该配置值，再决定：

- 关闭：用户级规则只会放大/收窄在“或”范围内；
- 开启：用户级规则可能收窄，产品文案与审批风险提示必须改变。

### 6.3 “全部数据”选项的语义需要定死

“全部数据”不能简单等同于“不写用户级规则”：

| 场景 | 不写用户级规则的结果 |
| --- | --- |
| 用户无角色/部门规则 | 可能全量（“空即是真”开）或全量（无规则） |
| 用户有角色/部门规则 | 只拿到角色/部门的“或”范围，不等于全量 |
| “空即是真”关闭 | 角色/部门无行规则时可能无数据或全量，取决于版本行为 |

建议方案设计时把“全部数据”定义为以下之一，并写入接口/执行逻辑：

- A. 明确“不额外限制，继承角色/部门规则”（更符合“或”模型，但不一定是全量）；
- B. 写一条“命中所有行”的用户级规则（需要找到一个始终为真的字段/表达式；纯 `strIn` 未必能表达）；
- C. 仅允许在“用户无任何角色/部门行规则”时选择，否则只提供“继承/角色范围”选项。

这个语义会直接影响审批页面文案、请求 payload 和回读校验，必须在编码前确认。

### 6.4 现有实现与设计结论的差距（重要）

| 结论 | 当前实现 | 需要改什么 |
| --- | --- | --- |
| 任意主体规则都算“已配置” | `row_permission_status` 只用开放平台查角色/部门/用户；**根部门/全局规则（roleType=1）查不到** | 检测优先用 FineDB `fine_pack_filter` 做全量判定，API 作为补充；拆分“全局/角色/部门/用户级”计数 |
| 审批人必须显式选择范围，包括“全部数据” | 审批详情页有补充表单，但**不保存直接通过也行**，没有“已决策”状态 | 增加 `scope_decision = restricted / inherit_all / all`；配置了行权限时，未选择不允许通过；选择“全部数据”需先定义 6.3 语义 |
| 候选值快照 + 快照时间 | 实时 FineDB + API + 本地缓存，页面不显示快照时间 | 增加 `data/row_value_snapshot.json` + 定时任务/手动刷新按钮 + 页面显示“枚举快照时间”；`assist` 全量性做一次实测 |
| 覆盖而非静默 OR | `grant` 的 row 合并是组间 OR；审批人配置直接覆盖 payload | 改为“预填原规则 ∪ 本次选择”，同字段合并；写入前 get 当前规则与审批时快照比对；不一致拒绝并重确认 |
| 动态规则禁止自动写 | 现有 `rowfilter` 遇 `filterType=11` 抛错转人工（方向正确），但审批页无提前提示 | 审批页读取目标用户当前规则，若含 11/未知类型直接显示“需人工处理”，禁用保存/通过自动写入 |
| 多主体提示 | 只提示“已配置 N 条”，没有“最终范围 = 本次 ∪ 角色/部门”文案 | 增加多主体提示与“空即是真”配置状态说明 |
| 失败回滚 | 表权限成功后行权限失败，表权限保留（请求 partial/failed） | 增加“行失败→回收本单表权限”逻辑；回收失败告警；步骤级状态/续跑 |
| 只看用户级写权限 | 系统只写 user 级行权限，角色/部门规则只读 | 已符合结论 |

### 6.5 联调前必须确认

1. FineBI 版本与 `SystemOptimizationConfig.roleEmptyFilterAsTrueFilter` 的实际值；
2. `roleType` 各取值与 `roleId/departmentId/postId` 的对应关系（服务器 `DESCRIBE` + `SELECT DISTINCT`）；
3. `assist` 是否等于字段当前全部取值（新开店铺是否会不在其中）；
4. 用一个测试账号验证“用户级 ∪ 角色级/部门级”的实际可见结果，以及“空即是真”开启/关闭两种行为；
5. “全部数据”选项的最终语义（6.3 的 A/B/C）。

---

## 7. 附录：接口调用最小示例

```bash
# 1) 查用户行权限（无规则返回 data:""）
curl -s -X POST 'http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/user/get' \
  -H 'clientId: <id>' -H 'secret: <secret>' -H 'Content-Type: application/json' \
  -d '[{"user":"test","tableName":"<tableGUID>"}]'

# 2) 给用户设置行权限（全量覆盖）
curl -s -X POST 'http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/user' \
  -H 'clientId: <id>' -H 'secret: <secret>' -H 'Content-Type: application/json' \
  -d '[{"user":"test","tableName":"<tableGUID>","filter":{"type":"or","filterValue":[{"type":"strIn","fieldId":"<tableGUID>_<field>","filterValue":["店铺A","店铺B"]}]}}]'
```

> 注意：`<tableGUID>` 是数据集原始名/GUID；`<field>` 必须来自 `/v3/bi/table/info` 的 `fieldId`，不要手写中文编码。
