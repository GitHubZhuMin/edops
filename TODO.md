# EdOps（zhjx）TODO（本期执行清单）

日期：2026-02-04
范围：执行 P0 开发并持续更新状态

## 总体目标
- 本期仅聚焦 `local` 与 `portainer` 两种部署模式可交付。
- `k8s` 本期从 CLI 入口屏蔽（不删除代码文件）。
- `portainer` 仅实现“可用渲染”，不做部署/状态/日志能力。
- 模块依赖改为弱依赖：只提示，不阻断。

## P0（必须）

### P0-01 屏蔽 K8s CLI 入口（已完成）
- 任务：
  - 从 CLI 命令注册中移除 `k8s`。
  - 保留 `tutor/commands/k8s.py` 与 `tutor/templates/k8s/`，不删除文件。
- 涉及文件：
  - `tutor/commands/cli.py`
  - `tests/commands/test_cli.py`
  - `tests/commands/test_k8s.py`
- 验收标准：
  - `edops --help` 不再出现 `k8s`。
  - `edops k8s --help` 返回“未知命令”并退出非 0。
- 状态：✅ 已完成（2026-02-04）

### P0-02 Portainer 渲染命令可用化（仅渲染，已完成）
- 任务：
  - `edops portainer render [module]` 改为实际产出 stack 文件。
  - 使用 `docker compose ... config` 合并已渲染的 `local` 模板。
  - 命令输出生成文件路径与 `docker stack deploy` 示例。
- 涉及文件：
  - `tutor/commands/portainer.py`
  - `tests/commands/test_portainer.py`（新增）
  - `docs/edops-cli.md`
- 渲染规则：
  - `edops portainer render`
    - 输出：`<root>/portainer/docker-stack.yml`
    - 包含：`local/docker-compose.yml`、`local/docker-compose.prod.yml`、`zhjx-base/common`、已启用业务模块、override（若存在）
  - `edops portainer render base`
    - 输出：`<root>/portainer/docker-stack.base.yml`
    - 包含：`base` 依赖闭包
  - `edops portainer render common`
    - 输出：`<root>/portainer/docker-stack.common.yml`
    - 包含：`base + common`
  - `edops portainer render zhjx_media`
    - 输出：`<root>/portainer/docker-stack.zhjx_media.yml`
    - 包含：`base + common + zhjx_zlmediakit + zhjx_media`
  - 其他模块：
    - 输出：`<root>/portainer/docker-stack.<module>.yml`
    - 依赖规则按 `docs/zhjx-modules.md` 计算闭包
- 验收标准：
  - 成功生成 stack 文件。
  - 命令输出包含部署示例，且不包含“尚未实现”提示。
- 状态：✅ 已完成（2026-02-04）

### P0-03 模块依赖弱校验（已完成）
- 任务：
  - 将 `_validate_module_deps` 改为“收集警告并输出”，不抛异常。
  - 在 `config validate` 与 `local launch` 前置检查阶段均输出依赖警告。
  - `config save` 不做模块依赖提示（避免保存环节阻塞）。
- 涉及文件：
  - `tutor/commands/config.py`
  - `tutor/commands/compose.py`
  - `tests/commands/test_config.py`
- 验收标准：
  - `RUN_ZHJX_MEDIA=true` 且依赖缺失时，`edops config validate` 退出码为 0，输出警告。
  - `edops local launch` 前检查同样出现警告，但不因该警告中断。
- 状态：✅ 已完成（2026-02-04）

### P0-04 私有 Registry / 离线提示增强（已完成）
- 任务：
  - 在 `config validate` 输出中增加私有仓库认证提示：
    - 用户名密码：`EDOPS_IMAGE_REGISTRY_USER` + `EDOPS_IMAGE_REGISTRY_PASSWORD`
    - Token：`EDOPS_IMAGE_REGISTRY_TOKEN`
  - 仅提示，不新增配置机制。
- 涉及文件：
  - `tutor/commands/config.py`
  - `docs/edops-cli.md`
  - `QUICKSTART_CN.md`
- 验收标准：
  - 使用私有 registry 且认证缺失时，给出可直接执行的下一步命令。
- 状态：✅ 已完成（2026-02-04）

### P0-05 文档口径统一（已完成）
- 任务：
  - 主文档仅声明 `local + portainer` 本期可用。
  - `k8s` 标记为“本期屏蔽”，移除可执行命令示例。
  - 与现有 CLI 行为保持一致。
- 涉及文件：
  - `README.rst`
  - `docs/edops-cli.md`
  - `docs/DESIGN_DECISIONS_CN.md`
  - `PRD.md`
  - `TODO.md`
  - `agents.md`
- 验收标准：
  - 文档示例命令可执行且与当前版本行为一致。
- 状态：✅ 已完成（2026-02-04）

## P1（重要，暂缓到下一迭代）

### P1-01 回滚可用性修复
- 目标：`local rollback` 真正更新版本配置键，不再只写历史。
- 涉及文件：
  - `tutor/commands/local.py`
  - `tests/commands/test_local.py`
  - `docs/edops-cli.md`

### P1-02 历史记录可用性增强
- 目标：在升级/发布关键路径写入 deploy history，统一记录格式。
- 涉及文件：
  - `tutor/commands/local.py`
  - `tutor/edops/image_registry.py`
  - `tests/edops/test_image_registry.py`

### P1-03 离线部署指引完善
- 目标：补充“镜像预拉取/导入、认证、校验”完整操作说明。
- 涉及文件：
  - `docs/edops-cli.md`
  - `QUICKSTART_CN.md`

## P2（可选）
- P2-01：K8s 重新启用方案（恢复条件、里程碑、测试门槛）
- P2-02：Jenkins 触发封装（仅便捷触发，不改变职责边界）

## 测试与验收清单（执行开发时使用）
- 自动化：
  - `python -m pytest tests/commands/test_cli.py tests/commands/test_k8s.py tests/commands/test_portainer.py tests/commands/test_config.py tests/commands/test_local.py`
- 手工：
  - `edops --help`
  - `edops k8s --help`
  - `edops portainer render`
  - `edops config validate`（依赖缺失场景）
  - `edops local launch --no-health-check`（依赖缺失提示场景）
- 文档：
  - 命令示例全部可在当前版本执行，且输出与文档一致

## 备注
- 本次已执行并完成 P0 功能与文档改造，同时回填状态。
