# 全局公共参数

**全局Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| clientId | {{clientId}} | string | 是 | - |
| secret | {{secret}} | string | 是 | - |
| secret | {{secret}} | string | 是 | - |
| clientId | {{clientId}} | string | 是 | - |

**全局Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**全局Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**全局认证方式**

> 无需认证

# 状态码说明

| 状态码 | 中文描述 |
| --- | ---- |
| 暂无参数 |

# 开放平台公共接口

> 创建人: 普洛托

> 更新人: icey

> 创建时间: 2022-06-09 10:10:41

> 更新时间: 2026-03-11 10:17:01

**帆软FR、BI平台对外开发公共接口文档说明**

#### 接口认证模式说明

###### 1.开放平台认证模式


 - 接口认证逻辑由 开放平台 - 应用 来管控，例如选择 aksk 认证模式，在接口请求时需传递 clientId 和 secret 参数；
 - 通过开放平台认证后，接口的 操作用户 默认为平台管理员；
 - 当需要修改 操作用户 时，可在 header 或 query 中添加 decUser 参数，参数值为用户名或用户id。

**通过开放平台认证后，接口的 操作用户 默认为平台管理员；**

```
操作用户
```

**当需要修改 操作用户 时，可在 header 或 query 中添加 decUser 参数，参数值为用户名或用户id。**

```
undefined
```

###### 2.fine_auth_token认证模式(需要安装子插件包来实现)

