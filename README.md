# FineBI × 飞书 数据权限申请与审批

一个部署在客户内网的 Web 审批系统：员工在浏览器/飞书中提交 FineBI 数据权限申请，审批通过后由服务端调用 FineBI 开放平台自动授权、记录台账、到期回收和离职交接。

> 本仓库为公开版本，已移除客户环境配置、账号密码、Token、客户资源名称等敏感信息。示例配置仅用于演示，请勿把真实 `.env` 提交到仓库。

## 功能

- 仪表板权限：查看 / 导出 / 编辑，连带依赖数据集的组件数据权限
- 公共数据权限：文件夹 / 数据集，使用 / 管理 / 组件数据
- 行权限、列权限：审批人可在详情页补充；支持按血缘把自助数据集映射到公共数据集祖先
- 角色 / 部门成员申请：详情页展示实体已有权限摘要
- 定时调度、数据预警等管理权限
- 数据 Owner → 业务 Owner 审批链；飞书通知；到期回收；离职交接
- 已有权限预检：资源下拉树标注“已有”，避免重复申请
- 后台管理：Owner/审批人配置、目录刷新、飞书用户映射、FineBI 数据接口凭证（加密持久化）

## 目录

```
src/                服务端代码（FastAPI + SQLite + FineBI/飞书客户端）
tests/              单元/集成测试
deploy/             部署脚本与 systemd/NGINX 配置
docs/finebi/        FineBI 开放平台接口文档（已脱敏）
docs/requirements/  项目需求书
docs/database/      FineDB 行权限表结构说明
config/config.example.json
.env.example
```

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
cp config/config.example.json config/config.json
# 编辑 .env：FineBI/飞书凭证、数据库、Web 登录方式
python -m executor.cli web
```

默认本地开发使用 `WEB_AUTH_MODE=dev`；生产环境按部署文档切换飞书登录，并设置 `EXECUTOR_DRY_RUN=false`。

## 文档

- [FineBI BI 接口文档](docs/finebi/开放平台%20FineBI接口（对外）.md)
- [FineBI 平台接口文档](docs/finebi/开放平台%20平台接口（对外）.md)
- [项目需求书](docs/requirements/项目需求书.md)
- [FineDB 行权限表结构说明](docs/database/FineDB行权限表结构说明.md)
- [部署说明](deploy/README.md)

## 安全说明

- 不要提交 `.env`、`config/config.json`、数据库文件、客户资源快照、部署包中的 `DEPLOY_CONFIG_README.txt`。
- 生产环境必须使用飞书登录；不要用 `WEB_AUTH_MODE=dev` 暴露到公网。
- 后台配置的 FineBI 数据接口凭证会加密保存到 SQLite，`data/.settings.key` 与数据库一起备份。
- 本仓库中的接口文档示例已把 clientId/secret/token、私有 IP、客户数据集名称替换为占位符。

## 说明

FineBI 开放平台接口文档版权归帆软所有，本仓库仅用于项目集成参考；实际使用请以客户 FineBI 版本的官方文档为准。
