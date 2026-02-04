# zhjx 模块清单

本文件将 Tutor 的插件/模块概念映射到联奕智慧教学场景。模块是否启用由 `RUN_ZHJX_*` 开关控制，模板中通过条件判断决定是否渲染对应服务。模块依赖需要人工保证启用，系统不会自动解析依赖或排序。

## 依赖关系总览（人工约束）

- **base**：基础设施必选模块，无前置依赖。
- **common**：依赖 base，提供网关、认证与共享服务。
- **zhjx_zlmediakit**：依赖 base，提供直播流接入。
- **zhjx_ilive_ecom / zhjx_sup / zhjx_ykt**：依赖 common。
- **zhjx_media**：依赖 common + zhjx_zlmediakit。

> 补充：`1panel` 为单机 Docker 运维面板；`portainer` 用于多节点 / Swarm 集群。当前模板按 1panel（单机）编排，后续可为 portainer 模式新增模板。
> 注意：依赖不会自动解析。启用某模块前，请先确保其依赖模块对应的 `RUN_ZHJX_*` 已开启。

## base（默认开启）
- **模板来源**：`tutor/templates/local/zhjx-base.yml`（内容源自 `zhjx-hub/1panel版本/zhjx-base.yaml`）
- **职责**：提供 nacos、mysql、redis、rabbitmq、minio、sentinel、emqx、kafka、elasticsearch、nginx、kkfileview 等基础组件。
- **依赖**：需在宿主机准备证书与 nginx 配置，默认指向 `/home/zhjx/*.crt/*.key`。
- **关键变量**
  - `MASTER_NODE_IP`：决定 nacos/mysql/minio 等服务对外地址。
  - `NACOS_DB_PASSWORD` / `MYSQL_ROOT_PASSWORD`
  - `PORTAL_CERT_PATH`：nginx 证书映射路径。
  - 镜像仓库 `IMAGE_REGISTRY`（默认为 `zhjx-images.tencentcloudcr.com`）。
- **edops 操作约束**：任何 `edops build/deploy` 均需先检查 base 是否健康；`edops rollback` 需提供镜像/数据备份策略。

## common（默认开启）
- **模板来源**：`tutor/templates/local/zhjx-common.yml`（内容源自 `zhjx-hub/1panel版本/zhjx-common.yaml`）
- **职责**：部署共享域服务（认证、用户、后台、网关、对象存储 API、基础数据等）以及 `ly-ac-console-ui` 前端。
- **依赖**：需依赖 base 中的 nacos/mysql；默认通过 `zhjx-network` 互通。
- **关键变量**
  - `IMAGE_REGISTRY`
  - `VERSION_UI_AUTH`、`VERSION_UI_CONSOLE`、`VERSION_SVC_DEFAULT`
  - `SCHOOL_ID`
  - `MASTER_NODE_IP`（用于拼接 `API_TENANT_URL`、`API_OBJECT_STORAGE_URL`）
- **edops 行为**：默认随 base 自动启用；后续将暴露 `edops config set common.version.svc` 等命令方便批量升级。

## zhjx_zlmediakit（默认关闭）
- **模板来源**：`tutor/templates/local/zhjx-zlmediakit.yml`（内容源自 `zhjx-hub/1panel版本/zhjx-zlmediakit.yaml`）
- **职责**：部署 ZLMediaKit，用于 RTMP/RTSP/HTTP-FLV/HLS 等直播流接入。
- **依赖**：需要 `base` 网络，使用宿主机目录 `/home/zhjx/media` 保存配置、日志与静态资源。
- **关键变量**
  - `MEDIA_CONF_PATH`、`MEDIA_LOG_PATH`、`MEDIA_WEB_PATH`
  - 对外端口（默认 1935/8080/8443/554/10000/UDP 等）
- **edops 行为**：默认关闭。要启用此模块，请在 `config.yml` 中设置对应开关：
  ```yaml
  RUN_ZHJX_ZLMEDIAKIT: true
  ```

## zhjx_sup（默认关闭）
- **模板来源**：`tutor/templates/local/zhjx-sup.yml`
- **职责**：部署 AI 督导系统相关服务。
- **依赖**：依赖 `common` 模块。

## zhjx_ilive_ecom（默认关闭）
- **模板来源**：`tutor/templates/local/zhjx-ilive-ecom.yml`
- **职责**：部署直播实训电商相关服务。
- **依赖**：依赖 `common` 模块。

## zhjx_media（默认关闭）
- **模板来源**：`tutor/templates/local/zhjx-media.yml`
- **职责**：部署流媒体处理相关业务服务。
- **依赖**：依赖 `common` 和 `zhjx_zlmediakit` 模块。

## zhjx_ykt（默认关闭）
- **模板来源**：`tutor/templates/local/zhjx-ykt.yml`
- **职责**：部署奕课堂相关业务服务。
- **依赖**：依赖 `common` 模块。

> 说明：edops 不会自动处理模块依赖或部署顺序。启用 `zhjx_media` 前需同时开启 `RUN_ZHJX_COMMON` 与 `RUN_ZHJX_ZLMEDIAKIT`；启用 `zhjx_ilive_ecom`/`zhjx_sup`/`zhjx_ykt` 前需开启 `RUN_ZHJX_COMMON`。