**帮助文档说明：开放平台子插件-https://help.fanruan.com/finereport/doc-view-4934.html**


 - 在请求地址中添加上 module/ 路径时(例如，原始为 /sp/client/api/*，添加后为 /sp/client/api/module/*)，接口认证逻辑不再由 开放平台 - 应用 来管控，而是需要携带帆软平台的认证登录标识 fine_auth_token，未携带或携带无效 token 时接口认证失败；
 - 
 - token 携带方式：和产品用户token传递方式一致
 - 
 - 该认证模式下，接口操作用户 为 fine_auth_token 中映射的用户，无法通过 decUser 参数修改。

```
undefined
```

**token 携带方式：和产品用户token传递方式一致
**

**token 携带方式：和产品用户token传递方式一致**

**该认证模式下，接口操作用户 为 fine_auth_token 中映射的用户，无法通过 decUser 参数修改。
**

**该认证模式下，接口操作用户 为 fine_auth_token 中映射的用户，无法通过 decUser 参数修改。**

```
undefined
```

#### 接口示例说明

##### 1.示例url中，"http://localhost:8075/webroot/decision"  为工程地址
2.engineName：直连-direct 抽取-spider

#### 权限管理接口配置说明

###### 配置父子目录权限的时候，权限逻辑需要和平台上保持一致。例如：父目录配置了【授权】权限后，不可以给子目录配置"empowerPrivilege": false，接口会报错。（产品默认置灰不可选，接口无法限制）

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

## BI（5.x）

> 创建人: 普洛托

> 更新人: JokerZy

> 创建时间: 2022-06-09 10:11:10

> 更新时间: 2023-01-06 09:42:53

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| fine_auth_token | {{token}} | String | 是 | - |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 数据权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:23:56

> 更新时间: 2022-07-26 09:23:51

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### BI 数据公共分组权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:18

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/group/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"groupId": "9cb54c94f6264d96877048f6774b7b49",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| groupId | 9cb54c94f6264d96877048f6774b7b49 | string | 是 | 分组id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 1-管理 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共分组权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:17

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/group/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"groupId": "9cb54c94f6264d96877048f6774b7b49",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| groupId | 9cb54c94f6264d96877048f6774b7b49 | string | 是 | 分组id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 1-管理 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共分组权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:16

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/group/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"groupId": "9cb54c94f6264d96877048f6774b7b49",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| groupId | 9cb54c94f6264d96877048f6774b7b49 | string | 是 | 分组id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 1-管理 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共业务包权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:19

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/pack/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"packId": "0d7be13b119b4a3fae13f6c5cd937d5f",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| packId | 0d7be13b119b4a3fae13f6c5cd937d5f | string | 是 | 业务包id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 1-管理 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共业务包权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:21

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/pack/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"packId": "0d7be13b119b4a3fae13f6c5cd937d5f",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| packId | 0d7be13b119b4a3fae13f6c5cd937d5f | string | 是 | 业务包id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 1-管理 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共业务包权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:14

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/pack/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"packId": "0d7be13b119b4a3fae13f6c5cd937d5f",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| packId | 0d7be13b119b4a3fae13f6c5cd937d5f | string | 是 | 业务包id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 1-管理 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:22

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/table/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"tableName": "api_接口添加SQL表测试",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:15

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/table/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"tableName": "api_接口添加SQL表测试",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:22

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/table/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"tableName": "api_接口添加SQL表测试",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 2-授权 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 行权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:23:57

> 更新时间: 2022-07-26 09:23:51

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据公共数据集行权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:20

> 更新时间: 2024-06-07 15:37:24

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"tableName": "api_接口添加SQL表测试",
		"filter": {
			"type": "or",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 strIn strNotIn |
| filter.filterValue.fieldId | api[5f]接口添加SQL表测试_canshu | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共数据集行权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:23

> 更新时间: 2024-06-07 15:37:24

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"tableName": "api_接口添加SQL表测试",
		"filter": {
			"type": "or",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 strIn strNotIn |
| filter.filterValue.fieldId | api[5f]接口添加SQL表测试_canshu | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共数据集行权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:21

> 更新时间: 2024-06-07 15:37:24

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"tableName": "api_接口添加SQL表测试",
		"filter": {
			"type": "and",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strNotIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | and | string | 是 | 类型 and or |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 strIn strNotIn |
| filter.filterValue.fieldId | api[5f]接口添加SQL表测试_canshu | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:17

> 更新时间: 2024-06-07 15:37:24

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"tableName": "api_接口添加SQL表测试",
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:18

> 更新时间: 2024-06-07 15:37:24

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"tableName": "api_接口添加SQL表测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:23

> 更新时间: 2024-06-07 15:37:24

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"tableName": "api_接口添加SQL表测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"737968e152a74190\",\"filterType\":34,\"filterValue\":[{\"id\":\"562a329931644711\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"be7b0dc4072b46f6\",\"filterType\":12,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"737968e152a74190","filterType":34,"filterValue":[{"id":"562a329931644711","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"be7b0dc4072b46f6","filterType":12,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 列权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:23:57

> 更新时间: 2022-07-26 09:23:51

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据公共列权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:06

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"fieldId": "mysql[5f]t[5f]D_name",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| fieldId | mysql[5f]t[5f]D_name | string | 是 | 字段id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共列权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:14

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"fieldId": "mysql[5f]t[5f]D_name",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| fieldId | mysql[5f]t[5f]D_name | string | 是 | 字段id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共列权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:19

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"fieldId": "mysql[5f]t[5f]D_name",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| fieldId | mysql[5f]t[5f]D_name | string | 是 | 字段id |
| values | - | array | 是 | 权限列表 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:15

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"fieldId": "mysql[5f]t[5f]D_name"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门id |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务id |
| fieldId | mysql[5f]t[5f]D_name | string | 是 | 字段id |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | - |
| data.data.authType | 0 | integer | 权限类型 0-使用 |
| data.data.authValue | true | boolean | 权限值 true \|| false |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:16

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"fieldId": "mysql[5f]t[5f]D_name"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色id |
| fieldId | mysql[5f]t[5f]D_name | string | 是 | 字段id |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | - |
| data.data.authType | 0 | integer | 权限类型 0-使用 |
| data.data.authValue | true | boolean | 权限值 true \|| false |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:20

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"fieldId": "mysql[5f]t[5f]D_name"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户id |
| fieldId | mysql[5f]t[5f]D_name | string | 是 | 字段id |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | - |
| data.data.authType | 0 | integer | 权限类型 0-使用 |
| data.data.authValue | true | boolean | 权限值 true \|| false |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 数据准备

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:46

> 更新时间: 2024-06-07 15:37:24

**engineName：直连-direct 抽取-spider**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 分组

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:47

> 更新时间: 2022-07-26 09:27:46

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 添加分组

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:52

> 更新时间: 2024-06-07 15:37:24

**传入父分组id（为空默认在根目录下添加分组），分组名称；返回分组id等信息**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/group/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"pGroupId": "",
		"groupName": "接口添加分组测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| pGroupId | - | string | 是 | 父文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"]；传""即为根文件夹 |
| groupName | 接口添加分组测试 | string | 是 | 分组名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"groupId": "ce890923c27d48d0b772a7a48a9285bd",
				"groupName": "接口添加分组测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.groupId | ce890923c27d48d0b772a7a48a9285bd | string | 分组ID |
| data.data.groupName | 接口添加分组测试 | string | 分组名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 分组重命名

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:53

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/group/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"groupId": "ce890923c27d48d0b772a7a48a9285bd",
		"newGroupName": "分组重命名"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| groupId | ce890923c27d48d0b772a7a48a9285bd | string | 是 | 分组id |
| newGroupName | 分组重命名 | string | 是 | 重命名的分组名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除分组

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:53

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/group/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"groupId": "ce890923c27d48d0b772a7a48a9285bd"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| groupId | ce890923c27d48d0b772a7a48a9285bd | string | 是 | 分组id |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取所有业务包分组信息

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:52

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/groups

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"id": "__my_analysis_group__bf2115b1-44a6-4bd0-bb30-b75641a7754e1",
			"name": "我的自助数据集",
			"packs": [
				{
					"id": "__share_me__bf2115b1-44a6-4bd0-bb30-b75641a7754e1",
					"name": "分享给我的自助数据集",
					"createBy": "admin",
					"myAnalysis": true,
					"shareAnalysis": true
				},
				{
					"id": "__my_analysis__bf2115b1-44a6-4bd0-bb30-b75641a7754e1",
					"name": "admin的业务包",
					"createBy": "admin",
					"myAnalysis": true,
					"shareAnalysis": false
				}
			],
			"groups": []
		},
		{
			"id": "__no_group__d",
			"name": "未分组",
			"packs": [],
			"groups": []
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据，业务包和分组的树 |
| data.id | __my_analysis_group__bf2115b1-44a6-4bd0-bb30-b75641a7754e1 | string | 分组id |
| data.name | 我的自助数据集 | string | 分组名称 |
| data.packs | - | array | 分组包含的业务包列表 |
| data.packs.id | __share_me__bf2115b1-44a6-4bd0-bb30-b75641a7754e1 | string | 业务包id |
| data.packs.name | 分享给我的自助数据集 | string | 业务包名称 |
| data.packs.createBy | admin | string | 创建者名称 |
| data.packs.myAnalysis | true | boolean | 是否是我的自助数据集中的 |
| data.packs.shareAnalysis | true | boolean | 是否是分享给我的 |
| data.groups | - | array | 分组包含的分组列表 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 业务包

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:47

> 更新时间: 2022-07-26 09:27:46

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 添加业务包

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:55

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/pack/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"pGroupId": "d35b7591cd3e4a0a8ac6c3e207c566c2",
		"packName": "接口添加业务包"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| pGroupId | d35b7591cd3e4a0a8ac6c3e207c566c2 | string | 是 | 父文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"]；传""即为根文件夹 |
| packName | 接口添加业务包 | string | 是 | 文件夹名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"packId": "efe82b2cb0134158b8c7ed18e6ad965e",
				"packName": "接口添加业务包"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 业务包信息 |
| data.data.packId | efe82b2cb0134158b8c7ed18e6ad965e | string | 业务包ID |
| data.data.packName | 接口添加业务包 | string | 业务包名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 业务包重命名

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:54

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/pack/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "efe82b2cb0134158b8c7ed18e6ad965e",
		"newPackName": "业务包重命名"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | efe82b2cb0134158b8c7ed18e6ad965e | string | 是 | - |
| newPackName | 业务包重命名 | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除业务包

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:50

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/pack/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "efe82b2cb0134158b8c7ed18e6ad965e"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | efe82b2cb0134158b8c7ed18e6ad965e | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取业务包相关信息

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:49

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/pack/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "e62d00d5c97341f6aed9875d8ad95b8e"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | e62d00d5c97341f6aed9875d8ad95b8e | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"id": "e62d00d5c97341f6aed9875d8ad95b8e",
				"name": "接口添加业务包",
				"owner": "bf2115b1-44a6-4bd0-bb30-b75641a7754e",
				"createBy": "admin",
				"tables": [
					"api_接口添加SQL表测试"
				],
				"tableList": [
					{
						"name": "api_接口添加SQL表测试",
						"transferName": "新的数据集名称",
						"createBy": "admin"
					}
				]
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.id | e62d00d5c97341f6aed9875d8ad95b8e | string | 业务包id |
| data.data.name | 接口添加业务包 | string | 业务包名称 |
| data.data.owner | bf2115b1-44a6-4bd0-bb30-b75641a7754e | string | 业务包创建者ID |
| data.data.createBy | admin | string | 创建者用户 |
| data.data.tables | api_接口添加SQL表测试 | array | 数据集名称列表 |
| data.data.tableList | - | array | 数据集列表 |
| data.data.tableList.name | api_接口添加SQL表测试 | string | 数据集原始名 |
| data.data.tableList.transferName | 新的数据集名称 | string | 数据集转义名 |
| data.data.tableList.createBy | admin | string | 创建者用户 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:46

> 更新时间: 2022-07-26 09:27:46

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 添加DB数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:50

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/addDb

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "e62d00d5c97341f6aed9875d8ad95b8e",
		"connectionName": "mysql",
		"dbTableName": "t"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | e62d00d5c97341f6aed9875d8ad95b8e | string | 是 | 业务包id |
| connectionName | mysql | string | 是 | 数据链接名称 |
| dbTableName | t | string | 是 | 数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "mysql_t_D",
				"transferName": "mysql_t"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | mysql_t_D | string | 数据集原始名 |
| data.data.transferName | mysql_t | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:51

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "mysql_t_D"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | mysql_t_D | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 新建SQL数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-10-12 17:12:56

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/addSql

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "e62d00d5c97341f6aed9875d8ad95b8e",
		"connectionName": "mysql",
		"tableName": "api_接口添加SQL表测试",
		"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
		"paramSetting": [
			{
				"name": "uptype",
				"value": "add",
				"type": 16
			},
			{
				"name": "time",
				"value": "2022-08-29",
				"type": 48
			},
			{
				"name": "shoufei",
				"type": 32,
				"value": "10"
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | e62d00d5c97341f6aed9875d8ad95b8e | string | 是 | 业务包id |
| connectionName | mysql | string | 是 | 数据连接名称 |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集名称 |
| sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | 是 | sql语句 |
| paramSetting | - | array | 是 | - |
| paramSetting.name | uptype | string | 是 | 参数名 |
| paramSetting.value | add | string | 是 | 参数值 |
| paramSetting.type | 16 | integer | 是 | 参数类型 文本-16 时间-48 数值-32 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "api_接口添加SQL表测试",
				"transferName": "api_接口添加SQL表测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | api_接口添加SQL表测试 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 更新SQL数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-10-12 17:14:54

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/updateSql

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"connectionName": "mysql",
		"tableName": "api_接口添加SQL表测试",
		"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
		"paramSetting": [
			{
				"name": "uptype",
				"value": "add",
				"type": 16
			},
			{
				"name": "time",
				"value": "2022-08-29",
				"type": 48
			},
			{
				"name": "shoufei",
				"type": 32,
				"value": "10"
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| connectionName | mysql | string | 是 | 数据连接名称 |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | 是 | sql语句 |
| paramSetting | - | array | 是 | - |
| paramSetting.name | uptype | string | 是 | 参数名称 |
| paramSetting.value | add | string | 是 | 参数值 |
| paramSetting.type | 16 | integer | 是 | 参数类型 文本-16 时间-48 数值-32 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "api_接口添加SQL表测试",
				"transferName": "api_接口添加SQL表测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | api_接口添加SQL表测试 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据集修改转义名

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:48

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "api_接口添加SQL表测试",
		"newTransferName": "新的数据集名称"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |
| newTransferName | 新的数据集名称 | string | 是 | 新数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取数据集相关信息

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:27:49

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "api_接口添加SQL表测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "api_接口添加SQL表测试",
				"transferName": "新的数据集名称",
				"createBy": "admin",
				"fields": [
					{
						"fieldId": "api[5f]接口添加SQL表测试_canshu",
						"name": "canshu",
						"transferName": "canshu"
					}
				]
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.tableName | api_接口添加SQL表测试 | string | 数据集原始名 |
| data.data.transferName | 新的数据集名称 | string | 数据集转义名 |
| data.data.createBy | admin | string | 创建者用户 |
| data.data.fields | - | array | 字段列表 |
| data.data.fields.fieldId | api[5f]接口添加SQL表测试_canshu | string | 字段ID |
| data.data.fields.name | canshu | string | 字段原始名 |
| data.data.fields.transferName | canshu | string | 字段转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据集血缘分析

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-09-05 16:17:12

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/usage

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"tableName": "admin的自助数据集"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | admin的自助数据集 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"sonTables": [],
				"fatherTables": [
					{
						"tableName": "测试参数数据集",
						"createBy": "admin",
						"usage": [],
						"transferName": "测试参数数据集",
						"tables": []
					}
				],
				"usage": [
					{
						"id": "2479c18501bd497cbc99c373bd99be5d",
						"name": "新建仪表板2",
						"createBy": "admin"
					}
				],
				"tableName": "admin的自助数据集",
				"transferName": "admin的自助数据集",
				"createBy": "admin"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.sonTables | - | array | 关联子表列表，结构同父表列表 |
| data.data.fatherTables | - | array | 关联父表列表 |
| data.data.fatherTables.tableName | 测试参数数据集 | string | 数据集原始名 |
| data.data.fatherTables.createBy | admin | string | 创建者用户 |
| data.data.fatherTables.usage | - | array | 关联仪表板列表 |
| data.data.fatherTables.transferName | 测试参数数据集 | string | 数据集转义名 |
| data.data.fatherTables.tables | - | array | 关联数据集列表 |
| data.data.usage | - | array | 关联仪表板列表 |
| data.data.usage.id | 2479c18501bd497cbc99c373bd99be5d | string | 关联仪表板ID |
| data.data.usage.name | 新建仪表板2 | string | 关联仪表板名称 |
| data.data.usage.createBy | admin | string | 创建者用户 |
| data.data.tableName | admin的自助数据集 | string | 数据集原始名 |
| data.data.transferName | admin的自助数据集 | string | 数据集转义名 |
| data.data.createBy | admin | string | 创建者用户 |

* 失败(201)

```javascript
暂无数据
```

**Query**

##### 添加服务器数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-12-08 17:04:37

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{engineName}/table/addDataset

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "e62d00d5c97341f6aed9875d8ad95b8e",
		"datasetName": "fine_record_login"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | e62d00d5c97341f6aed9875d8ad95b8e | string | 是 | 业务包ID 或 业务包路径（如[\"未分组\",\"接口添加业务包\"]） |
| datasetName | fine_record_login | string | 是 | 服务器数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "__FR_BI_SERVER_SQL___fine_record_login_D",
				"transferName": "__FR_BI_SERVER_SQL___fine_record_login"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | __FR_BI_SERVER_SQL___fine_record_login_D | string | 数据集原始名 |
| data.data.transferName | __FR_BI_SERVER_SQL___fine_record_login | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### Spider更新

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-11-16 11:11:20

> 更新时间: 2022-11-16 11:11:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 触发全局更新

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-11-16 11:11:43

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/all

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"taskInstanceId": "c96790d6-19d0-4c67-8188-7547b69d7c12"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.taskInstanceId | c96790d6-19d0-4c67-8188-7547b69d7c12 | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 触发业务包更新

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-11-16 11:11:43

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/pack

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "cc3f64cdade64551a557dafda89b4c2b"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | cc3f64cdade64551a557dafda89b4c2b | string | 是 | 业务包ID 或 业务包路径（如[\"未分组\",\"接口添加业务包\"]） |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "25cbd26f-0688-4aec-a85d-78e896494fbe"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.taskInstanceId | 25cbd26f-0688-4aec-a85d-78e896494fbe | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 触发数据集更新

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-11-16 11:11:43

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/table

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "mysql_销售明细表_S",
		"fullLoad": true
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | mysql_销售明细表_S | string | 是 | 数据集原始名 |
| fullLoad | true | boolean | 否 | fullload 参数为 false 表示增量更新，true 为全量更新，不填改参数默认为 true 。 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "e03e26f7-85ab-43c7-a635-4e670a1bdb4d"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 批量返回结果 |
| data.data.taskInstanceId | e03e26f7-85ab-43c7-a635-4e670a1bdb4d | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 查询更新任务状态

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-11-16 11:11:43

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/instance/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"taskInstanceId": "0c48ac30-b335-41bd-9ed6-77134e94a0a5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| taskInstanceId | 0c48ac30-b335-41bd-9ed6-77134e94a0a5 | string | 是 | 更新任务ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "0c48ac30-b335-41bd-9ed6-77134e94a0a5",
				"taskName": "全局更新任务",
				"state": 1,
				"triggerType": 1,
				"resultType": 1
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.taskInstanceId | 0c48ac30-b335-41bd-9ed6-77134e94a0a5 | string | 更新任务ID |
| data.data.taskName | 全局更新任务 | string | 任务名称 |
| data.data.state | 1 | integer | 更新状态，1为已结束，2为正在运行中 |
| data.data.triggerType | 1 | integer | 触发方式，1为手动，2为自动，3为内部 |
| data.data.resultType | 1 | integer | 运行结果，1为全部成功，2为部分成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 抽取更新任务运行监控查询

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-11-16 11:11:43

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/monitor/task/query

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"page": 1,
	"pageSize": 20,
	"queryCondition": {
		"taskName": "mysql_销售明细表更新任务",
		"taskStartFrom": 0,
		"taskStartTo": 0,
		"taskEndFrom": 0,
		"taskEndTo": 0,
		"triggerTypes": [
			1,
			2
		],
		"roleNames": [
			"system",
			"admin",
			"API"
		],
		"taskStatusList": [
			1,
			2
		],
		"resultTypes": [
			1,
			2
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| page | 1 | integer | 是 | 页数 |
| pageSize | 20 | integer | 是 | 分页数量 |
| queryCondition | - | object | 否 | 查询条件 |
| queryCondition.taskName | mysql_销售明细表更新任务 | string | 否 | 任务名称 |
| queryCondition.taskStartFrom | 0 | integer | 否 | 任务开始时间范围起点，毫秒级时间戳同下 |
| queryCondition.taskStartTo | 0 | integer | 否 | 任务开始时间范围终点 |
| queryCondition.taskEndFrom | 0 | integer | 否 | 任务结束时间范围起点 |
| queryCondition.taskEndTo | 0 | integer | 否 | 任务结束时间范围终点 |
| queryCondition.triggerTypes | 1 | array | 否 | 触发方式 手动1 定时2 |
| queryCondition.roleNames | system | array | 否 | 触发人名称，如 system admin API |
| queryCondition.taskStatusList | 1 | array | 否 | 更新状态-已结束 1 正在更新中 2 |
| queryCondition.resultTypes | 1 | array | 否 | 运行结果 全部成功 1 部分成功 2 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"monitorTaskBeanList": [
			{
				"taskInstanceId": "fc1b298b-e821-4dad-9e6b-19900cd017ca",
				"taskName": "mysql_销售明细表更新任务",
				"startTime": 1667286028393,
				"endTime": 1667286037990,
				"state": 1,
				"triggerType": 2,
				"resultType": 1,
				"roleName": "system",
				"baseTableExpect": 1,
				"baseTableFinish": 1,
				"analysisTableExpect": 1,
				"analysisTableFinish": 1,
				"relationExpect": 0,
				"relationFinish": 0
			}
		],
		"totalSize": 1
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.monitorTaskBeanList | - | array | 任务列表 |
| data.monitorTaskBeanList.taskInstanceId | fc1b298b-e821-4dad-9e6b-19900cd017ca | string | 任务ID |
| data.monitorTaskBeanList.taskName | mysql_销售明细表更新任务 | string | 任务名称 |
| data.monitorTaskBeanList.startTime | 1667286028393 | integer | 开始时间 |
| data.monitorTaskBeanList.endTime | 1667286037990 | integer | 结束时间 |
| data.monitorTaskBeanList.state | 1 | integer | 更新状态-已结束 1 正在更新中 2 |
| data.monitorTaskBeanList.triggerType | 2 | integer | 触发方式 手动1 定时2 |
| data.monitorTaskBeanList.resultType | 1 | integer | 运行结果 全部成功 1 部分成功 2 |
| data.monitorTaskBeanList.roleName | system | string | 触发人名称 |
| data.monitorTaskBeanList.baseTableExpect | 1 | integer | 基础表更新预期个数 |
| data.monitorTaskBeanList.baseTableFinish | 1 | integer | 基础表更新完成个数 |
| data.monitorTaskBeanList.analysisTableExpect | 1 | integer | 自助数据集更新预期个数 |
| data.monitorTaskBeanList.analysisTableFinish | 1 | integer | 自助数据集更新完成个数 |
| data.monitorTaskBeanList.relationExpect | 0 | integer | 关联更新预期个数 |
| data.monitorTaskBeanList.relationFinish | 0 | integer | 关联更新完成个数 |
| data.totalSize | 1 | integer | 任务总数 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:23:55

> 更新时间: 2022-07-26 09:23:51

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 新建仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:23:58

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/create

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"pDashFolderId": "5cf1544e0708423f972bcd1445126707",
		"dashName": "新建仪表板X"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| pDashFolderId | 5cf1544e0708423f972bcd1445126707 | string | 是 | 父文件夹ID 或 文件夹路径 |
| dashName | 新建仪表板X | string | 是 | 仪表板名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "8e898c66b8704e1c91f8d4eeb94bc9e1",
				"dashName": "新建仪表板X"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | 8e898c66b8704e1c91f8d4eeb94bc9e1 | string | 仪表板ID |
| data.data.dashName | 新建仪表板X | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 重命名仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:01

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"dashId": "bd1c86aeb2674aaeb30f6554c9c77f14",
		"newDashName": "新的仪表板名称"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | bd1c86aeb2674aaeb30f6554c9c77f14 | string | 是 | 仪表板ID 或 仪表板文件夹路径 |
| newDashName | 新的仪表板名称 | string | 是 | 新的仪表板名称 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 删除仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:07

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"dashId": "8e898c66b8704e1c91f8d4eeb94bc9e1"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | 8e898c66b8704e1c91f8d4eeb94bc9e1 | string | 是 | 仪表板ID 或 仪表板文件夹路径 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 另存为仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:05

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/saveas

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"fromDashId": "b2de9bc4ee3f4454a933cfea4374fee1",
		"toNewDashName": "另存为后的仪表板名称",
		"toParentDashFolderId": "5cf1544e0708423f972bcd1445126707"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| fromDashId | b2de9bc4ee3f4454a933cfea4374fee1 | string | 是 | 仪表板ID 或 仪表板文件夹路径 |
| toNewDashName | 另存为后的仪表板名称 | string | 是 | 另存为的仪表板名称 |
| toParentDashFolderId | 5cf1544e0708423f972bcd1445126707 | string | 是 | 另存为的父 文件夹ID 或 文件夹路径 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "bd1c86aeb2674aaeb30f6554c9c77f14",
				"dashName": "另存为后的仪表板名称"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | bd1c86aeb2674aaeb30f6554c9c77f14 | string | 仪表板ID |
| data.data.dashName | 另存为后的仪表板名称 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 获取仪表板相关信息

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:11

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"dashId": "27a285f2486b4f9e9efa91d7ac276030"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 是 | 仪表板ID 或 仪表板文件夹路径 |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "27a285f2486b4f9e9efa91d7ac276030",
				"dashName": "新建仪表板"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 仪表板ID |
| data.data.dashName | 新建仪表板 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 获取当前用户的所有仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:23:59

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/user/all

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"dashId": "27a285f2486b4f9e9efa91d7ac276030",
			"dashName": "新建仪表板"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据 |
| data.dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 仪表板ID |
| data.dashName | 新建仪表板 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 仪表板导出图片

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-11-09 14:20:50

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/export/png

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"dashId": "27a285f2486b4f9e9efa91d7ac276030"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 是 | 仪表板ID 或 仪表板文件夹路径 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"attach_type": "image",
		"attach_id": "default1665546823726_ppd-t",
		"filename": "27a285f2486b4f9e9efa91d7ac276030.png"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.attach_type | image | string | 附件类型 |
| data.attach_id | default1665546823726_ppd-t | string | 附件ID，下载文件，产品接口：http(s)://xx.com/webroot/decision/view/report?op=fr_attach&amp;cmd=ah_download&amp;id=附件ID |
| data.filename | 27a285f2486b4f9e9efa91d7ac276030.png | string | 附件名称 |

* 失败(201)

```javascript
暂无数据
```

**Query**

### 仪表板权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-07-26 09:23:54

> 更新时间: 2022-07-26 09:23:51

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### BI 仪表板公共链接使用权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:13

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/publink/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门ID |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板公共链接使用权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:04

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/publink/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板公共链接使用权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:02

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/publink/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板分享使用权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:09

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/share/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门ID |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板分享使用权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:07

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/share/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板分享使用权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-07-26 09:24:12

> 更新时间: 2024-06-07 15:37:24

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/share/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* (404)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 模板认证

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-12-08 17:01:23

> 更新时间: 2022-12-08 17:01:23

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 角色权限认证

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2022-12-08 17:02:05

> 更新时间: 2024-06-07 15:37:24

**准备工作：需要先开启模板认证全局设置-角色权限认证，并选择需要认证的模板。
查看权限关闭时，导出权限也要同时关闭；导出开启时，查看权限也要同时开启。**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### BI 仪表板模板认证权限查询对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-12-08 17:02:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"dashId": "07562a12bbe544008b09f066ed3f35d3"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门ID |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 是 | 职务ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | 如果没有返回的，就是默认没权限 |
| data.data.authType | 0 | integer | 权限类型 0-查看 1-导出 |
| data.data.authValue | true | boolean | true - 有权限 false - 无权限 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-12-08 17:02:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "7e5d2ad6-7b02-4f40-b9bf-31893932fb91",
		"postId": "645a87c4-f558-49b3-8e6c-da8b561f320a",
		"dashId": "07562a12bbe544008b09f066ed3f35d3",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | 7e5d2ad6-7b02-4f40-b9bf-31893932fb91 | string | 是 | 部门ID |
| postId | 645a87c4-f558-49b3-8e6c-da8b561f320a | string | 否 | 职务ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-查看 1-导出 |
| values.authValue | true | boolean | 是 | true - 有权限 false - 无权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限查询对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-12-08 17:02:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"dashId": "07562a12bbe544008b09f066ed3f35d3"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 如果没有返回的，就是默认没权限 |
| data.data.authType | 0 | integer | 权限类型 0-查看 1-导出 |
| data.data.authValue | true | boolean | true - 有权限 false - 无权限 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-12-08 17:02:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"dashId": "07562a12bbe544008b09f066ed3f35d3",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |
| values | - | object | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-查看 1-导出 |
| values.authValue | true | boolean | 是 | true - 有权限 false - 无权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限查询对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-12-08 17:02:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"dashId": "07562a12bbe544008b09f066ed3f35d3"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | 如果没有返回的，就是默认没权限 |
| data.data.authType | 0 | integer | 权限类型 0-查看 1-导出 |
| data.data.authValue | true | boolean | true - 有权限 false - 无权限 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2022-12-08 17:02:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"dashId": "07562a12bbe544008b09f066ed3f35d3",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-查看 1-导出 2-授权 |
| values.authValue | true | boolean | 是 | true - 有权限 false - 无权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

## BI6.x

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2025-06-04 15:23:08

**FineBI开放平台接口**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 数据权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:31

> 更新时间: 2023-02-09 09:57:31

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### BI 数据公共文件夹权限对部门职务

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/pack/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"packId": "102a8a2183cf4304ae566abedca05c60",
		"values": [
			{
				"authType": 3,
				"authValue": true
			},
			{
				"authType": 0,
				"authValue": true
			},
			{
				"authType": 1,
				"authValue": true
			},
			{
				"authType": 2,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |
| values | - | array | 是 | 权限值 |
| values.authType | 3 | integer | 是 | 权限类型 0-使用1-管理2-授权3-组件数据 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共文件夹权限对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/pack/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"packId": "102a8a2183cf4304ae566abedca05c60",
		"values": [
			{
				"authType": 3,
				"authValue": true
			},
			{
				"authType": 0,
				"authValue": true
			},
			{
				"authType": 1,
				"authValue": false
			},
			{
				"authType": 2,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |
| values | - | array | 是 | 权限值 |
| values.authType | 3 | integer | 是 | 权限类型 0-使用1-管理2-授权3-组件数据 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共文件夹权限对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/pack/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"packId": "102a8a2183cf4304ae566abedca05c60",
		"values": [
			{
				"authType": 3,
				"authValue": true
			},
			{
				"authType": 0,
				"authValue": true
			},
			{
				"authType": 1,
				"authValue": true
			},
			{
				"authType": 2,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |
| values | - | array | 是 | 权限值 |
| values.authType | 3 | integer | 是 | 权限类型 0-使用1-管理2-授权3-组件数据 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/table/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"values": [
			{
				"authType": 3,
				"authValue": true
			},
			{
				"authType": 0,
				"authValue": false
			},
			{
				"authType": 1,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| values | - | array | 是 | 权限值 |
| values.authType | 3 | integer | 是 | 权限类型 0-使用1-管理2-授权3-组件数据 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/table/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"values": [
			{
				"authType": 3,
				"authValue": true
			},
			{
				"authType": 0,
				"authValue": true
			},
			{
				"authType": 1,
				"authValue": true
			},
			{
				"authType": 2,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| values | - | array | 是 | 权限值 |
| values.authType | 3 | integer | 是 | 权限类型 0-使用1-管理2-授权3-组件数据 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/table/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"values": [
			{
				"authType": 3,
				"authValue": true
			},
			{
				"authType": 0,
				"authValue": true
			},
			{
				"authType": 1,
				"authValue": true
			},
			{
				"authType": 2,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| values | - | array | 是 | 权限值 |
| values.authType | 3 | integer | 是 | 权限类型 0-使用1-管理2-授权3-组件数据 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 列权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2023-02-09 09:57:33

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据公共列权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | - |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共列权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | - |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共列权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | - |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | - |
| data.data.authType | 0 | integer | 权限类型 0-使用 |
| data.data.authValue | true | boolean | 权限值 true \|| false |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | - |
| data.data.authType | 0 | integer | 权限类型 0-使用 |
| data.data.authValue | true | boolean | 权限值 true \|| false |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/field/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | - |
| data.data.authType | 0 | integer | 权限类型 0-使用 |
| data.data.authValue | true | boolean | 权限值 true \|| false |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 行权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2023-02-09 09:57:33

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据公共数据集行权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-25 20:26:44

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053",
				"filter": {
			"type": "or",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue.fieldId | api[5f]接口添加SQL表测试_canshu | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共数据集行权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"filter": {
			"type": "or",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue.fieldId | api[5f]接口添加SQL表测试_canshu | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共数据集行权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"filter": {
			"type": "and",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strNotIn",
				"fieldId": "api[5f]接口添加SQL表测试_canshu",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | and | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue.fieldId | api[5f]接口添加SQL表测试_canshu | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"tableName": "api_接口添加SQL表测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/row/filter/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"tableName": "api_接口添加SQL表测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| tableName | api_接口添加SQL表测试 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"737968e152a74190\",\"filterType\":34,\"filterValue\":[{\"id\":\"562a329931644711\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"be7b0dc4072b46f6\",\"filterType\":12,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"737968e152a74190","filterType":34,"filterValue":[{"id":"562a329931644711","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"be7b0dc4072b46f6","filterType":12,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 数据准备（公共数据）

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 新建SQL数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/addSql

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "9b539b7d398641b389c9c33ee5fcabed",
		"connectionName": "mysql",
		"tableName": "api_接口添加SQL表测试",
		"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
		"paramSetting": [
			{
				"name": "uptype",
				"value": "add",
				"type": 16
			},
			{
				"name": "time",
				"value": "2022-08-29",
				"type": 48
			},
			{
				"name": "shoufei",
				"type": 32,
				"value": "10"
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 文件夹ID |
| connectionName | mysql | string | 是 | 数据连接名称 |
| tableName | api_接口添加SQL表测试 | string | 是 | 添加到数据准备里的数据集名称 |
| sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | 是 | sql 字符串 |
| paramSetting | - | array | 否 | 参数设置，需要和sql保持一致 |
| paramSetting.name | uptype | string | 是 | 参数名称 |
| paramSetting.value | add | string | 是 | 参数值 |
| paramSetting.type | 16 | integer | 是 | 参数类型 文本-16 时间-48 数值-32 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "cc3fa97db37348f7b32231412b429053",
				"transferName": "api_接口添加SQL表测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | cc3fa97db37348f7b32231412b429053 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 更新SQL数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/updateSql

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"connectionName": "mysql",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
		"paramSetting": [
			{
				"name": "uptype",
				"value": "add",
				"type": 16
			},
			{
				"name": "time",
				"value": "2022-11-30",
				"type": 48
			},
			{
				"name": "shoufei",
				"type": 32,
				"value": "10"
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| connectionName | mysql | string | 是 | 数据连接名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | 是 | sql 字符串 |
| paramSetting | - | array | 否 | 参数设置，需要和sql保持一致 |
| paramSetting.name | uptype | string | 是 | 参数名称 |
| paramSetting.value | add | string | 是 | 参数值 |
| paramSetting.type | 16 | integer | 是 | 参数类型 文本-16 时间-48 数值-32 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "cc3fa97db37348f7b32231412b429053",
				"transferName": "api_接口添加SQL表测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | cc3fa97db37348f7b32231412b429053 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取数据集相关信息

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "cc3fa97db37348f7b32231412b429053",
				"transferName": "api_接口添加SQL表测试",
				"createBy": "admin",
				"fields": [
					{
						"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
						"name": "销售单号",
						"transferName": "销售单号"
					}
				]
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.tableName | cc3fa97db37348f7b32231412b429053 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |
| data.data.createBy | admin | string | 创建者用户 |
| data.data.fields | - | array | 字段列表 |
| data.data.fields.fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 字段ID |
| data.data.fields.name | 销售单号 | string | 字段原始名 |
| data.data.fields.transferName | 销售单号 | string | 字段转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 添加DB数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/addDb

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "9b539b7d398641b389c9c33ee5fcabed",
		"connectionName": "mysql",
		"dbTableName": "t"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 业务包ID 或 业务包路径 |
| connectionName | mysql | string | 是 | 数据连接名称 |
| dbTableName | t | string | 是 | 数据库表名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "mysql_t_D",
				"transferName": "mysql_t"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | mysql_t_D | string | 数据集原始名 |
| data.data.transferName | mysql_t | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "3b581fcfc09a4f43922a7676ef9865d0"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | 3b581fcfc09a4f43922a7676ef9865d0 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据集修改转义名

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "9d46d930cf824209ac0f3e9354f810a4",
		"newTransferName": "新的数据集名称"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | 9d46d930cf824209ac0f3e9354f810a4 | string | 是 | 数据集原始名 |
| newTransferName | 新的数据集名称 | string | 是 | 新的数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据集血缘分析

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/usage

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"tableName": "admin的自助数据集"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | admin的自助数据集 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"sonTables": [],
				"fatherTables": [
					{
						"tableName": "测试参数数据集",
						"createBy": "admin",
						"usage": [],
						"transferName": "测试参数数据集",
						"tables": []
					}
				],
				"usage": [
					{
						"id": "2479c18501bd497cbc99c373bd99be5d",
						"name": "新建仪表板2",
						"createBy": "admin"
					}
				],
				"tableName": "admin的自助数据集",
				"transferName": "admin的自助数据集",
				"createBy": "admin"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.sonTables | - | array | 关联子表列表，结构同父表列表 |
| data.data.fatherTables | - | array | 关联父表列表 |
| data.data.fatherTables.tableName | 测试参数数据集 | string | 数据集原始名 |
| data.data.fatherTables.createBy | admin | string | 创建者用户 |
| data.data.fatherTables.usage | - | array | 关联仪表板列表 |
| data.data.fatherTables.transferName | 测试参数数据集 | string | 数据集转义名 |
| data.data.fatherTables.tables | - | array | 关联数据集列表 |
| data.data.usage | - | array | 关联仪表板列表 |
| data.data.usage.id | 2479c18501bd497cbc99c373bd99be5d | string | 关联仪表板ID |
| data.data.usage.name | 新建仪表板2 | string | 关联仪表板名称 |
| data.data.usage.createBy | admin | string | 创建者用户 |
| data.data.tableName | admin的自助数据集 | string | 数据集原始名 |
| data.data.transferName | admin的自助数据集 | string | 数据集转义名 |
| data.data.createBy | admin | string | 创建者用户 |

* 失败(201)

```javascript
暂无数据
```

**Query**

##### 添加服务器数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/{{engineName}}/table/addDataset

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "9b539b7d398641b389c9c33ee5fcabed",
		"datasetName": "test"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | e62d00d5c97341f6aed9875d8ad95b8e | string | 是 | 业务包ID 或 业务包路径（如[\"未分组\",\"接口添加业务包\"]） |
| datasetName | t | string | 是 | 服务器数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "__FR_BI_SERVER_SQL___fine_record_login_D",
				"transferName": "__FR_BI_SERVER_SQL___fine_record_login"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | __FR_BI_SERVER_SQL___fine_record_login_D | string | 数据集原始名 |
| data.data.transferName | __FR_BI_SERVER_SQL___fine_record_login | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 抽取更新

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 触发全局更新

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:31

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/all

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"taskInstanceId": "c96790d6-19d0-4c67-8188-7547b69d7c12"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.taskInstanceId | c96790d6-19d0-4c67-8188-7547b69d7c12 | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 触发业务包更新

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/pack

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "cc3f64cdade64551a557dafda89b4c2b"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | cc3f64cdade64551a557dafda89b4c2b | string | 是 | 业务包ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "25cbd26f-0688-4aec-a85d-78e896494fbe"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.taskInstanceId | 25cbd26f-0688-4aec-a85d-78e896494fbe | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 触发数据集更新

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/table

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "8d93f61b173f4f4ab51d9c6d7dac9079",
		"fullLoad": true
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | 8d93f61b173f4f4ab51d9c6d7dac9079 | string | 是 | 数据集原始名 |
| fullLoad | true | boolean | 否 | fullload 参数为 false 表示增量更新，true 为全量更新，不填改参数默认为 true 。 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "e03e26f7-85ab-43c7-a635-4e670a1bdb4d"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 批量返回结果 |
| data.data.taskInstanceId | e03e26f7-85ab-43c7-a635-4e670a1bdb4d | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 查询更新任务状态

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/instance/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"taskInstanceId": "636cb1fa-c9e2-4d5a-b52b-be16e5a5aff1"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| taskInstanceId | 636cb1fa-c9e2-4d5a-b52b-be16e5a5aff1 | string | 是 | 更新任务ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "636cb1fa-c9e2-4d5a-b52b-be16e5a5aff1",
				"taskName": "mysql_销售明细表单表更新",
				"startTime": 1670999037612,
				"endTime": 1670999040658,
				"state": 1,
				"costTime": 3046,
				"resultType": 1,
				"roleName": "admin",
				"baseTableExpect": 1,
				"baseTableFinish": 1,
				"analysisTableExpect": 0,
				"analysisTableFinish": 0,
				"relationExpect": 0,
				"relationFinish": 0,
				"triggerType": 1,
				"jobType": 3
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.taskInstanceId | 636cb1fa-c9e2-4d5a-b52b-be16e5a5aff1 | string | 更新任务ID |
| data.data.taskName | mysql_销售明细表单表更新 | string | 任务名称 |
| data.data.startTime | 1670999037612 | integer | 开始时间 |
| data.data.endTime | 1670999040658 | integer | 结束时间 |
| data.data.state | 1 | integer | 更新状态，1为已结束，2为正在运行中 |
| data.data.costTime | 3046 | integer | 耗时 |
| data.data.resultType | 1 | integer | 运行结果，1为全部成功，2为部分成功 |
| data.data.roleName | admin | string | 调用者 |
| data.data.baseTableExpect | 1 | integer | 基础表更新预期个数 |
| data.data.baseTableFinish | 1 | integer | 基础表更新完成个数 |
| data.data.analysisTableExpect | 0 | integer | 自助数据集更新预期个数 |
| data.data.analysisTableFinish | 0 | integer | 自助数据集更新完成个数 |
| data.data.relationExpect | 0 | integer | 关联更新预期个数 |
| data.data.relationFinish | 0 | integer | 关联更新完成个数 |
| data.data.triggerType | 1 | integer | 触发方式，1为手动，2为自动，3为内部 |
| data.data.jobType | 3 | integer | 任务类型， 1-全局，2-业务包， 3-数据集，4-关联 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI抽取更新任务管理历史运行情况查询

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:21:35

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/monitor/task/history/query

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"page": 1,
	"pageSize": 20,
	"queryCondition": {
		"taskName": "文件夹更新",
		"taskStartFrom": 0,
		"taskStartTo": 0,
		"taskEndFrom": 0,
		"taskEndTo": 0,
		"triggerTypes": [
			1,
			2
		],
		"roleNames": [
			"system",
			"admin",
			"API"
		],
		"taskStatusList": [
			1,
			2
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| page | 1 | integer | 是 | 页数 |
| pageSize | 20 | integer | 是 | 分页数量 |
| queryCondition | - | object | 是 | 查询条件 |
| queryCondition.taskName | 文件夹更新 | string | 是 | 任务名称 |
| queryCondition.taskStartFrom | 0 | integer | 是 | 任务开始时间范围起点，毫秒级时间戳同下 |
| queryCondition.taskStartTo | 0 | integer | 是 | 任务开始时间范围终点 |
| queryCondition.taskEndFrom | 0 | integer | 是 | 任务结束时间范围起点 |
| queryCondition.taskEndTo | 0 | integer | 是 | 任务结束时间范围终点 |
| queryCondition.triggerTypes | 1 | array | 是 | 触发方式 手动1 定时2 |
| queryCondition.roleNames | system | array | 是 | 触发人名称，如 system admin API |
| queryCondition.taskStatusList | 1 | array | 是 | 更新状态-已结束 1 正在更新中 2 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"monitorTaskBeanList": [
			{
				"taskInstanceId": "452e176b-23fe-456a-9e9c-87931530bf38",
				"taskName": "文件夹更新",
				"startTime": 1671006360102,
				"endTime": 1671006360653,
				"state": 1,
				"costTime": 551,
				"resultType": 1,
				"roleName": "admin",
				"baseTableExpect": 0,
				"baseTableFinish": 0,
				"analysisTableExpect": 0,
				"analysisTableFinish": 0,
				"relationExpect": 0,
				"relationFinish": 0,
				"triggerType": 1,
				"jobType": 2
			}
		],
		"totalSize": 8
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.monitorTaskBeanList | - | array | 任务列表 |
| data.monitorTaskBeanList.taskInstanceId | 452e176b-23fe-456a-9e9c-87931530bf38 | string | 任务ID |
| data.monitorTaskBeanList.taskName | 文件夹更新 | string | 任务名称 |
| data.monitorTaskBeanList.startTime | 1671006360102 | integer | 开始时间 |
| data.monitorTaskBeanList.endTime | 1671006360653 | integer | 结束时间 |
| data.monitorTaskBeanList.state | 1 | integer | 更新状态-已结束 1 正在更新中 2 |
| data.monitorTaskBeanList.costTime | 551 | integer | 更新耗时 |
| data.monitorTaskBeanList.resultType | 1 | integer | 运行结果 全部成功 1 部分成功 2 |
| data.monitorTaskBeanList.roleName | admin | string | 触发人名称 |
| data.monitorTaskBeanList.baseTableExpect | 0 | integer | 基础表更新预期个数 |
| data.monitorTaskBeanList.baseTableFinish | 0 | integer | 基础表更新完成个数 |
| data.monitorTaskBeanList.analysisTableExpect | 0 | integer | 自助数据集更新预期个数 |
| data.monitorTaskBeanList.analysisTableFinish | 0 | integer | 自助数据集更新完成个数 |
| data.monitorTaskBeanList.relationExpect | 0 | integer | 关联更新预期个数 |
| data.monitorTaskBeanList.relationFinish | 0 | integer | 关联更新完成个数 |
| data.monitorTaskBeanList.triggerType | 1 | integer | 触发方式 手动1 定时2 |
| data.monitorTaskBeanList.jobType | 2 | integer | 任务类型， 1-全局，2-业务包， 3-数据集，4-关联 |
| data.totalSize | 8 | integer | 任务总数 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI抽取更新任务管理当前运行情况查询

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:21:35

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/spider/update/monitor/task/running/query

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"page": 1,
	"pageSize": 20,
	"queryCondition": {
		"taskName": "t单表更新",
		"taskStartFrom": 0,
		"taskStartTo": 0,
		"taskEndFrom": 0,
		"taskEndTo": 0,
		"triggerTypes": [
			1,
			2
		],
		"roleNames": [
			"system",
			"admin",
			"API"
		],
		"taskStatusList": [
			1,
			2
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| page | 1 | integer | 是 | 页数 |
| pageSize | 20 | integer | 是 | 分页数量 |
| queryCondition | - | object | 是 | 查询条件 |
| queryCondition.taskName | t单表更新 | string | 是 | 任务名称 |
| queryCondition.taskStartFrom | 0 | integer | 是 | 任务开始时间范围起点，毫秒级时间戳同下 |
| queryCondition.taskStartTo | 0 | integer | 是 | 任务开始时间范围终点 |
| queryCondition.taskEndFrom | 0 | integer | 是 | 任务结束时间范围终点 |
| queryCondition.taskEndTo | 0 | integer | 是 | 任务结束时间范围终点 |
| queryCondition.triggerTypes | 1 | array | 是 | 触发方式 手动1 定时2 |
| queryCondition.roleNames | system | array | 是 | 触发人名称，如 system admin API |
| queryCondition.taskStatusList | 1 | array | 是 | 更新状态-已结束 1 正在更新中 2 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"monitorTaskBeanList": [
			{
				"taskInstanceId": "769b755b-2bf3-4da7-abc6-3141ae76fd05",
				"taskName": "t单表更新",
				"startTime": 1671006904146,
				"endTime": 0,
				"state": 2,
				"costTime": 0,
				"resultType": 2,
				"roleName": "admin",
				"baseTableExpect": 1,
				"baseTableFinish": 0,
				"analysisTableExpect": 0,
				"analysisTableFinish": 0,
				"relationExpect": 0,
				"relationFinish": 0,
				"triggerType": 1,
				"jobType": 3
			}
		],
		"totalSize": 1
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.monitorTaskBeanList | - | array | 任务列表 |
| data.monitorTaskBeanList.taskInstanceId | 769b755b-2bf3-4da7-abc6-3141ae76fd05 | string | 任务ID |
| data.monitorTaskBeanList.taskName | t单表更新 | string | 任务名称 |
| data.monitorTaskBeanList.startTime | 1671006904146 | integer | 开始时间 |
| data.monitorTaskBeanList.endTime | 0 | integer | 结束时间 |
| data.monitorTaskBeanList.state | 2 | integer | 更新状态-已结束 1 正在更新中 2 |
| data.monitorTaskBeanList.costTime | 0 | integer | 更新耗时 |
| data.monitorTaskBeanList.resultType | 2 | integer | 运行结果 全部成功 1 部分成功 2 |
| data.monitorTaskBeanList.roleName | admin | string | 触发人名称 |
| data.monitorTaskBeanList.baseTableExpect | 1 | integer | 基础表更新预期个数 |
| data.monitorTaskBeanList.baseTableFinish | 0 | integer | 基础表更新完成个数 |
| data.monitorTaskBeanList.analysisTableExpect | 0 | integer | 自助数据集更新预期个数 |
| data.monitorTaskBeanList.analysisTableFinish | 0 | integer | 自助数据集更新完成个数 |
| data.monitorTaskBeanList.relationExpect | 0 | integer | 关联更新预期个数 |
| data.monitorTaskBeanList.relationFinish | 0 | integer | 关联更新完成个数 |
| data.monitorTaskBeanList.triggerType | 1 | integer | 触发方式 手动1 定时2 |
| data.monitorTaskBeanList.jobType | 3 | integer | 任务类型， 1-全局，2-业务包， 3-数据集，4-关联 |
| data.totalSize | 1 | integer | 任务总数 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 获取所有文件夹

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/groups

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"id": "9b539b7d398641b389c9c33ee5fcabed",
			"name": "文件夹",
			"createBy": "admin",
			"packs": [
				{
					"id": "102a8a2183cf4304ae566abedca05c60",
					"name": "文件夹",
					"createBy": "admin",
					"packs": []
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据，业务包和分组的树 |
| data.id | 9b539b7d398641b389c9c33ee5fcabed | string | 文件夹id |
| data.name | 文件夹 | string | 文件夹名称 |
| data.createBy | admin | string | 创建者名称 |
| data.packs | - | array | 文件夹包含的文件夹列表 |
| data.packs.id | 102a8a2183cf4304ae566abedca05c60 | string | 子文件夹id |
| data.packs.name | 文件夹 | string | 子文件夹名称 |
| data.packs.createBy | admin | string | 创建者名称 |
| data.packs.packs | - | array | 子文件夹包含的文件夹列表 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 添加文件夹

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/pack/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"pGroupId": "9b539b7d398641b389c9c33ee5fcabed",
		"packName": "接口添加业务包"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| pGroupId | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 父文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"]；传""即为根文件夹 |
| packName | 接口添加业务包 | string | 是 | 文件夹名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"packId": "efe82b2cb0134158b8c7ed18e6ad965e",
				"packName": "接口添加业务包"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 业务包信息 |
| data.data.packId | efe82b2cb0134158b8c7ed18e6ad965e | string | 业务包ID |
| data.data.packName | 接口添加业务包 | string | 业务包名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 文件夹重命名

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/pack/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "00c6da1d8bee4deaa12d71e8b012444b",
		"newPackName": "业务包重命名"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | 00c6da1d8bee4deaa12d71e8b012444b | string | 是 | 文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"] |
| newPackName | 业务包重命名 | string | 是 | 新的文件夹名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除文件夹

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/pack/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "00c6da1d8bee4deaa12d71e8b012444b"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | 00c6da1d8bee4deaa12d71e8b012444b | string | 是 | 文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取文件夹相关信息

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/pack/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "9b539b7d398641b389c9c33ee5fcabed"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"id": "9b539b7d398641b389c9c33ee5fcabed",
				"name": "文件夹",
				"owner": "4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9",
				"createBy": "admin",
				"tables": [
					"c02127da02264264b1d3aec05646e661"
				],
				"tableList": [
					{
						"name": "c02127da02264264b1d3aec05646e661",
						"transferName": "sql数据集测试",
						"createBy": "admin"
					}
				]
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.id | 9b539b7d398641b389c9c33ee5fcabed | string | 业务包id |
| data.data.name | 文件夹 | string | 业务包名称 |
| data.data.owner | 4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9 | string | 业务包创建者ID |
| data.data.createBy | admin | string | 创建者用户 |
| data.data.tables | c02127da02264264b1d3aec05646e661 | array | 数据集名称列表 |
| data.data.tableList | - | array | 数据集列表 |
| data.data.tableList.name | c02127da02264264b1d3aec05646e661 | string | 数据集原始名 |
| data.data.tableList.transferName | sql数据集测试 | string | 数据集转义名 |
| data.data.tableList.createBy | admin | string | 创建者用户 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 我的分析

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 主题

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:31

> 更新时间: 2023-02-09 09:57:31

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 新建仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:31

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/create

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"pDashFolderId": "91963877617542e99e58dd88ad768c0c",
		"dashName": "新建仪表板测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| pDashFolderId | 91963877617542e99e58dd88ad768c0c | string | 是 | 父文件夹ID，这里是主题ID |
| dashName | 新建仪表板测试 | string | 是 | 仪表板名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "8e898c66b8704e1c91f8d4eeb94bc9e1",
				"dashName": "新建仪表板X"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | 8e898c66b8704e1c91f8d4eeb94bc9e1 | string | 仪表板ID |
| data.data.dashName | 新建仪表板X | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 重命名仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"dashId": "bd1c86aeb2674aaeb30f6554c9c77f14",
		"newDashName": "新的仪表板名称"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | bd1c86aeb2674aaeb30f6554c9c77f14 | string | 是 | 仪表板ID |
| newDashName | 新的仪表板名称 | string | 是 | 新的仪表板名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 删除仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/remove

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"dashId": "8e898c66b8704e1c91f8d4eeb94bc9e1"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | 8e898c66b8704e1c91f8d4eeb94bc9e1 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 另存为仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/saveas

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"fromDashId": "4c6209858e56437387f4383f7961ddb5",
		"toNewDashName": "另存为后的仪表板名称",
		"toParentDashFolderId": "fc802496d1734b8b9f6e1e391dd9f67b"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| fromDashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |
| toNewDashName | 另存为后的仪表板名称 | string | 是 | 另存为的仪表板名称 |
| toParentDashFolderId | fc802496d1734b8b9f6e1e391dd9f67b | string | 是 | 另存为的父 文件夹ID，这里是主题ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "bd1c86aeb2674aaeb30f6554c9c77f14",
				"dashName": "另存为后的仪表板名称"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | bd1c86aeb2674aaeb30f6554c9c77f14 | string | 仪表板ID |
| data.data.dashName | 另存为后的仪表板名称 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 获取仪表板相关信息

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/info

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"dashId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| dashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "27a285f2486b4f9e9efa91d7ac276030",
				"dashName": "新建仪表板"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 仪表板ID |
| data.data.dashName | 新建仪表板 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 获取当前用户的所有仪表板

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/user/all

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"dashId": "27a285f2486b4f9e9efa91d7ac276030",
			"dashName": "新建仪表板"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据 |
| data.dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 仪表板ID |
| data.dashName | 新建仪表板 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 另存为主题

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:32:30

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/dash/subject/saveas

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"fromDashId": "34c2a3b66cb2434f8b2efba232ec587c",
	"toNewSubjectName": "另存为后的主题名称",
	"toParentSubjectFolderId": "674c7dd15af845fb97633d4a732ca447"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| fromDashId | 34c2a3b66cb2434f8b2efba232ec587c | string | 是 | 仪表板ID |
| toNewSubjectName | 另存为后的主题名称 | string | 是 | 另存为后的主题名称 |
| toParentSubjectFolderId | 674c7dd15af845fb97633d4a732ca447 | string | 是 | 另存为的父 文件夹ID；传""即为当前用户我的分析根文件夹 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": {
		"subjectId": "295026cc48fa4d32a8b8839ed32be4ae",
		"subjectName": "另存为后的主题名称"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | object | - |
| data.subjectId | 295026cc48fa4d32a8b8839ed32be4ae | string | 主题ID |
| data.subjectName | 另存为后的主题名称 | string | 主题名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 组件

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 主题下添加空数据组件

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/widgets/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"subjectId": "91963877617542e99e58dd88ad768c0c",
	"widgetName": "分析组件2"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| subjectId | 91963877617542e99e58dd88ad768c0c | string | 是 | 主题ID |
| widgetName | 分析组件2 | string | 是 | 组件名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"widgetId": "c56d4a6ba8a147f6bba0b76f1793575f",
		"widgetName": "分析组件2"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.widgetId | c56d4a6ba8a147f6bba0b76f1793575f | string | 组件ID |
| data.widgetName | 分析组件2 | string | 组件名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 删除组件

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/widgets/delete

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "widgetId": "c56d4a6ba8a147f6bba0b76f1793575f"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| widgetId | c56d4a6ba8a147f6bba0b76f1793575f | string | 是 | 组件ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 重命名组件

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/widgets/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "widgetId": "d7362d7542124019acb2efa68dfc858e",
    "newWidgetName": "新的组件名称"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| widgetId | d7362d7542124019acb2efa68dfc858e | string | 是 | 组件ID |
| newWidgetName | 新的组件名称 | string | 是 | 新的组件名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 主题添加数据表

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/analysis/tables/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "tableName": "c02127da02264264b1d3aec05646e661",
  "parentId": "91963877617542e99e58dd88ad768c0c"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | c02127da02264264b1d3aec05646e661 | string | 是 | 数据集原始名 |
| parentId | 91963877617542e99e58dd88ad768c0c | string | 是 | 父主题ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"tableName": "f8283aeeab264682b85cb6496c697eb2",
		"transferName": "新的数据集名称"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.tableName | f8283aeeab264682b85cb6496c697eb2 | string | 数据集原始名 |
| data.transferName | 新的数据集名称 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 主题重命名数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/analysis/tables/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "tableName": "f8283aeeab264682b85cb6496c697eb2",
  "newTransferName": "测试重命名X"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | f8283aeeab264682b85cb6496c697eb2 | string | 是 | 数据集原始名 |
| newTransferName | 测试重命名X | string | 是 | 新的数据集转义名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 主题文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2023-02-09 09:57:32

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 我的分析所有文件夹分组

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/folders/all

**请求方式**

> GET

**Content-Type**

> form-data

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "__my_analysis__4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9",
		"name": "4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9",
		"createBy": "admin",
		"subjectFolders": [
			{
				"id": "674c7dd15af845fb97633d4a732ca447",
				"name": "文件夹",
				"createBy": "admin",
				"subjectFolders": [],
				"subjects": [
					{
						"id": "fc802496d1734b8b9f6e1e391dd9f67b",
						"name": "分析主题"
					}
				]
			}
		],
		"subjects": [
			{
				"id": "976b17d0510943a7986faff8b5ea7ab0",
				"name": "分析主题1"
			}
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | __my_analysis__4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9 | string | 文件夹id |
| data.name | 4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9 | string | 文件夹名称 |
| data.createBy | admin | string | 创建者用户名 |
| data.subjectFolders | - | array | 子文件夹列表 |
| data.subjectFolders.id | 674c7dd15af845fb97633d4a732ca447 | string | - |
| data.subjectFolders.name | 文件夹 | string | - |
| data.subjectFolders.createBy | admin | string | - |
| data.subjectFolders.subjectFolders | - | array | - |
| data.subjectFolders.subjects | - | array | - |
| data.subjectFolders.subjects.id | fc802496d1734b8b9f6e1e391dd9f67b | string | - |
| data.subjectFolders.subjects.name | 分析主题 | string | - |
| data.subjects | - | array | 子主题列表 |
| data.subjects.id | 976b17d0510943a7986faff8b5ea7ab0 | string | 主题ID |
| data.subjects.name | 分析主题1 | string | 主题名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取主题下资源

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/items

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "id": "91963877617542e99e58dd88ad768c0c"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| id | 91963877617542e99e58dd88ad768c0c | string | 是 | 主题ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "91963877617542e99e58dd88ad768c0c",
		"name": "分析主题",
		"tableNames": [
			"9d46d930cf824209ac0f3e9354f810a4"
		],
		"reportIds": [
			"4c6209858e56437387f4383f7961ddb5"
		],
		"widgetIds": [
			"d7362d7542124019acb2efa68dfc858e"
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | 91963877617542e99e58dd88ad768c0c | string | 主题ID |
| data.name | 分析主题 | string | 主题名称 |
| data.tableNames | 9d46d930cf824209ac0f3e9354f810a4 | array | 数据集原始名列表 |
| data.reportIds | 4c6209858e56437387f4383f7961ddb5 | array | 报表ID列表 |
| data.widgetIds | d7362d7542124019acb2efa68dfc858e | array | 组件ID列表 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 添加主题文件夹

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/folders/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "parentId": "674c7dd15af845fb97633d4a732ca447"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentId | 674c7dd15af845fb97633d4a732ca447 | string | 是 | 父文件夹ID；传""即为当前用户我的分析根文件夹 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "c4ccad589c794ff68cf7b4aad31c6bcb",
		"name": "文件夹"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | c4ccad589c794ff68cf7b4aad31c6bcb | string | 文件夹ID |
| data.name | 文件夹 | string | 文件夹名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 文件夹下添加主题

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/add

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "parentId": "674c7dd15af845fb97633d4a732ca447"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentId | 674c7dd15af845fb97633d4a732ca447 | string | 是 | 父文件夹ID；传""即为当前用户我的分析根文件夹 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "59696f96492b47cebf812740166886c8",
		"name": "分析主题"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | 59696f96492b47cebf812740166886c8 | string | 主题ID |
| data.name | 分析主题 | string | 主题名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 重命名主题文件夹

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/folders/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "id": "c4ccad589c794ff68cf7b4aad31c6bcb",
  "newName": "重命名文件夹"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| id | c4ccad589c794ff68cf7b4aad31c6bcb | string | 是 | - |
| newName | 重命名文件夹 | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作是否成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 重命名主题

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:32

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/rename

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "id": "0d20b23767ef4c17a59c3ebf392bc396",
  "newName": "重命名主题"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| id | 0d20b23767ef4c17a59c3ebf392bc396 | string | 是 | 主题ID |
| newName | 重命名主题 | string | 是 | 新的主题名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作是否成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除资源（主题或文件夹）

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-02-09 09:57:33

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/conf/subjects/delete

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "id": "e4e7688c475d4eab8a682cf3fe491479"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| id | e4e7688c475d4eab8a682cf3fe491479 | string | 是 | 主题或文件夹ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作是否成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 仪表板权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2023-05-06 10:24:18

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### BI 仪表板公共链接使用权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/publink/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板公共链接使用权限对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/publink/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板公共链接使用权限对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/publink/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-使用 |
| values.authValue | true | boolean | 是 | 权限值 true \|| false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 模板认证

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2023-05-06 10:24:18

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 角色权限认证

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:24

**准备工作：需要先开启模板认证全局设置-角色权限认证，并选择需要认证的模板。
查看权限关闭时，导出权限也要同时关闭；导出开启时，查看权限也要同时开启。**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### BI 仪表板模板认证权限查询对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"dashId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| dashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | 如果没有返回的，就是默认没权限 |
| data.data.authType | 0 | integer | 权限类型 0-查看 1-导出 |
| data.data.authValue | true | boolean | true - 有权限 false - 无权限 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
		"dashId": "4c6209858e56437387f4383f7961ddb5",
		"values": [
			{
				"authType": 0,
				"authValue": false
			},
			{
				"authType": 1,
				"authValue": false
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 否 | 职务ID |
| dashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-查看 1-导出 |
| values.authValue | false | boolean | 是 | true - 有权限 false - 无权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限查询对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"dashId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| dashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | 如果没有返回的，就是默认没权限 |
| data.data.authType | 0 | integer | 权限类型 0-查看 1-导出 |
| data.data.authValue | true | boolean | true - 有权限 false - 无权限 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"roleId": "测试角色",
		"dashId": "4c6209858e56437387f4383f7961ddb5",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roleId | 测试角色 | string | 是 | 角色ID |
| dashId | 07562a12bbe544008b09f066ed3f35d3 | string | 是 | 仪表板ID |
| values | - | object | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-查看 1-导出 |
| values.authValue | true | boolean | 是 | true - 有权限 false - 无权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限查询对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"dashId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| dashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | array | 如果没有返回的，就是默认没权限 |
| data.data.authType | 0 | integer | 权限类型 0-查看 1-导出 |
| data.data.authValue | true | boolean | true - 有权限 false - 无权限 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-06 10:24:18

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/dash/template/auth/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"userId": "test",
		"dashId": "4c6209858e56437387f4383f7961ddb5",
		"values": [
			{
				"authType": 0,
				"authValue": true
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| userId | test | string | 是 | 用户ID |
| dashId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-查看 1-导出 2-授权 |
| values.authValue | true | boolean | 是 | true - 有权限 false - 无权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 仪表板分享到目录

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:24

**权限管理-全局设置中需开启仪表板-分享到目录控制**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 分享给部门

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 仪表板可分享给哪些部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/deprole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/deprole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "roleId": "测试角色",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/deprole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "userId": "test",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| userId | test | string | 是 | 用户ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询仪表板可分享给部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/deprole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/deprole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"shareToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
	"roleId": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/deprole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"shareToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
	"userId": "test"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| userId | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 分享给角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 仪表板可分享给哪些角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/customrole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"shareToRoleId": "角色A",
	"depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
	"postId": "86df28cb-892c-4de4-87ac-3477113610cf",
	"values": [
		{
			"authType": 0,
			"authValue": true
		}
	]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些角色对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/customrole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
    "shareToRoleId": "角色A",
    "roleId": "测试角色",
    "values": [
        {
            "authType": 0,
            "authValue": true
        }
    ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些角色对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/customrole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToRoleId": "角色A",
  "userId": "test",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| userId | test | string | 是 | 用户ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询仪表板可分享给角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/customrole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToRoleId": "角色A",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给角色对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/customrole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
    "shareToRoleId": "角色A",
    "roleId": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给角色对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/sharedash/customrole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToRoleId": "角色A",
  "userId": "test"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| userId | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 资源协作

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:24

**权限管理-全局设置中需开启资源协作控制**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 协作给部门

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 资源协作可协作给哪些部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/deprole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/deprole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "roleId": "测试角色",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/deprole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "userId": "test",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| userId | test | string | 是 | 用户ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询资源协作可协作给部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/deprole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/deprole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "roleId": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/deprole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDepId": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "userId": "test"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDepId | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID |
| userId | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 协作给角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 资源协作可协作给哪些角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/customrole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRoleId": "角色A",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| values | - | array | 是 | 权限值 |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些角色对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/customrole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRoleId": "角色A",
  "roleId": "测试角色",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些角色对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/customrole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRoleId": "角色A",
  "userId": "test",
  "values": [
    {
      "authType": 0,
      "authValue": true
    }
  ]
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| userId | test | string | 是 | 用户ID或名称 |
| values | - | array | 是 | - |
| values.authType | 0 | integer | 是 | 权限类型 0-是否可以分享 |
| values.authValue | true | boolean | 是 | 权限值 true\||false |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2023-05-09 14:01:41

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询资源协作可协作给角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/customrole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRoleId": "角色A",
  "depId": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "postId": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| depId | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| postId | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给角色对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/customrole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRoleId": "角色A",
  "roleId": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| roleId | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给角色对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-09 14:01:41

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/bi/authority/cooperation/customrole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
  {
    "cooperateToRoleId": "角色A",
    "userId": "test"
  }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRoleId | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| userId | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": [
				{
					"authType": 0,
					"authValue": true
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | array | 操作成功 |
| data.data.authType | 0 | integer | 权限类型 0-是否可以分享 |
| data.data.authValue | true | boolean | 权限值 true\||false |

* 失败(404)

```javascript
暂无数据
```

**Query**

## BI6.x(V3)

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2025-06-04 15:23:15

**FineBI开放平台接口**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 数据权限

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2026-03-11 10:17:06

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### BI 数据公共文件夹权限对部门职务

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2025-05-29 17:32:49

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/pack/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"packId": "102a8a2183cf4304ae566abedca05c60",
		"authority": {
			"biData": true,
			"biView": true,
			"usePrivilege": true,
			"managePrivilege": true,
			"empowerPrivilege": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |
| authority.biView | true | boolean | 是 | 组件查看 BI7.0支持 |
| authority.usePrivilege | true | boolean | 是 | 使用 |
| authority.managePrivilege | true | boolean | 是 | 管理 |
| authority.empowerPrivilege | true | boolean | 是 | 授权 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共文件夹权限对角色

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2025-05-29 17:35:30

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/pack/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"packId": "102a8a2183cf4304ae566abedca05c60",
		"authority": {
			"biData": true,
			"biView": true,
			"usePrivilege": true,
			"managePrivilege": true,
			"empowerPrivilege": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |
| authority.biView | true | boolean | 是 | 组件查看 BI7.0支持 |
| authority.usePrivilege | true | boolean | 是 | 使用 |
| authority.managePrivilege | true | boolean | 是 | 管理 |
| authority.empowerPrivilege | true | boolean | 是 | 授权 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共文件夹权限对用户

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2025-05-29 17:36:11

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/pack/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"packId": "102a8a2183cf4304ae566abedca05c60",
		"authority": {
			"biData": true,
			"biView": true,
			"usePrivilege": true,
			"managePrivilege": true,
			"empowerPrivilege": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | - |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |
| authority.biView | true | boolean | 是 | 组件查看 BI7.0支持 |
| authority.usePrivilege | true | boolean | 是 | 使用 |
| authority.managePrivilege | true | boolean | 是 | 管理 |
| authority.empowerPrivilege | true | boolean | 是 | 授权 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对部门职务

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2025-05-29 17:36:43

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/table/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"authority": {
			"biData": true,
			"biView": true,
			"usePrivilege": true,
			"managePrivilege": true,
			"empowerPrivilege": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |
| authority.biView | true | boolean | 是 | 组件查看 BI7.0支持 |
| authority.usePrivilege | true | boolean | 是 | 使用 |
| authority.managePrivilege | true | boolean | 是 | 管理 |
| authority.empowerPrivilege | true | boolean | 是 | 授权 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对角色

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2025-05-29 17:39:27

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/table/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"authority": {
			"biData": true,
			"biView": true,
			"usePrivilege": true,
			"managePrivilege": true,
			"empowerPrivilege": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |
| authority.biView | true | boolean | 是 | 组件查看 BI7.0支持 |
| authority.usePrivilege | true | boolean | 是 | 使用 |
| authority.managePrivilege | true | boolean | 是 | 管理 |
| authority.empowerPrivilege | true | boolean | 是 | 授权 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 数据公共数据集权限对用户

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2025-05-29 17:39:52

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/table/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"authority": {
			"biData": true,
			"biView": true,
			"usePrivilege": true,
			"managePrivilege": true,
			"empowerPrivilege": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |
| authority.biView | true | boolean | 是 | 组件查看 BI7.0支持 |
| authority.usePrivilege | true | boolean | 是 | 使用 |
| authority.managePrivilege | true | boolean | 是 | 管理 |
| authority.empowerPrivilege | true | boolean | 是 | 授权 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 列权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2023-05-15 19:20:23

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据公共列权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 11:55:16

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/field/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
		"authority": {
			"biData": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共列权限对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/field/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
		"authority": {
			"biData": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 数据权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | 批量返回结果 |
| data.status | true | string | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共列权限对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/field/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
		"authority": {
			"biData": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |
| authority | - | object | 是 | 权限 |
| authority.biData | true | boolean | 是 | 组件数据 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:04:17

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/field/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或名称路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biData": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | - |
| data.data.biData | true | boolean | 数据 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/field/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biData": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | - |
| data.data.biData | true | boolean | 数据 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共列权限对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/field/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biData": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | - |
| data.data.biData | true | boolean | 数据 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 行权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2023-05-15 19:20:23

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据公共数据集行权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-25 20:23:46

> 更新时间: 2024-12-20 14:14:26

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"filter": {
			"type": "or",
			"filterValue": [
				{
					"type": "strIn",
					"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
					"filterValue": [
						"A1"
					]
				},
				{
					"type": "strIn",
					"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
					"filterValue": [
						"B"
					]
				}
			]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue.fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共数据集行权限对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"filter": {
			"type": "or",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strIn",
				"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue.fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据公共数据集行权限对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"tableName": "cc3fa97db37348f7b32231412b429053",
		"filter": {
			"type": "or",
			"filterValue": [{
				"type": "strIn",
				"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
				"filterValue": [
					"A1"
				]
			}, {
				"type": "strIn",
				"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
				"filterValue": [
					"B"
				]
			}]
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | - |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |
| filter | - | object | 是 | 行权限 |
| filter.type | or | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue | - | array | 是 | 过滤条件值 |
| filter.filterValue.type | strIn | string | 是 | 类型 and or strIn strNotIn |
| filter.filterValue.fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 是 | 字段ID |
| filter.filterValue.filterValue | A1 | array | 是 | 过滤条件值 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2026-08-27 14:20:32

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |
| data.data.id | - | string | 唯一标识符 |
| data.data.filterType | 35 | string | 类型，and:34  or:35  str_in:10 strNotIn:12 |
| data.data.filterValue | - | string | - |
| data.data.filterValue.fieldId | - | string | 字段id |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"760894855e8e4662\",\"filterType\":35,\"filterValue\":[{\"id\":\"5fb8da3700904e9e\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"925eb55cc1fe4159\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"760894855e8e4662","filterType":35,"filterValue":[{"id":"5fb8da3700904e9e","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"925eb55cc1fe4159","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集行权限对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

**全量覆盖的逻辑**

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/row/filter/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "{\"id\":\"737968e152a74190\",\"filterType\":34,\"filterValue\":[{\"id\":\"562a329931644711\",\"filterType\":10,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"A1\"]}},{\"id\":\"be7b0dc4072b46f6\",\"filterType\":12,\"fieldId\":\"api[5f]接口添加SQL表测试_canshu\",\"filterValue\":{\"type\":1,\"value\":[\"B\"]}}]}"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | {"id":"737968e152a74190","filterType":34,"filterValue":[{"id":"562a329931644711","filterType":10,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["A1"]}},{"id":"be7b0dc4072b46f6","filterType":12,"fieldId":"api[5f]接口添加SQL表测试_canshu","filterValue":{"type":1,"value":["B"]}}]} | string | 行权限 json串 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 公共数据权限获取

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-12-14 18:21:21

> 更新时间: 2024-06-07 15:37:24

**【开放平台-FineBI6.0接口】插件版本3.1.3-**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 数据获取公共文件夹权限对部门职务

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-12-14 18:21:30

> 更新时间: 2025-05-29 17:46:11

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/pack/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"packId": "9b539b7d398641b389c9c33ee5fcabed"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"managePrivilege": false,
				"biData": false,
				"empowerPrivilege": false,
				"biView": false,
				"usePrivilege": false
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 操作成功 |
| data.data.managePrivilege | false | boolean | 管理 |
| data.data.biData | false | boolean | 组件数据 |
| data.data.empowerPrivilege | false | boolean | 授权 |
| data.data.biView | false | boolean | 组件查看 BI7.0支持 |
| data.data.usePrivilege | false | boolean | 使用 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共文件夹权限对角色

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-12-14 18:21:30

> 更新时间: 2025-05-29 17:46:40

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/pack/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"packId": "9b539b7d398641b389c9c33ee5fcabed"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| packId | 102a8a2183cf4304ae566abedca05c60 | string | 是 | 文件夹ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"managePrivilege": false,
				"biData": false,
				"empowerPrivilege": false,
				"biView": false,
				"usePrivilege": false
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 操作成功 |
| data.data.managePrivilege | false | boolean | 组件数据 |
| data.data.biData | false | boolean | 组件数据 |
| data.data.empowerPrivilege | false | boolean | 授权 |
| data.data.biView | false | boolean | 组件查看 BI7.0支持 |
| data.data.usePrivilege | false | boolean | 使用 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共文件夹权限对用户

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-12-14 18:21:30

> 更新时间: 2025-05-29 17:47:01

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/pack/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"packId": "9b539b7d398641b389c9c33ee5fcabed"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| packId | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 文件夹ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"managePrivilege": false,
				"biData": false,
				"empowerPrivilege": false,
				"biView": false,
				"usePrivilege": false
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 操作成功 |
| data.data.managePrivilege | false | boolean | 组件数据 |
| data.data.biData | false | boolean | 组件数据 |
| data.data.empowerPrivilege | false | boolean | 授权 |
| data.data.biView | false | boolean | 组件查看 BI7.0支持 |
| data.data.usePrivilege | false | boolean | 使用 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集权限对部门职务

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-12-14 18:21:30

> 更新时间: 2025-05-29 17:47:30

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/table/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"managePrivilege": false,
				"biData": false,
				"empowerPrivilege": false,
				"biView": false,
				"usePrivilege": false
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 操作成功 |
| data.data.managePrivilege | true | boolean | 组件数据 |
| data.data.biData | true | boolean | 组件数据 |
| data.data.empowerPrivilege | true | boolean | 授权 |
| data.data.biView | true | boolean | 组件查看 BI7.0支持 |
| data.data.usePrivilege | true | boolean | 使用 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集权限对角色

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-12-14 18:21:30

> 更新时间: 2025-05-29 17:47:45

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/table/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"managePrivilege": false,
				"biData": false,
				"empowerPrivilege": false,
				"biView": false,
				"usePrivilege": false
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 操作成功 |
| data.data.managePrivilege | true | boolean | 组件数据 |
| data.data.biData | true | boolean | 组件数据 |
| data.data.empowerPrivilege | true | boolean | 授权 |
| data.data.biView | true | boolean | 组件查看 BI7.0支持 |
| data.data.usePrivilege | true | boolean | 使用 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 数据获取公共数据集权限对用户

> 创建人: JokerZy

> 更新人: Ivan.Guo

> 创建时间: 2023-12-14 18:21:30

> 更新时间: 2025-05-29 17:48:00

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/table/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"tableName": "cc3fa97db37348f7b32231412b429053"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| tableName | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"managePrivilege": true,
				"biData": true,
				"empowerPrivilege": true,
				"biView": true,
				"usePrivilege": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 操作成功 |
| data.data.managePrivilege | true | boolean | 组件数据 |
| data.data.biData | true | boolean | 组件数据 |
| data.data.empowerPrivilege | true | boolean | 授权 |
| data.data.biView | true | boolean | 组件查看 BI7.0支持 |
| data.data.usePrivilege | true | boolean | 使用 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 目录组件数据权限

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2026-01-13 18:59:10

> 更新时间: 2026-01-15 09:28:03

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 设置目录组件数据权限对用户

> 创建人: Ivan.Guo

> 更新人: icey

> 创建时间: 2026-01-14 11:25:44

> 更新时间: 2026-03-20 15:02:20

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dashboard/data/user/set

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
    {
        "user": "2", // 用户ID或名称
        "entry": "[\"分析主题\"]", // 目录ID或路径
        "biData": true // 组件数据权限
    },
    {
        "user": "3", // 用户ID或名称
        "entry": "[\"分析主题\"]", // 目录ID或路径
        "biData": false // 组件数据权限
    }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 0 | - | object | 是 | - |
| 0.user | 2 | string | 是 | 用户ID或名称 |
| 0.entry | ["分析主题"] | string | 是 | 目录ID或路径 |
| 0.biData | true | boolean | 是 | 组件数据权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	],
	"traceId": "53cb03e3-fb8a-4028-848a-1a43d2f95378"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | array | 返回数据 |
| data.status | true | boolean | - |
| data.data | success | array | 返回数据 |
| traceId | 53cb03e3-fb8a-4028-848a-1a43d2f95378 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 设置目录组件数据权限对角色

> 创建人: Ivan.Guo

> 更新人: icey

> 创建时间: 2026-01-14 11:39:30

> 更新时间: 2026-03-20 15:02:16

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dashboard/data/role/set

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
    {
        "role": "普通角色", // 角色ID或名称
        "entry": "[\"分析主题\"]", // 目录ID或路径
        "biData": true // 组件数据权限
    },
    {
        "role": "对外查看用户", // 角色ID或名称
        "entry": "[\"分析主题\"]", // 目录ID或路径
        "biData": false // 组件数据权限
    }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 0 | - | object | 是 | - |
| 0.role | 普通角色 | string | 是 | 角色ID或名称 |
| 0.entry | ["分析主题"] | string | 是 | 目录ID或路径 |
| 0.biData | true | boolean | 是 | 组件数据权限 |
| 1 | - | object | 是 | - |
| 1.role | 对外查看用户 | string | 是 | 角色ID或名称 |
| 1.entry | ["分析主题"] | string | 是 | 目录ID或路径 |
| 1.biData | false | boolean | 是 | 组件数据权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		},
		{
			"status": true,
			"data": "success"
		}
	],
	"traceId": "f2f27815-c354-4af3-854b-1a3bdbfd6648"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | array | 返回数据 |
| data.status | true | boolean | - |
| data.data | success | array | 返回数据 |
| traceId | f2f27815-c354-4af3-854b-1a3bdbfd6648 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 设置目录组件数据权限对部门职务

> 创建人: Ivan.Guo

> 更新人: icey

> 创建时间: 2026-01-14 11:45:14

> 更新时间: 2026-03-20 15:02:13

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dashboard/data/depost/set

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
    {
        "department": "6213d988-312a-4ee4-b0ae-5f290a4fe822", //部门ID
        "position": "86df28cb-892c-4de4-87ac-3477113610cf", //职务ID
        "entry": "[\"分析主题\"]",
        "biData": true // 组件数据权限
    },
    {
        "department": "9834d223-111a-4ee4-b0ae-5f290a4fe822", //部门ID
        "entry": "[\"分析主题\"]",
        "biData": false // 组件数据权限
    }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 0 | - | object | 是 | - |
| 0.department | 6213d988-312a-4ee4-b0ae-5f290a4fe822 | string | 是 | 部门ID |
| 0.position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID |
| 0.entry | ["分析主题"] | string | 是 | 目录ID或路径 |
| 0.biData | false | boolean | 是 | 组件数据权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		},
		{
			"status": true,
			"data": "success"
		}
	],
	"traceId": "f2f27815-c354-4af3-854b-1a3bdbfd6648"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | array | 返回数据 |
| data.status | true | boolean | - |
| data.data | success | array | 返回数据 |
| traceId | 53cb03e3-fb8a-4028-848a-1a43d2f95378 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 数据准备（公共数据）

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 新建SQL数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/{engineName}/table/sql

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"parentPack": "9b539b7d398641b389c9c33ee5fcabed",
		"connectionName": "mysql",
		"tableName": "api_接口添加SQL表测试",
		"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
		"paramSetting": [
			{
				"name": "uptype",
				"value": "add",
				"type": 16
			},
			{
				"name": "time",
				"value": "2022-08-29",
				"type": 48
			},
			{
				"name": "shoufei",
				"type": 32,
				"value": "10"
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentPack | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 文件夹ID或文件夹路径如[\"文件夹\", \"文件夹1\"] |
| connectionName | mysql | string | 是 | 数据连接名称 |
| tableName | api_接口添加SQL表测试 | string | 是 | 添加到数据准备里的数据集名称 |
| sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | 是 | sql 字符串 |
| paramSetting | - | array | 否 | 参数设置，需要和sql保持一致 |
| paramSetting.name | uptype | string | 是 | 参数名称 |
| paramSetting.value | add | string | 是 | 参数值 |
| paramSetting.type | 16 | integer | 是 | 参数类型 文本-16 时间-48 数值-32 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "cc3fa97db37348f7b32231412b429053",
				"transferName": "api_接口添加SQL表测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | cc3fa97db37348f7b32231412b429053 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 更新SQL数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/{engineName}/table/sql

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"connectionName": "mysql",
		"table": "cc3fa97db37348f7b32231412b429053",
		"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
		"paramSetting": [
			{
				"name": "uptype",
				"value": "add",
				"type": 16
			},
			{
				"name": "time",
				"value": "2022-11-30",
				"type": 48
			},
			{
				"name": "shoufei",
				"type": 32,
				"value": "10"
			}
		]
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| connectionName | mysql | string | 是 | 数据连接名称 |
| table | cc3fa97db37348f7b32231412b429053 | string | 是 | 数据集原始名或数据集路径如[\"文件夹\",  \"api_接口添加SQL表测试\"] |
| sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | 是 | sql 字符串 |
| paramSetting | - | array | 否 | 参数设置，需要和sql保持一致 |
| paramSetting.name | uptype | string | 是 | 参数名称 |
| paramSetting.value | add | string | 是 | 参数值 |
| paramSetting.type | 16 | integer | 是 | 参数类型 文本-16 时间-48 数值-32 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "cc3fa97db37348f7b32231412b429053",
				"transferName": "api_接口添加SQL表测试"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | cc3fa97db37348f7b32231412b429053 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取数据集相关信息

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/table/info?tables=["cc3fa97db37348f7b32231412b429053","8d93f61b173f4f4ab51d9c6d7dac9079"]

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tables | ["cc3fa97db37348f7b32231412b429053","8d93f61b173f4f4ab51d9c6d7dac9079"] | string | 是 | 数据集原始名列表或数据集路径列表如["[\"文件夹\",  \"api_接口添加SQL表测试\"]"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "cc3fa97db37348f7b32231412b429053",
				"transferName": "api_接口添加SQL表测试",
				"createBy": "admin",
				"fields": [
					{
						"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7]",
						"name": "销售单号",
						"transferName": "销售单号"
					},
					{
						"fieldId": "cc3fa97db37348f7b32231412b429053_[6536][8d39]",
						"name": "收费",
						"transferName": "收费"
					},
					{
						"fieldId": "cc3fa97db37348f7b32231412b429053_[9500][552e][65f6][95f4]",
						"name": "销售时间",
						"transferName": "销售时间"
					},
					{
						"fieldId": "cc3fa97db37348f7b32231412b429053_uptype",
						"name": "uptype",
						"transferName": "uptype"
					}
				],
				"sql": "select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei}",
				"connectionName": "mysql"
			}
		},
		{
			"status": true,
			"data": {
				"tableName": "8d93f61b173f4f4ab51d9c6d7dac9079",
				"transferName": "mysql_销售明细表",
				"createBy": "admin",
				"fields": [
					{
						"fieldId": "8d93f61b173f4f4ab51d9c6d7dac9079_[9500][552e][5355][53f7]",
						"name": "销售单号",
						"transferName": "销售单号1"
					},
					{
						"fieldId": "8d93f61b173f4f4ab51d9c6d7dac9079_[6536][8d39]",
						"name": "收费",
						"transferName": "收费"
					},
					{
						"fieldId": "8d93f61b173f4f4ab51d9c6d7dac9079_[9500][552e][65f6][95f4]",
						"name": "销售时间",
						"transferName": "销售时间"
					},
					{
						"fieldId": "8d93f61b173f4f4ab51d9c6d7dac9079_uptype",
						"name": "uptype",
						"transferName": "uptype"
					}
				],
				"dbTableName": "销售明细表",
				"connectionName": "mysql"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.tableName | cc3fa97db37348f7b32231412b429053 | string | 数据集原始名 |
| data.data.transferName | api_接口添加SQL表测试 | string | 数据集转义名 |
| data.data.createBy | admin | string | 创建者用户 |
| data.data.fields | - | array | 字段列表 |
| data.data.fields.fieldId | cc3fa97db37348f7b32231412b429053_[9500][552e][5355][53f7] | string | 字段ID |
| data.data.fields.name | 销售单号 | string | 字段原始名 |
| data.data.fields.transferName | 销售单号 | string | 字段转义名 |
| data.data.sql | select * from 销售明细表 where uptype = '${uptype}' and 销售时间 < '${time}' and 收费 > ${shoufei} | string | SQL数据集会返回sql |
| data.data.connectionName | mysql | string | SQL、DB数据集会返回数据连接名 |
| data.data.dbTableName | DB数据集的数据库表名 | string | DB数据集的数据库表名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 添加DB数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/{engineName}/table/db

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"parentPack": "9b539b7d398641b389c9c33ee5fcabed",
		"connectionName": "mysql",
		"dbTableName": "t"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentPack | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 文件夹ID或文件夹路径如[\"文件夹\", \"文件夹1\"] |
| connectionName | mysql | string | 是 | 数据连接名称 |
| dbTableName | t | string | 是 | 数据库表名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "mysql_t_D",
				"transferName": "mysql_t"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | mysql_t_D | string | 数据集原始名 |
| data.data.transferName | mysql_t | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除数据集

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/table?tables=["cc3fa97db37348f7b32231412b429053"]

**请求方式**

> DELETE

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tables | ["cc3fa97db37348f7b32231412b429053"] | string | 是 | 数据集原始名列表或数据集路径列表如["[\"文件夹\",  \"api_接口添加SQL表测试\"]"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据集修改转义名

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/table/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"table": "511431e9dfd74dbfbe405b67df2e859e",
		"newTransferName": "新的数据集名称122"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| table | 511431e9dfd74dbfbe405b67df2e859e | string | 是 | 数据集原始名或数据集路径如[\"文件夹\",  \"api_接口添加SQL表测试\"] |
| newTransferName | 新的数据集名称122 | string | 是 | 新的数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据集血缘分析

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/table/usage?tables=["cc3fa97db37348f7b32231412b429053"]

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tables | ["cc3fa97db37348f7b32231412b429053"] | string | 是 | 数据集原始名列表或数据集路径列表如["[\"文件夹\",  \"api_接口添加SQL表测试\"]"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"sonTables": [],
				"fatherTables": [
					{
						"tableName": "测试参数数据集",
						"createBy": "admin",
						"usage": [],
						"transferName": "测试参数数据集",
						"tables": []
					}
				],
				"usage": [
					{
						"id": "2479c18501bd497cbc99c373bd99be5d",
						"name": "新建仪表板2",
						"createBy": "admin"
					}
				],
				"tableName": "admin的自助数据集",
				"transferName": "admin的自助数据集",
				"createBy": "admin"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.sonTables | - | array | 关联子表列表，结构同父表列表 |
| data.data.fatherTables | - | array | 关联父表列表 |
| data.data.fatherTables.tableName | 测试参数数据集 | string | 数据集原始名 |
| data.data.fatherTables.createBy | admin | string | 创建者用户 |
| data.data.fatherTables.usage | - | array | 关联仪表板列表 |
| data.data.fatherTables.transferName | 测试参数数据集 | string | 数据集转义名 |
| data.data.fatherTables.tables | - | array | 关联数据集列表 |
| data.data.usage | - | array | 关联仪表板列表 |
| data.data.usage.id | 2479c18501bd497cbc99c373bd99be5d | string | 关联仪表板ID |
| data.data.usage.name | 新建仪表板2 | string | 关联仪表板名称 |
| data.data.usage.createBy | admin | string | 创建者用户 |
| data.data.tableName | admin的自助数据集 | string | 数据集原始名 |
| data.data.transferName | admin的自助数据集 | string | 数据集转义名 |
| data.data.createBy | admin | string | 创建者用户 |

* 失败(201)

```javascript
暂无数据
```

**Query**

##### 添加服务器数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/{engineName}/table/dataset

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"parentPack": "9b539b7d398641b389c9c33ee5fcabed",
		"datasetName": "test"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentPack | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 文件夹ID或文件夹路径如[\"文件夹\", \"文件夹1\"] |
| datasetName | test | string | 是 | 服务器数据集名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"tableName": "__FR_BI_SERVER_SQL___fine_record_login_D",
				"transferName": "__FR_BI_SERVER_SQL___fine_record_login"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 数据集信息 |
| data.data.tableName | __FR_BI_SERVER_SQL___fine_record_login_D | string | 数据集原始名 |
| data.data.transferName | __FR_BI_SERVER_SQL___fine_record_login | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 抽取更新

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 触发全局更新

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/spider/update/all

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"taskInstanceId": "c96790d6-19d0-4c67-8188-7547b69d7c12"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.taskInstanceId | c96790d6-19d0-4c67-8188-7547b69d7c12 | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 触发业务包更新

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/spider/update/pack

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"packId": "cc3f64cdade64551a557dafda89b4c2b"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packId | cc3f64cdade64551a557dafda89b4c2b | string | 是 | 业务包ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "25cbd26f-0688-4aec-a85d-78e896494fbe"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.taskInstanceId | 25cbd26f-0688-4aec-a85d-78e896494fbe | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 触发数据集更新

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/spider/update/table

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"tableName": "8d93f61b173f4f4ab51d9c6d7dac9079",
		"fullLoad": true
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | 8d93f61b173f4f4ab51d9c6d7dac9079 | string | 是 | 数据集原始名 |
| fullLoad | true | boolean | 否 | fullload 参数为 false 表示增量更新，true 为全量更新，不填改参数默认为 true 。 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "e03e26f7-85ab-43c7-a635-4e670a1bdb4d"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 批量返回结果 |
| data.data.taskInstanceId | e03e26f7-85ab-43c7-a635-4e670a1bdb4d | string | 更新任务ID |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 查询更新任务状态

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2026-01-30 16:14:08

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/spider/update/instance/info?taskInstanceIds=["31ff8520-1422-4e3b-aad3-a71744067a28"]

**请求方式**

> GET

**Content-Type**

> json

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| taskInstanceIds | ["31ff8520-1422-4e3b-aad3-a71744067a28"] | string | 是 | 任务ID列表 |

**请求Body参数**

```javascript
暂无数据
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"taskInstanceId": "636cb1fa-c9e2-4d5a-b52b-be16e5a5aff1",
				"taskName": "mysql_销售明细表单表更新",
				"startTime": 1670999037612,
				"endTime": 1670999040658,
				"state": 1,
				"costTime": 3046,
				"resultType": 1,
				"roleName": "admin",
				"baseTableExpect": 1,
				"baseTableFinish": 1,
				"analysisTableExpect": 0,
				"analysisTableFinish": 0,
				"relationExpect": 0,
				"relationFinish": 0,
				"triggerType": 1,
				"jobType": 3
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.taskInstanceId | 636cb1fa-c9e2-4d5a-b52b-be16e5a5aff1 | string | 更新任务ID |
| data.data.taskName | mysql_销售明细表单表更新 | string | 任务名称 |
| data.data.startTime | 1670999037612 | integer | 开始时间 |
| data.data.endTime | 1670999040658 | integer | 结束时间 |
| data.data.state | 1 | integer | 更新状态，1为已结束，2为正在运行中,3等待中，4取消 |
| data.data.costTime | 3046 | integer | 耗时 |
| data.data.resultType | 1 | integer | 运行结果，1为全部成功，2为部分成功 |
| data.data.roleName | admin | string | 调用者 |
| data.data.baseTableExpect | 1 | integer | 基础表更新预期个数 |
| data.data.baseTableFinish | 1 | integer | 基础表更新完成个数 |
| data.data.analysisTableExpect | 0 | integer | 自助数据集更新预期个数 |
| data.data.analysisTableFinish | 0 | integer | 自助数据集更新完成个数 |
| data.data.relationExpect | 0 | integer | 关联更新预期个数 |
| data.data.relationFinish | 0 | integer | 关联更新完成个数 |
| data.data.triggerType | 1 | integer | 触发方式，1为手动，2为自动，3为内部 |
| data.data.jobType | 3 | integer | 任务类型， 1-全局，2-业务包， 3-数据集，4-关联 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI抽取更新任务管理历史运行情况查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/spider/update/monitor/task/history/query

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"page": 1,
	"pageSize": 20,
	"queryCondition": {
		"taskName": "文件夹更新",
		"taskStartFrom": 0,
		"taskStartTo": 0,
		"taskEndFrom": 0,
		"taskEndTo": 0,
		"triggerTypes": [
			1,
			2
		],
		"roleNames": [
			"system",
			"admin",
			"API"
		],
		"taskStatusList": [
			1,
			2
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| page | 1 | integer | 是 | 页数 |
| pageSize | 20 | integer | 是 | 分页数量 |
| queryCondition | - | object | 是 | 查询条件 |
| queryCondition.taskName | 文件夹更新 | string | 是 | 任务名称 |
| queryCondition.taskStartFrom | 0 | integer | 是 | 任务开始时间范围起点，毫秒级时间戳同下 |
| queryCondition.taskStartTo | 0 | integer | 是 | 任务开始时间范围终点 |
| queryCondition.taskEndFrom | 0 | integer | 是 | 任务结束时间范围起点 |
| queryCondition.taskEndTo | 0 | integer | 是 | 任务结束时间范围终点 |
| queryCondition.triggerTypes | 1 | array | 是 | 触发方式 手动1 定时2 |
| queryCondition.roleNames | system | array | 是 | 触发人名称，如 system admin API |
| queryCondition.taskStatusList | 1 | array | 是 | 更新状态-已结束 1 正在更新中 2 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"monitorTaskBeanList": [
			{
				"taskInstanceId": "452e176b-23fe-456a-9e9c-87931530bf38",
				"taskName": "文件夹更新",
				"startTime": 1671006360102,
				"endTime": 1671006360653,
				"state": 1,
				"costTime": 551,
				"resultType": 1,
				"roleName": "admin",
				"baseTableExpect": 0,
				"baseTableFinish": 0,
				"analysisTableExpect": 0,
				"analysisTableFinish": 0,
				"relationExpect": 0,
				"relationFinish": 0,
				"triggerType": 1,
				"jobType": 2
			}
		],
		"totalSize": 8
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.monitorTaskBeanList | - | array | 任务列表 |
| data.monitorTaskBeanList.taskInstanceId | 452e176b-23fe-456a-9e9c-87931530bf38 | string | 任务ID |
| data.monitorTaskBeanList.taskName | 文件夹更新 | string | 任务名称 |
| data.monitorTaskBeanList.startTime | 1671006360102 | integer | 开始时间 |
| data.monitorTaskBeanList.endTime | 1671006360653 | integer | 结束时间 |
| data.monitorTaskBeanList.state | 1 | integer | 更新状态-已结束 1 正在更新中 2 |
| data.monitorTaskBeanList.costTime | 551 | integer | 更新耗时 |
| data.monitorTaskBeanList.resultType | 1 | integer | 运行结果 全部成功 1 部分成功 2 |
| data.monitorTaskBeanList.roleName | admin | string | 触发人名称 |
| data.monitorTaskBeanList.baseTableExpect | 0 | integer | 基础表更新预期个数 |
| data.monitorTaskBeanList.baseTableFinish | 0 | integer | 基础表更新完成个数 |
| data.monitorTaskBeanList.analysisTableExpect | 0 | integer | 自助数据集更新预期个数 |
| data.monitorTaskBeanList.analysisTableFinish | 0 | integer | 自助数据集更新完成个数 |
| data.monitorTaskBeanList.relationExpect | 0 | integer | 关联更新预期个数 |
| data.monitorTaskBeanList.relationFinish | 0 | integer | 关联更新完成个数 |
| data.monitorTaskBeanList.triggerType | 1 | integer | 触发方式 手动1 定时2 |
| data.monitorTaskBeanList.jobType | 2 | integer | 任务类型， 1-全局，2-业务包， 3-数据集，4-关联 |
| data.totalSize | 8 | integer | 任务总数 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI抽取更新任务管理当前运行情况查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/spider/update/monitor/task/running/query

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"page": 1,
	"pageSize": 20,
	"queryCondition": {
		"taskName": "t单表更新",
		"taskStartFrom": 0,
		"taskStartTo": 0,
		"taskEndFrom": 0,
		"taskEndTo": 0,
		"triggerTypes": [
			1,
			2
		],
		"roleNames": [
			"system",
			"admin",
			"API"
		],
		"taskStatusList": [
			1,
			2
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| page | 1 | integer | 是 | 页数 |
| pageSize | 20 | integer | 是 | 分页数量 |
| queryCondition | - | object | 是 | 查询条件 |
| queryCondition.taskName | t单表更新 | string | 是 | 任务名称 |
| queryCondition.taskStartFrom | 0 | integer | 是 | 任务开始时间范围起点，毫秒级时间戳同下 |
| queryCondition.taskStartTo | 0 | integer | 是 | 任务开始时间范围终点 |
| queryCondition.taskEndFrom | 0 | integer | 是 | 任务结束时间范围终点 |
| queryCondition.taskEndTo | 0 | integer | 是 | 任务结束时间范围终点 |
| queryCondition.triggerTypes | 1 | array | 是 | 触发方式 手动1 定时2 |
| queryCondition.roleNames | system | array | 是 | 触发人名称，如 system admin API |
| queryCondition.taskStatusList | 1 | array | 是 | 更新状态-已结束 1 正在更新中 2 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"monitorTaskBeanList": [
			{
				"taskInstanceId": "769b755b-2bf3-4da7-abc6-3141ae76fd05",
				"taskName": "t单表更新",
				"startTime": 1671006904146,
				"endTime": 0,
				"state": 2,
				"costTime": 0,
				"resultType": 2,
				"roleName": "admin",
				"baseTableExpect": 1,
				"baseTableFinish": 0,
				"analysisTableExpect": 0,
				"analysisTableFinish": 0,
				"relationExpect": 0,
				"relationFinish": 0,
				"triggerType": 1,
				"jobType": 3
			}
		],
		"totalSize": 1
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.monitorTaskBeanList | - | array | 任务列表 |
| data.monitorTaskBeanList.taskInstanceId | 769b755b-2bf3-4da7-abc6-3141ae76fd05 | string | 任务ID |
| data.monitorTaskBeanList.taskName | t单表更新 | string | 任务名称 |
| data.monitorTaskBeanList.startTime | 1671006904146 | integer | 开始时间 |
| data.monitorTaskBeanList.endTime | 0 | integer | 结束时间 |
| data.monitorTaskBeanList.state | 2 | integer | 更新状态-已结束 1 正在更新中 2 |
| data.monitorTaskBeanList.costTime | 0 | integer | 更新耗时 |
| data.monitorTaskBeanList.resultType | 2 | integer | 运行结果 全部成功 1 部分成功 2 |
| data.monitorTaskBeanList.roleName | admin | string | 触发人名称 |
| data.monitorTaskBeanList.baseTableExpect | 1 | integer | 基础表更新预期个数 |
| data.monitorTaskBeanList.baseTableFinish | 0 | integer | 基础表更新完成个数 |
| data.monitorTaskBeanList.analysisTableExpect | 0 | integer | 自助数据集更新预期个数 |
| data.monitorTaskBeanList.analysisTableFinish | 0 | integer | 自助数据集更新完成个数 |
| data.monitorTaskBeanList.relationExpect | 0 | integer | 关联更新预期个数 |
| data.monitorTaskBeanList.relationFinish | 0 | integer | 关联更新完成个数 |
| data.monitorTaskBeanList.triggerType | 1 | integer | 触发方式 手动1 定时2 |
| data.monitorTaskBeanList.jobType | 3 | integer | 任务类型， 1-全局，2-业务包， 3-数据集，4-关联 |
| data.totalSize | 1 | integer | 任务总数 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2023-05-15 19:20:22

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 获取所有文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/groups

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"id": "9b539b7d398641b389c9c33ee5fcabed",
			"name": "文件夹",
			"createBy": "admin",
			"packs": [
				{
					"id": "102a8a2183cf4304ae566abedca05c60",
					"name": "文件夹",
					"createBy": "admin",
					"packs": []
				}
			]
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据，业务包和分组的树 |
| data.id | 9b539b7d398641b389c9c33ee5fcabed | string | 文件夹id |
| data.name | 文件夹 | string | 文件夹名称 |
| data.createBy | admin | string | 创建者名称 |
| data.packs | - | array | 文件夹包含的文件夹列表 |
| data.packs.id | 102a8a2183cf4304ae566abedca05c60 | string | 子文件夹id |
| data.packs.name | 文件夹 | string | 子文件夹名称 |
| data.packs.createBy | admin | string | 创建者名称 |
| data.packs.packs | - | array | 子文件夹包含的文件夹列表 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 添加文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/pack

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"parentPack": "9b539b7d398641b389c9c33ee5fcabed",
		"packName": "接口添加业务包"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentPack | 9b539b7d398641b389c9c33ee5fcabed | string | 是 | 父文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"] |
| packName | 接口添加业务包 | string | 是 | 文件夹名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"packId": "efe82b2cb0134158b8c7ed18e6ad965e",
				"packName": "接口添加业务包"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 业务包信息 |
| data.data.packId | efe82b2cb0134158b8c7ed18e6ad965e | string | 业务包ID |
| data.data.packName | 接口添加业务包 | string | 业务包名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 文件夹重命名

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/pack/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"pack": "5bb3428283004f6ea2b91b915bd12a5a",
		"newPackName": "业务包重命名"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| pack | 5bb3428283004f6ea2b91b915bd12a5a | string | 是 | 文件夹ID 或文件夹路径如[\"文件夹\", \"文件夹1\", \"文件夹2\"] |
| newPackName | 业务包重命名 | string | 是 | 新的文件夹名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/pack?packs=["ee5466019bbb420995655f2e0c559f15"]

**请求方式**

> DELETE

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packs | ["ee5466019bbb420995655f2e0c559f15"] | string | 是 | 文件夹ID列表或文件夹路径列表如["[\"文件夹\", \"接口添加业务包\"]"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取文件夹相关信息

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/pack/info?packs=["ee5466019bbb420995655f2e0c559f15"]

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| packs | ["ee5466019bbb420995655f2e0c559f15"] | string | 是 | 文件夹ID列表或文件夹路径列表如["[\"文件夹\", \"接口添加业务包\"]"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"id": "9b539b7d398641b389c9c33ee5fcabed",
				"name": "文件夹",
				"owner": "4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9",
				"createBy": "admin",
				"tables": [
					"c02127da02264264b1d3aec05646e661"
				],
				"tableList": [
					{
						"name": "c02127da02264264b1d3aec05646e661",
						"transferName": "sql数据集测试",
						"createBy": "admin"
					}
				]
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.id | 9b539b7d398641b389c9c33ee5fcabed | string | 业务包id |
| data.data.name | 文件夹 | string | 业务包名称 |
| data.data.owner | 4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9 | string | 业务包创建者ID |
| data.data.createBy | admin | string | 创建者用户 |
| data.data.tables | c02127da02264264b1d3aec05646e661 | array | 数据集名称列表 |
| data.data.tableList | - | array | 数据集列表 |
| data.data.tableList.name | c02127da02264264b1d3aec05646e661 | string | 数据集原始名 |
| data.data.tableList.transferName | sql数据集测试 | string | 数据集转义名 |
| data.data.tableList.createBy | admin | string | 创建者用户 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 我的分析

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-03-27 11:00:43

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 主题文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2023-05-15 19:20:22

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 我的分析所有文件夹分组

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects/folders/all

**请求方式**

> GET

**Content-Type**

> form-data

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "__my_analysis__4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9",
		"name": "4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9",
		"createBy": "admin",
		"subjectFolders": [
			{
				"id": "674c7dd15af845fb97633d4a732ca447",
				"name": "文件夹",
				"createBy": "admin",
				"subjectFolders": [],
				"subjects": [
					{
						"id": "fc802496d1734b8b9f6e1e391dd9f67b",
						"name": "分析主题"
					}
				]
			}
		],
		"subjects": [
			{
				"id": "976b17d0510943a7986faff8b5ea7ab0",
				"name": "分析主题1"
			}
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | __my_analysis__4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9 | string | 文件夹id |
| data.name | 4fb31f9f-c2db-4bfd-9e4c-f80caf9bd9d9 | string | 文件夹名称 |
| data.createBy | admin | string | 创建者用户名 |
| data.subjectFolders | - | array | 子文件夹列表 |
| data.subjectFolders.id | 674c7dd15af845fb97633d4a732ca447 | string | - |
| data.subjectFolders.name | 文件夹 | string | - |
| data.subjectFolders.createBy | admin | string | - |
| data.subjectFolders.subjectFolders | - | array | - |
| data.subjectFolders.subjects | - | array | - |
| data.subjectFolders.subjects.id | fc802496d1734b8b9f6e1e391dd9f67b | string | - |
| data.subjectFolders.subjects.name | 分析主题 | string | - |
| data.subjects | - | array | 子主题列表 |
| data.subjects.id | 976b17d0510943a7986faff8b5ea7ab0 | string | 主题ID |
| data.subjects.name | 分析主题1 | string | 主题名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 获取主题下资源

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects/items?subject=91963877617542e99e58dd88ad768c0c

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| subject | 91963877617542e99e58dd88ad768c0c | string | 是 | 主题ID或路径如["重命名主题"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "91963877617542e99e58dd88ad768c0c",
		"name": "分析主题",
		"tableNames": [
			"9d46d930cf824209ac0f3e9354f810a4"
		],
		"reportIds": [
			"4c6209858e56437387f4383f7961ddb5"
		],
		"widgetIds": [
			"d7362d7542124019acb2efa68dfc858e"
		]
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | 91963877617542e99e58dd88ad768c0c | string | 主题ID |
| data.name | 分析主题 | string | 主题名称 |
| data.tableNames | 9d46d930cf824209ac0f3e9354f810a4 | array | 数据集原始名列表 |
| data.reportIds | 4c6209858e56437387f4383f7961ddb5 | array | 报表ID列表 |
| data.widgetIds | d7362d7542124019acb2efa68dfc858e | array | 组件ID列表 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 添加主题文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects/folder

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "parentFolder": "674c7dd15af845fb97633d4a732ca447"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentFolder | 674c7dd15af845fb97633d4a732ca447 | string | 是 | - |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "c4ccad589c794ff68cf7b4aad31c6bcb",
		"name": "文件夹"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | c4ccad589c794ff68cf7b4aad31c6bcb | string | 文件夹ID |
| data.name | 文件夹 | string | 文件夹名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 文件夹下添加主题

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "parentFolder": "674c7dd15af845fb97633d4a732ca447"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentFolder | 674c7dd15af845fb97633d4a732ca447 | string | 是 | 父文件夹ID或路径；传""即为当前用户我的分析根文件夹 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"id": "59696f96492b47cebf812740166886c8",
		"name": "分析主题"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.id | c4ccad589c794ff68cf7b4aad31c6bcb | string | 主题ID |
| data.name | 文件夹 | string | 主题名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 重命名主题文件夹

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects/folders/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "folder": "c4ccad589c794ff68cf7b4aad31c6bcb",
  "newFolderName": "重命名文件夹"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| folder | c4ccad589c794ff68cf7b4aad31c6bcb | string | 是 | 文件夹ID或路径 |
| newFolderName | 重命名文件夹 | string | 是 | 文件夹名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作是否成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 重命名主题

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "subject": "0d20b23767ef4c17a59c3ebf392bc396",
  "newSubjectName": "重命名主题"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| subject | 0d20b23767ef4c17a59c3ebf392bc396 | string | 是 | 主题ID或路径 |
| newSubjectName | 重命名主题 | string | 是 | 新的主题名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作是否成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 删除资源（主题或文件夹）

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/subjects?folder=92176c1bfa9d40f394e2769c3ffe955d&subject=89d5e6c8325d4b4eb804e886f235431b

**请求方式**

> DELETE

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| folder | 92176c1bfa9d40f394e2769c3ffe955d | string | 否 | 文件夹ID或路径；和subject参数同时只传一个 |
| subject | 89d5e6c8325d4b4eb804e886f235431b | string | 否 | 主题ID或路径 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作是否成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 主题

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 新建仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"parentSubject": "91963877617542e99e58dd88ad768c0c",
		"biReportName": "新建仪表板测试"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentSubject | 91963877617542e99e58dd88ad768c0c | string | 是 | 父主题ID或主题文件夹路径 |
| biReportName | 新建仪表板测试 | string | 是 | 仪表板名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biReportId": "ba5c3cffb11140cab31a5815c28b70f6",
				"biReportName": "新建仪表板测试1"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.biReportId | ba5c3cffb11140cab31a5815c28b70f6 | string | 仪表板ID |
| data.data.biReportName | 新建仪表板测试1 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 重命名仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"biReport": "34c2a3b66cb2434f8b2efba232ec587c",
		"newBiReportName": "新的仪表板名称"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| biReport | 34c2a3b66cb2434f8b2efba232ec587c | string | 是 | 仪表板ID或路径 |
| newBiReportName | 新的仪表板名称 | string | 是 | 新的仪表板名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 删除仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash?biReports=["558bf95aa1854b03969dbb473036e2c7"]

**请求方式**

> DELETE

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| biReports | ["558bf95aa1854b03969dbb473036e2c7"] | string | 是 | 仪表板ID或路径列表 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": true
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | true | boolean | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 另存为仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash/saveas

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"biReport": "4c6209858e56437387f4383f7961ddb5",
		"newBiReportName": "另存为后的仪表板名称",
		"parentSubject": "fc802496d1734b8b9f6e1e391dd9f67b"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| biReport | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID或路径 |
| newBiReportName | 另存为后的仪表板名称 | string | 是 | 仪表板名称 |
| parentSubject | fc802496d1734b8b9f6e1e391dd9f67b | string | 是 | 主题ID或路径 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "bd1c86aeb2674aaeb30f6554c9c77f14",
				"dashName": "另存为后的仪表板名称"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | bd1c86aeb2674aaeb30f6554c9c77f14 | string | 仪表板ID |
| data.data.dashName | 另存为后的仪表板名称 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 获取仪表板相关信息

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash/info?biReports=["4c6209858e56437387f4383f7961ddb5", "[\"重命名主题\", \"新建仪表板控件测试\"]"]

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| biReports | ["4c6209858e56437387f4383f7961ddb5", "[\"重命名主题\", \"新建仪表板控件测试\"]"] | string | 是 | 仪表板ID或路径列表 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": {
				"dashId": "27a285f2486b4f9e9efa91d7ac276030",
				"dashName": "新建仪表板"
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 仪表板ID |
| data.data.dashName | 新建仪表板 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 获取当前用户的所有仪表板

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash/user/all

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"dashId": "27a285f2486b4f9e9efa91d7ac276030",
			"dashName": "新建仪表板"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据 |
| data.dashId | 27a285f2486b4f9e9efa91d7ac276030 | string | 仪表板ID |
| data.dashName | 新建仪表板 | string | 仪表板名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 另存为主题

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/dash/subject/saveas

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"biReport": "34c2a3b66cb2434f8b2efba232ec587c",
	"newSubjectName": "另存为后的主题名称",
	"parentFolder": "674c7dd15af845fb97633d4a732ca447"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| biReport | 34c2a3b66cb2434f8b2efba232ec587c | string | 是 | 仪表板ID或路径如"[\"重命名主题\", \"新建仪表板控件测试\"]" |
| newSubjectName | 另存为后的主题名称 | string | 是 | 主题名称 |
| parentFolder | 674c7dd15af845fb97633d4a732ca447 | string | 是 | 父文件夹ID或路径；传""即为当前用户我的分析根文件夹 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": {
		"subjectId": "295026cc48fa4d32a8b8839ed32be4ae",
		"subjectName": "另存为后的主题名称"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | object | - |
| data.subjectId | 295026cc48fa4d32a8b8839ed32be4ae | string | 主题ID |
| data.subjectName | 另存为后的主题名称 | string | 主题名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 获取发布信息

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2025-04-02 17:49:07

> 更新时间: 2025-04-02 18:08:03

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/publish/info?templateIds=["templateId"]

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| templateIds | ["templateId"] | string | 是 | 发布ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"templateId": "b09c6a4b28d74f73a1853e03c8ff20de",
				"resources": [
					{
						"id": "7f1c919c676e4b648f3ed7db548be7a5",
						"name": "仪表板",
						"itemType": 1,
						"tableType": 0
					},
					{
						"id": "cb00618204c44f19904c7ac0e734ed91",
						"name": "组件",
						"itemType": 2,
						"tableType": 0
					},
					{
						"id": "3452abe0f92e41e8b3b60a5378d920cf",
						"name": "分析组件1",
						"itemType": 2,
						"tableType": 0
					},
					{
						"id": "acd83c0c9bf946d9bc8b7f1300882782",
						"name": "分析组件2",
						"itemType": 2,
						"tableType": 0
					}
				]
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | array | 返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 返回数据 |
| data.data.templateId | b09c6a4b28d74f73a1853e03c8ff20de | string | 发布 |
| data.data.resources | - | array | 资源信息 |
| data.data.resources.id | 7f1c919c676e4b648f3ed7db548be7a5 | string | 仪表板ID/组件ID |
| data.data.resources.name | 仪表板 | string | 仪表板名称/组件名称 |
| data.data.resources.itemType | 1 | number | 资源类型 |
| data.data.resources.tableType | 0 | number | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 组件

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2023-05-15 19:20:22

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 主题下添加空数据组件

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-12 15:35:46

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/widgets

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"parentSubject": "91963877617542e99e58dd88ad768c0c",
	"widgetName": "分析组件2",
	"tableName":"511431e9dfd74dbfbe405b67df2e859e"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| parentSubject | 91963877617542e99e58dd88ad768c0c | string | 是 | 主题ID或路径 |
| widgetName | 分析组件2 | string | 是 | 组件名称 |
| tableName | 511431e9dfd74dbfbe405b67df2e859e | string | 是 | 数据集原始名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"widgetId": "c56d4a6ba8a147f6bba0b76f1793575f",
		"widgetName": "分析组件2"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.widgetId | c56d4a6ba8a147f6bba0b76f1793575f | string | 组件ID |
| data.widgetName | 分析组件2 | string | 组件名称 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 删除组件

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/widgets?widget=88b9b4051cf84bdebd10258acfb0b516

**请求方式**

> DELETE

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| widget | 88b9b4051cf84bdebd10258acfb0b516 | string | 是 | 组件ID或路径 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 重命名组件

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/widgets/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "widget": "d7362d7542124019acb2efa68dfc858e",
    "newWidgetName": "新的组件名称"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| widget | d7362d7542124019acb2efa68dfc858e | string | 是 | 组件ID或组件路径 |
| newWidgetName | 新的组件名称 | string | 是 | 新的组件名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 数据

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2023-05-15 19:20:22

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 主题添加数据表

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/analysis/tables

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "tableName": "c02127da02264264b1d3aec05646e661",
  "parentSubject": "91963877617542e99e58dd88ad768c0c"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| tableName | c02127da02264264b1d3aec05646e661 | string | 是 | 数据集原始名 |
| parentSubject | 91963877617542e99e58dd88ad768c0c | string | 是 | 主题ID或路径 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": {
		"tableName": "f8283aeeab264682b85cb6496c697eb2",
		"transferName": "新的数据集名称"
	}
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | object | - |
| data.tableName | f8283aeeab264682b85cb6496c697eb2 | string | 数据集原始名 |
| data.transferName | 新的数据集名称 | string | 数据集转义名 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 主题重命名数据集

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/analysis/tables/name

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
  "table": "f8283aeeab264682b85cb6496c697eb2",
  "newTableTransferName": "测试重命名X"
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| table | f8283aeeab264682b85cb6496c697eb2 | string | 是 | 数据集原始名或路径 |
| newTableTransferName | 测试重命名X | string | 是 | 新的数据集转义名 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 删除主题下数据

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-07-14 15:20:42

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/analysis/tables?table=f8283aeeab264682b85cb6496c697eb2

**请求方式**

> DELETE

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| table | f8283aeeab264682b85cb6496c697eb2 | string | 是 | 数据ID(原始名)，或路径如["文件夹12","文件夹1","分析主题","mysql_销售明细表XXX"] |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": true
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | true | boolean | 操作成功或失败 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 仪表板权限

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2023-05-15 19:20:22

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### BI 仪表板公共链接使用权限对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:37:03

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/publink/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"authority": {
			"biShareFun": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareFun | true | boolean | 是 | 分享功能 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板公共链接使用权限对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/publink/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"authority": {
			"biShareFun": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareFun | true | boolean | 是 | 分享功能 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### BI 仪表板公共链接使用权限对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/publink/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"authority": {
			"biShareFun": false
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareFun | false | boolean | 是 | 分享功能 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回数据 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 模板认证

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2023-05-15 19:20:22

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 角色权限认证

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:24

**准备工作：需要先开启模板认证全局设置-角色权限认证，并选择需要认证的模板。
查看权限关闭时，导出权限也要同时关闭；导出开启时，查看权限也要同时开启。**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### BI 仪表板模板认证权限查询对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:36:59

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/template/auth/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"biReportId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| biReportId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"view": false,
				"export": false
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 如果没有返回的，就是默认没权限 |
| data.data.view | false | boolean | 查看 |
| data.data.export | false | boolean | 导出 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:36:57

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/template/auth/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
		"position": "86df28cb-892c-4de4-87ac-3477113610cf",
		"biReportId": "4c6209858e56437387f4383f7961ddb5",
		"authority": {
			"view": true,
			"export": false
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| biReportId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |
| authority | - | object | 是 | 权限 |
| authority.view | true | boolean | 是 | 查看 |
| authority.export | false | boolean | 是 | 导出 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限查询对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/template/auth/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"biReportId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| biReportId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"view": true,
				"export": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 如果没有返回的，就是默认没权限 |
| data.data.view | true | boolean | 查看 |
| data.data.export | true | boolean | 导出 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/template/auth/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"role": "测试角色",
		"biReportId": "4c6209858e56437387f4383f7961ddb5",
		"authority": {
			"view": true,
			"export": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| biReportId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |
| authority | - | object | 是 | 权限 |
| authority.view | true | boolean | 是 | 查看 |
| authority.export | false | boolean | 是 | 导出 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限查询对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/template/auth/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"biReportId": "4c6209858e56437387f4383f7961ddb5"
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| biReportId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"view": true,
				"export": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | - | object | 如果没有返回的，就是默认没权限 |
| data.data.view | true | boolean | 查看 |
| data.data.export | true | boolean | 导出 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### BI 仪表板模板认证权限设置对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/dash/template/auth/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"user": "test",
		"biReportId": "4c6209858e56437387f4383f7961ddb5",
		"authority": {
			"view": true,
			"export": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| biReportId | 4c6209858e56437387f4383f7961ddb5 | string | 是 | 仪表板ID |
| authority | - | object | 是 | 权限 |
| authority.view | true | boolean | 是 | 查看 |
| authority.export | true | boolean | 是 | 导出 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | - | array | 批量返回结果 |
| data.status | true | boolean | 状态 成功-true 失败-false |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 仪表板分享到目录

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:24

**权限管理-全局设置中需开启仪表板-分享到目录控制**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 分享给部门

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 仪表板可分享给哪些部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-11-18 16:02:18

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/deprole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
  {
    "shareToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
    "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
    "position": "86df28cb-892c-4de4-87ac-3477113610cf",
    "authority": {
      "biShareControl": true
    }
  }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID或路径 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式为"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareControl | true | boolean | 是 | 分享控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:38:32

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/deprole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "role": "测试角色",
  "authority": {
				"biShareControl": true
			}
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareControl | true | boolean | 是 | 分享控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:38:41

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/deprole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
  {
    "shareToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
    "user": "test",
    "authority": {
      "biShareControl": true
    }
  }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| user | test | string | 是 | 用户ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareControl | true | boolean | 是 | 分享控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询仪表板可分享给部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:37:47

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/deprole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "position": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID或路径 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biShareControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biShareControl | true | boolean | 分享控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:40:44

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/deprole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"shareToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
	"role": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| role | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biShareControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biShareControl | true | boolean | 分享控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:40:52

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/deprole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"shareToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
	"user": "test"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 可以分享给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| user | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biShareControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biShareControl | true | boolean | 分享控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 分享给角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 仪表板可分享给哪些角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:44:53

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/customrole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
	"shareToRole": "角色A",
	"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
	"position": "86df28cb-892c-4de4-87ac-3477113610cf",
	"authority": {
				"biShareControl": true
			}
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRole | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareControl | true | boolean | 是 | 分享控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些角色对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/customrole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
    "shareToRole": "角色A",
    "role": "测试角色",
		"authority": {
			"biShareControl": true
		}
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRole | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareControl | true | boolean | 是 | 分享控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 仪表板可分享给哪些角色对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/customrole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
	{
		"shareToRole": "角色A",
		"user": "test",
		"authority": {
			"biShareControl": true
		}
	}
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRole | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| user | test | string | 是 | 用户ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biShareControl | true | boolean | 是 | 分享控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询仪表板可分享给角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:45:07

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/customrole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToRole": "角色A",
  "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "position": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRole | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biShareControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biShareControl | true | boolean | 分享控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给角色对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/customrole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
    "shareToRole": "角色A",
    "role": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRole | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| role | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biShareControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biShareControl | true | boolean | 分享控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询仪表板可分享给角色对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/sharedash/customrole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "shareToRole": "角色A",
  "user": "test"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| shareToRole | 角色A | string | 是 | 可以分享给的角色ID或名称 |
| user | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biShareControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biShareControl | true | boolean | 分享控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 资源协作

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:23

> 更新时间: 2024-06-07 15:37:24

**权限管理-全局设置中需开启资源协作控制**

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### 协作给部门

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 资源协作可协作给哪些部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:45:29

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/deprole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
  {
    "cooperateToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
    "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
    "position": "86df28cb-892c-4de4-87ac-3477113610cf",
    "authority": {
      "biCooperateControl": true
    }
  }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 协作给的部门ID或路径 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biCooperateControl | true | boolean | 是 | 协作控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:45:47

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/deprole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "role": "测试角色",
    "authority": {
      "biCooperateControl": true
    }
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 协作给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biCooperateControl | true | boolean | 是 | 协作控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:45:54

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/deprole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "user": "test",
    "authority": {
      "biCooperateControl": true
    }
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 协作给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| user | test | string | 是 | 用户ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biCooperateControl | true | boolean | 是 | 协作控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询资源协作可协作给部门对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:46:03

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/deprole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
  "position": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 协作给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径 |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biCooperateControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biCooperateControl | true | boolean | 协作控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给部门对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:46:11

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/deprole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "role": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 协作给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| role | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biCooperateControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biCooperateControl | true | boolean | 协作控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给部门对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-12-20 14:46:18

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/deprole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToDep": "c18e226b-ab35-428c-8d97-c8acdabfce3d",
  "user": "test"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToDep | c18e226b-ab35-428c-8d97-c8acdabfce3d | string | 是 | 协作给的部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| user | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biCooperateControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biCooperateControl | true | boolean | 协作控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### 协作给角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2023-05-15 19:20:20

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 查询资源协作可协作给角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:46:41

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/customrole/depost/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRole": "角色A",
    "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
    "position": "86df28cb-892c-4de4-87ac-3477113610cf"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRole | 角色A | string | 是 | 协作给的角色ID或名称 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biCooperateControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biCooperateControl | true | boolean | 协作控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给角色对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/customrole/role/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
		"cooperateToRole": "角色A",
		"role": "测试角色"
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRole | 角色A | string | 是 | 协作给的角色ID或名称 |
| role | 测试角色 | string | 是 | 角色ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biCooperateControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biCooperateControl | true | boolean | 协作控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 查询资源协作可协作给角色对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/customrole/user/get

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
  {
    "cooperateToRole": "角色A",
    "user": "test"
  }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRole | 角色A | string | 是 | 协作给的角色ID或名称 |
| user | test | string | 是 | 用户ID或名称 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"biCooperateControl": true
			}
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | - | object | 操作成功 |
| data.data.biCooperateControl | true | boolean | 协作控制 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 设置

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:46:21

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

###### 资源协作可协作给哪些角色对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2023-05-15 19:20:20

> 更新时间: 2024-12-20 14:46:59

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/customrole/depost

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
  {
    "cooperateToRole": "角色A",
    "department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
    "position": "86df28cb-892c-4de4-87ac-3477113610cf",
    "authority": {
      "biCooperateControl": true
    }
  }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRole | 角色A | string | 是 | 协作给的角色ID或名称 |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biCooperateControl | true | boolean | 是 | 协作控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些角色对角色

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/customrole/role

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRole": "角色A",
  "role": "测试角色",
    "authority": {
      "biCooperateControl": true
    }
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRole | 角色A | string | 是 | 协作给的角色ID或名称 |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biCooperateControl | true | boolean | 是 | 协作控制权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

###### 资源协作可协作给哪些角色对用户

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2023-05-15 19:20:22

> 更新时间: 2024-06-07 15:37:25

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/authority/cooperation/customrole/user

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[{
  "cooperateToRole": "角色A",
  "user": "test",
    "authority": {
      "biCooperateControl": true
    }
}]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| cooperateToRole | 角色A | string | 是 | 协作给的角色ID或名称 |
| user | test | string | 是 | 用户ID或名称 |
| authority | - | object | 是 | 权限 |
| authority.biCooperateControl | true | boolean | 是 | 协作控制 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": "success"
		}
	]
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | integer | - |
| data | - | array | - |
| data.status | true | boolean | - |
| data.data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 分享和协作设置

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2024-01-18 14:20:12

> 更新时间: 2024-01-18 14:20:12

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 主题协作

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2024-01-22 10:53:53

> 更新时间: 2024-01-22 10:53:53

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 主题协作对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2024-01-22 10:54:45

> 更新时间: 2024-12-20 14:47:16

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/cooperation/subject/depost

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
	"position": "86df28cb-892c-4de4-87ac-3477113610cf",
	"subject": "23b62271204c4d5fa22f6ff1eeb5cad4",
	"folder": "",
	"authority": {
		"use": true,
		"edit": true
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| department | f005d17f-384c-4a02-b0ad-62d2dd7b465a | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| position | 86df28cb-892c-4de4-87ac-3477113610cf | string | 是 | 职务ID或名称 |
| subject | 23b62271204c4d5fa22f6ff1eeb5cad4 | string | 是 | 主题ID或路径，和folder同时只能有一个参数存在。 |
| folder | - | string | 是 | 主题文件夹ID或路径，和subject同时只能有一个参数存在。 |
| authority | - | object | 是 | - |
| authority.use | true | boolean | 是 | 使用权限 |
| authority.edit | true | boolean | 是 | 编辑权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": "success"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 主题协作对角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2024-01-22 11:00:46

> 更新时间: 2024-09-18 14:40:27

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/cooperation/subject/role

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"role": "测试角色",
	"subject": "23b62271204c4d5fa22f6ff1eeb5cad4",
	"folder": "",
	"authority": {
		"use": true,
		"edit": true
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| role | 测试角色 | string | 是 | 角色ID或名称 |
| subject | 23b62271204c4d5fa22f6ff1eeb5cad4 | string | 是 | 主题ID或路径，和folder同时只能有一个参数存在。 |
| folder | - | string | 是 | 主题文件夹ID或路径，和subject同时只能有一个参数存在。 |
| authority | - | object | 是 | - |
| authority.use | true | boolean | 是 | 使用权限 |
| authority.edit | true | boolean | 是 | 编辑权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": "success"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 主题协作对用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2024-01-22 11:01:13

> 更新时间: 2024-09-18 14:40:48

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/cooperation/subject/user

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"user": "test",
	"subject": "23b62271204c4d5fa22f6ff1eeb5cad4",
	"folder": "",
	"authority": {
		"use": true,
		"edit": true
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | test | string | 是 | 用户ID或名称 |
| subject | 23b62271204c4d5fa22f6ff1eeb5cad4 | string | 是 | 主题ID或路径，和folder同时只能有一个参数存在。 |
| folder | - | string | 是 | 主题文件夹ID或路径，和subject同时只能有一个参数存在。 |
| authority | - | object | 是 | - |
| authority.use | true | boolean | 是 | 使用权限 |
| authority.edit | true | boolean | 是 | 编辑权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": "success"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 仪表板分享

> 创建人: JokerZy

> 更新人: JokerZy

> 创建时间: 2024-01-22 10:54:04

> 更新时间: 2024-01-22 10:54:04

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

##### BI 仪表板分享对部门职务

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2024-01-22 11:03:52

> 更新时间: 2024-12-20 14:47:26

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/share/dash/depost

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"depPosts": [
		{
			"department": "f005d17f-384c-4a02-b0ad-62d2dd7b465a",
			"position": "86df28cb-892c-4de4-87ac-3477113610cf"
		}
	],
	"biReport": "1084687bdec149a4af75a28ac2e465d0",
	"authority": {
		"view": true
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| depPosts | - | array | 是 | 部门职务列表 |
| depPosts.department | depId_664ea1539404 | string | 是 | 部门ID或路径，路径格式"@@@测试部门@@@部门A" |
| depPosts.postition | postId_6d7380bff5b2 | string | 是 | 职务ID或名称 |
| biReport | biReport_b9a81263133a | string | 是 | 仪表板ID或路径 |
| authority | - | object | 是 | - |
| authority.view | true | boolean | 是 | 查看权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": "success"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 仪表板分享对部门角色

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2024-01-22 11:04:55

> 更新时间: 2024-09-06 10:01:38

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/share/dash/role

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"roles": [
		"测试角色"
	],
	"biReport": "1084687bdec149a4af75a28ac2e465d0",
	"authority": {
		"view": true
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| roles | 测试角色 | array | 是 | 角色ID或名称列表 |
| biReport | 1084687bdec149a4af75a28ac2e465d0 | string | 是 | 仪表板ID或路径 |
| authority | - | object | 是 | - |
| authority.view | true | boolean | 是 | 查看权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": "success"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

##### BI 仪表板分享对部门用户

> 创建人: JokerZy

> 更新人: icey

> 创建时间: 2024-01-22 11:05:27

> 更新时间: 2024-09-06 10:01:46

```text
暂无描述
```

**接口状态**

> 已完成

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/share/dash/user

**请求方式**

> PUT

**Content-Type**

> json

**请求Body参数**

```javascript
{
	"users": [
		"test"
	],
	"biReport": "1084687bdec149a4af75a28ac2e465d0",
	"authority": {
		"view": true
	}
}
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| users | test | array | 是 | 用户ID或名称列表 |
| biReport | 1084687bdec149a4af75a28ac2e465d0 | string | 是 | 仪表板ID或路径 |
| authority | - | object | 是 | - |
| authority.view | true | boolean | 是 | 查看权限 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": "success"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| data | success | string | 操作成功 |

* 失败(404)

```javascript
暂无数据
```

**Query**

### 资源交接

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2025-12-26 10:34:07

> 更新时间: 2025-12-26 10:34:07

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

#### 查询用户我的分析交接资源

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2025-12-26 10:34:49

> 更新时间: 2026-01-12 18:11:36

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/handover/analysis/get?user=1

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | 1 | string | 是 | 用户名或用户ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": {
		"id": "__my_analysis__b5f0c2ee-640f-4039-a4d4-918b55354898", // 我的分析根文件夹id
		"name": "b5f0c2ee-640f-4039-a4d4-918b55354898", // 用户id
		"folders": [
			{
				"id": "62e7d71a480841c5a87580079bf523c0", // 文件夹ID
				"name": "测试", // 文件夹名称
				"folders": [ // 子文件夹信息
					{
						"id": "581d0142f5e5405bac80a182199aa066",
						"name": "测试1",
						"folders": [
							{
								"id": "8466660791054d97a13e64ed2a4d4ad0",
								"name": "测试2",
								"folders": [],
								"subjects": [
									{
										"id": "cc3a95cd788442d687b7d5eb88a57e56",
										"name": "分析主题3"
									},
									{
										"id": "b095880b4f9b47b9a589760c21638b0a",
										"name": "分析主题4"
									},
									{
										"id": "cbed7ce978864b83aaa7520b6bef63cf",
										"name": "分析主题2"
									},
									{
										"id": "16d949c170724f11a0e742efa74519e6",
										"name": "分析主题"
									},
									{
										"id": "c711b193d53f4271acc4d4e1ea5d7c95",
										"name": "分析主题1"
									}
								]
							}
						],
						"subjects": []
					}
				],
				"subjects": [ // 文件夹下主题信息
					{
						"id": "3054f07e11624ec68e9d914fb2df8add", // 主题ID
						"name": "分析主题2" // 主题名称
					},
					{
						"id": "74ff70edd9774b8b8bf245d229e6336a",
						"name": "分析主题4"
					},
					{
						"id": "086a17a325db499c9e04bae0bde4fe7d",
						"name": "分析主题"
					},
					{
						"id": "5d262f2a7b924174ad78acf2962595e7",
						"name": "分析主题5"
					},
					{
						"id": "94dd585ed242464faf4bd374bd27e28f",
						"name": "分析主题6"
					},
					{
						"id": "29cc8244f3ef41a48f429035360b4f63",
						"name": "分析主题7"
					},
					{
						"id": "9b499c3ca55944bb918b233487908717",
						"name": "分析主题1"
					},
					{
						"id": "52517e75974240b791bbd675990fe8d0",
						"name": "分析主题3"
					}
				]
			},
			{
				"id": "f517bc36e44544d799e4cdff3ffb3ff3",
				"name": "业务主题",
				"folders": [
					{
						"id": "dab7749033f94ac7aa9e937a2577049d",
						"name": "人事管理",
						"folders": [],
						"subjects": [
							{
								"id": "da27ccd2bf654ea8bb709099ddffdb94",
								"name": "人员离职分析"
							}
						]
					},
					{
						"id": "89156cd54894431f9c2fb24cbd96afae",
						"name": "销售管理",
						"folders": [],
						"subjects": [
							{
								"id": "4b85bcf6ba9c40209a541054288c39cf",
								"name": "销售业绩达成情况"
							},
							{
								"id": "377f0ec7cc064ac48e1930c4ec3bb70e",
								"name": "2020上半年销售分析"
							}
						]
					},
					{
						"id": "ce5aa590971a4cd7aa75b4fb39545e11",
						"name": "财务分析",
						"folders": [],
						"subjects": [
							{
								"id": "1955561cc138473698f464cec44b0220",
								"name": "利润分析"
							},
							{
								"id": "62b6e18edab8493d965eb4e8e99ed7c6",
								"name": "资产负债分析"
							}
						]
					}
				],
				"subjects": []
			},
			{
				"id": "e05dec72c3a747a89443d76456e024c4",
				"name": "功能演示",
				"folders": [
					{
						"id": "dd8f0eac45fb4d3cb9ea7ff11ab7e366",
						"name": "FineReport高级报表",
						"folders": [],
						"subjects": [
							{
								"id": "e94ce35ba69f4b68ba0ccd142a15c506",
								"name": "人员变动情况统计"
							},
							{
								"id": "6f924e9999c84f72bb3f2e58a56359d8",
								"name": "零售数据统计"
							},
							{
								"id": "f68122e1968d4acba419559752791e75",
								"name": "货运订单信息表"
							}
						]
					}
				],
				"subjects": [
					{
						"id": "e5c58a91c26143299551ba73d856242f",
						"name": "五分钟上手FineBI"
					},
					{
						"id": "808283019ce64baf984ac821896932dd",
						"name": "图表组件汇总"
					},
					{
						"id": "515e3652368e40599dfe1b752d98aa14",
						"name": "突出显示"
					},
					{
						"id": "c6e36a473ea04f8f9527ac85fe722a32",
						"name": "第一个数据分析案例"
					},
					{
						"id": "7dff49efdb584b378e8fe7ca9b50b252",
						"name": "FineBI交互操作演示"
					},
					{
						"id": "aa25af630ae745d2957052968bbfcdb7",
						"name": "图表实用场景"
					},
					{
						"id": "35b69617f959457eb34c2ac6ba2002b5",
						"name": "首页导航"
					}
				]
			},
			{
				"id": "25cf8fdfb18b48ef81803d3a68662f68",
				"name": "指标拆解树",
				"folders": [],
				"subjects": [
					{
						"id": "62811f8cfac5472582668267f39dfd0f",
						"name": "分析主题"
					}
				]
			},
			{
				"id": "1342b23c6fac4601ad48bb415660d3ba",
				"name": "数据分析方法",
				"folders": [],
				"subjects": [
					{
						"id": "e6fbb49cdad847329a161692182712b4",
						"name": "RFM客户价值分析"
					},
					{
						"id": "97ced08eadd84f4b9b5e28bf8a6b73e7",
						"name": "复购分析"
					},
					{
						"id": "49bcaa04adfb4cec803d7c0f972fc995",
						"name": "用户画像"
					},
					{
						"id": "9415426492354f378aa768ae9eab10e2",
						"name": "杜邦分析"
					},
					{
						"id": "a15fec0780b146b797d8f00e2c4eb2a9",
						"name": "购物篮分析"
					},
					{
						"id": "5e5174230a4e4436b62edd116a425523",
						"name": "用户留存分析"
					},
					{
						"id": "606a1038d11a4d7bb22eb52143aa3476",
						"name": "商品销售帕累托分析"
					}
				]
			}
		],
		"subjects": [
			{
				"id": "58bc36f9d6bb4092b1ac4a853b5e1857",
				"name": "分析主题14"
			},
			{
				"id": "5fd3b69056f640c4ab51cf93feeccb80",
				"name": "分析主题2"
			},
			{
				"id": "2e02974f334148f0b3ff38c38db4f796",
				"name": "分析主题7"
			},
			{
				"id": "e848c12888224c5a89bd9be5ab6e7a67",
				"name": "分析主题3"
			},
			{
				"id": "ed6574da31594e1eb51b5d2e4ada556e",
				"name": "分析主题9"
			},
			{
				"id": "2b8d4a34187a4342af99afa91323c257",
				"name": "分析主题10"
			},
			{
				"id": "fb69a9e7bffc4445a7c0373aa55bb658",
				"name": "分析主题12"
			},
			{
				"id": "a1071bbaf28c4ee5875388b6ada0772b",
				"name": "分析主题6"
			},
			{
				"id": "34f5db5ce7b94ac6a9af702a1f98c4f0",
				"name": "分析主题13"
			},
			{
				"id": "c50e3d4fe3db42e897e057ca83d911a7",
				"name": "分析主题8"
			},
			{
				"id": "dffb33bba2fb4063816ba71dee7634f0",
				"name": "分析主题1"
			},
			{
				"id": "161cc7351cdc4ee9a343541268e7b495",
				"name": "分析主题11"
			},
			{
				"id": "80b0cd06bd0f423083fa06028ed7fe2e",
				"name": "分析主题"
			},
			{
				"id": "15c9e862636b4f9da7c1fc2146a62d08",
				"name": "分析主题5"
			},
			{
				"id": "edae2254426a4888a915c7d2d7b45a3b",
				"name": "dddooocc"
			},
			{
				"id": "1db026040b0f4b23bdd69ffb27b20e7a",
				"name": "分析主题4"
			},
			{
				"id": "c5c97f9d30f74b2a928fad7c7e490d01",
				"name": "分析主题15"
			}
		]
	},
	"traceId": "181404eb-4517-434f-b4e8-d39da8e8c354"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | object | 返回数据 |
| data.id | __my_analysis__b5f0c2ee-640f-4039-a4d4-918b55354898 | string | 我的分析根文件夹id |
| data.name | b5f0c2ee-640f-4039-a4d4-918b55354898 | string | 用户id |
| data.folders | - | array | 子文件夹列表 |
| data.folders.id | 62e7d71a480841c5a87580079bf523c0 | string | 文件夹id |
| data.folders.name | 测试 | string | 文件夹名称 |
| data.folders.folders | - | array | - |
| data.folders.folders.id | 581d0142f5e5405bac80a182199aa066 | string | - |
| data.folders.folders.name | 测试1 | string | - |
| data.folders.folders.folders | - | array | - |
| data.folders.folders.folders.id | 8466660791054d97a13e64ed2a4d4ad0 | string | - |
| data.folders.folders.folders.name | 测试2 | string | - |
| data.folders.folders.folders.folders | - | array | - |
| data.folders.folders.folders.subjects | - | array | - |
| data.folders.folders.folders.subjects.id | cc3a95cd788442d687b7d5eb88a57e56 | string | - |
| data.folders.folders.folders.subjects.name | 分析主题3 | string | - |
| data.folders.folders.subjects | - | array | - |
| data.folders.subjects | - | array | - |
| data.folders.subjects.id | 3054f07e11624ec68e9d914fb2df8add | string | - |
| data.folders.subjects.name | 分析主题2 | string | - |
| data.folders.folders.subjects.id | da27ccd2bf654ea8bb709099ddffdb94 | string | - |
| data.folders.folders.subjects.name | 人员离职分析 | string | - |
| data.subjects | - | array | 子主题列表 |
| data.subjects.id | 58bc36f9d6bb4092b1ac4a853b5e1857 | string | 主题id |
| data.subjects.name | 分析主题14 | string | 主题名称 |
| traceId | 181404eb-4517-434f-b4e8-d39da8e8c354 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 查询用户公共数据交接资源

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2025-12-26 11:26:27

> 更新时间: 2026-01-12 18:30:55

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/handover/table/get?user=1

**请求方式**

> GET

**Content-Type**

> none

**请求Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| user | 1 | string | 是 | 用户名或用户ID |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": {
		"id": "__root_group__",
		"name": "__root_group__",
		"folders": [
			{
				"id": "5c1d7416bdfb46d780725af2f6c3f351",
				"name": "测试",
				"folders": [
					{
						"id": "9a5f303c479f4f7db157978c8f230989",
						"name": "文件夹",
						"folders": [],
						"tables": [
							{
								"id": "a999b226528d451d93e51a686752fd33",
								"name": "BI Demo_CUSTOMER"
							}
						]
					}
				],
				"tables": []
			},
			{
				"id": "2802469f40b14094aa7372ea2488a830",
				"name": "行业数据",
				"folders": [
					{
						"id": "56c50bf1e90e4566a0d6ea2a95217c88",
						"name": "零售电商",
						"folders": [
							{
								"id": "3b9513c2421a402ba6c78a2fda5040b5",
								"name": "零售电商 demo",
								"folders": [],
								"tables": [
									{
										"id": "P@@@分析表2",
										"name": "门店销售数据统计"
									}
								]
							}
						],
						"tables": []
					},
					{
						"id": "7c8a78b6b6614fe4b0d211aa164a18cf",
						"name": "互联网",
						"folders": [],
						"tables": [
							{
								"id": "P@@@分析表1",
								"name": "互联网渠道统计数据"
							},
							{
								"id": "P@@@分析表7",
								"name": "互联网地区访问统计"
							}
						]
					},
					{
						"id": "401991d289254824aec8d3586285c52d",
						"name": "交通物流",
						"folders": [],
						"tables": [
							{
								"id": "P@@@物流盈利分析数据",
								"name": "物流盈利分析数据"
							},
							{
								"id": "P@@@航空运输分析数据",
								"name": "航空运输分析数据"
							}
						]
					},
					{
						"id": "b85f847a31e24e1cbe12c782f6f2755f",
						"name": "金融银行",
						"folders": [],
						"tables": [
							{
								"id": "P@@@贷款风险分析表",
								"name": "贷款风险分析表"
							}
						]
					},
					{
						"id": "43b798f75fe64904b277e54a503d931d",
						"name": "公共服务",
						"folders": [
							{
								"id": "d3c4d40760984547bb2e48a475393f94",
								"name": "其他公共服务",
								"folders": [],
								"tables": [
									{
										"id": "P@@@财政收支分析表",
										"name": "财政收支分析表"
									},
									{
										"id": "P@@@教育数据统计分析",
										"name": "教育数据统计分析"
									}
								]
							}
						],
						"tables": []
					},
					{
						"id": "f6caa5434f7345b788352a1fe6f51ebb",
						"name": "地产建筑",
						"folders": [],
						"tables": [
							{
								"id": "P@@@分析表5",
								"name": "项目产品销售数据"
							},
							{
								"id": "P@@@分析表3",
								"name": "省市签约数据统计"
							},
							{
								"id": "P@@@合同分析表",
								"name": "合同分析表"
							},
							{
								"id": "P@@@库存数据分析",
								"name": "库存数据分析"
							}
						]
					},
					{
						"id": "ad5531f7abc644d9bb5fc1a6dd1f449b",
						"name": "机械制造",
						"folders": [
							{
								"id": "3f902022-6aff-49de-9b38-7ce6bfe4ece8",
								"name": "返货品分析数据",
								"folders": [],
								"tables": [
									{
										"id": "P@@@自助数据集29",
										"name": "Excel-返货品画像-正单数据集-正返单合并-结果表"
									},
									{
										"id": "P@@@自助数据集28",
										"name": "Excel-返货品画像-返修订单-结果表"
									}
								]
							}
						],
						"tables": []
					}
				],
				"tables": []
			},
			{
				"id": "17bb42b152e3425fa0e2dd827191131a",
				"name": "部门数据",
				"folders": [
					{
						"id": "33e313c71fe94b3fbbeea52f9ce8b70e",
						"name": "销售_Lisa",
						"folders": [],
						"tables": [
							{
								"id": "P@@@分析表",
								"name": "KPI指标项"
							},
							{
								"id": "P@@@品类经营分析",
								"name": "品类经营分析"
							},
							{
								"id": "P@@@地区数据分析",
								"name": "地区数据分析"
							}
						]
					}
				],
				"tables": []
			}
		],
		"tables": []
	},
	"traceId": "da44a61d-3c75-4cfc-9585-2a6ec3f587f6"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | object | 返回数据 |
| data.id | __root_group__ | string | - |
| data.name | __root_group__ | string | - |
| data.folders | - | array | 文件夹 |
| data.folders.id | 5c1d7416bdfb46d780725af2f6c3f351 | string | 文件夹id |
| data.folders.name | 测试 | string | 文件夹名称 |
| data.folders.folders | - | array | - |
| data.folders.folders.id | 9a5f303c479f4f7db157978c8f230989 | string | - |
| data.folders.folders.name | 文件夹 | string | - |
| data.folders.folders.folders | - | array | - |
| data.folders.folders.tables | - | array | - |
| data.folders.folders.tables.id | a999b226528d451d93e51a686752fd33 | string | - |
| data.folders.folders.tables.name | BI Demo_CUSTOMER | string | - |
| data.folders.tables | - | array | 表信息 |
| data.folders.folders.folders.id | 3b9513c2421a402ba6c78a2fda5040b5 | string | - |
| data.folders.folders.folders.name | 零售电商 demo | string | - |
| data.folders.folders.folders.folders | - | array | - |
| data.folders.folders.folders.tables | - | array | - |
| data.folders.folders.folders.tables.id | P@@@分析表2 | string | - |
| data.folders.folders.folders.tables.name | 门店销售数据统计 | string | - |
| data.tables | - | array | - |
| traceId | da44a61d-3c75-4cfc-9585-2a6ec3f587f6 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 查询已删除用户

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2025-12-26 11:27:56

> 更新时间: 2026-01-12 18:13:34

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/handover/unknown/user/get

**请求方式**

> GET

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"userId": "84098cf8-1f11-4230-b43f-1a0b421fdc22",
			"userName": "未知用户"
		}
	],
	"traceId": "ab525495-23f4-45ca-9ba0-7393f6dc5782"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | object | 返回数据 |
| data.userId | 84098cf8-1f11-4230-b43f-1a0b421fdc22 | string | 用户id |
| data.userName | 未知用户 | string | - |
| traceId | ab525495-23f4-45ca-9ba0-7393f6dc5782 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**

#### 触发资源交接

> 创建人: Ivan.Guo

> 更新人: Ivan.Guo

> 创建时间: 2025-12-26 11:29:16

> 更新时间: 2026-01-12 18:15:53

```text
暂无描述
```

**接口状态**

> 已发布

**接口URL**

> http://{host}:{port}/webroot/decision/sp/client/api/v3/bi/conf/handover/start

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
[
    {
        "sender": "1", // 交出方用户id
        "accepter": "Ben", // 接收方用户id
        "resourceInPublicData": { // 公共数据资源
            "packIds": [ // 文件夹ID列表
                "de20c13fdcdd436987289588b232c38c"
            ],
            "tableNames": [ // 表名列表
                "销售明细表1105"
            ]
        },
        "resourceInUserAnalysis": { // 我的分析资源
            "packIds": [ // 文件夹ID列表
                "dd8f0eac45fb4d3cb9ea7ff11ab7e366"
            ],
            "subjectIds": [ // 主题ID列表
                "49bcaa04adfb4cec803d7c0f972fc995"
            ]
        }
    }
]
```

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 0 | - | object | 是 | - |
| 0.sender | 2 | string | 是 | 交出方用户id |
| 0.accepter | 3 | string | 是 | 接收方用户id |
| 0.resourceInPublicData | - | object | 是 | 交出资源-公共数据 |
| 0.resourceInPublicData.packIds | - | array | 是 | 交出资源-公共数据-文件夹 |
| 0.resourceInPublicData.tableNames | - | array | 是 | 交出资源-公共数据-表 |
| 0.resourceInUserAnalysis | - | object | 是 | 交出资源-我的分析 |
| 0.resourceInUserAnalysis.packIds | - | array | 是 | 交出资源-我的分析-文件夹 |
| 0.resourceInUserAnalysis.subjectIds | - | array | 是 | 交出资源-我的分析-主题 |

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"status": 200,
	"data": [
		{
			"status": true,
			"data": {
				"userRoleEqual": false,
				"success": true,
				"failResource": {
					"resourceInPublicData": {
						"tableNames": [],
						"packIds": []
					},
					"resourceInUserAnalysis": {
						"subjectIds": [],
						"packIds": []
					}
				}
			}
		}
	],
	"traceId": "834891eb-5520-42ed-88fd-13dbec8a6d53"
}
```

| 参数名 | 示例值 | 参数类型 | 参数描述 |
| --- | --- | ---- | ---- |
| status | 200 | number | 状态 |
| data | - | object | 返回数据 |
| data.status | true | boolean | - |
| data.data | - | object | 返回数据 |
| data.data.userRoleEqual | false | boolean | - |
| data.data.success | true | boolean | 成功响应 |
| data.data.failResource | - | object | 失败的资源 |
| data.data.failResource.resourceInPublicData | - | object | 公共数据信息 |
| data.data.failResource.resourceInPublicData.tableNames | - | array | 公共数据表名 |
| data.data.failResource.resourceInPublicData.packIds | - | array | 公共数据包Id |
| data.data.failResource.resourceInUserAnalysis | - | object | 我的分析信息 |
| data.data.failResource.resourceInUserAnalysis.subjectIds | - | array | 主题ID |
| data.data.failResource.resourceInUserAnalysis.packIds | - | array | 文件夹 |
| traceId | 834891eb-5520-42ed-88fd-13dbec8a6d53 | string | - |

* 失败(404)

```javascript
暂无数据
```

**Query**
