# FineBI 接口文档

| 文件 | 说明 |
|---|---|
| `开放平台 FineBI接口（对外）.md` | BI 权限/资源/交接接口（数据目录、数据集、行列权限、仪表板、协作、资源交接） |
| `开放平台 平台接口（对外）.md` | 平台公共模块接口（用户、部门、岗位、角色、目录、权限、定时调度、数据连接、消息、日志） |
| `接口索引.md` | 自动生成的接口总表（模块、接口名、方法、URL），检索用 |

## 使用建议

- 联调时先看 `接口索引.md` 定位接口，再回原文档看参数表与返回示例。
- 接口统一前缀：`/webroot/decision/sp/client/api`。
- v3 接口的响应一般形如 `{"status":200,"data":[{"status":true,"data":...}],"traceId":"..."}`；HTTP 200 不等于业务成功，需要检查 `data[].status`。
- 认证：Header `clientId` + `secret`；可选 `decUser` 指定操作人，建议固定为“权限机器人”。

## 重新生成索引

```powershell
python tools\parse_finebi_api.py `
  "docs\finebi\开放平台 FineBI接口（对外）.md" `
  "docs\finebi\开放平台 平台接口（对外）.md" `
  --out-json tools\endpoint_index.json `
  --out-md "docs\finebi\接口索引.md"
```
