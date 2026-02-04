from __future__ import annotations

import json
import time
import typing as t

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt
from tutor import hooks, utils
from tutor.commands import compose
from tutor.types import Config, get_typed


class LocalTaskRunner(compose.ComposeTaskRunner):
    def __init__(self, root: str, config: Config):
        """
        Load docker-compose files from local/.
        """
        super().__init__(root, config)
        self.project_name = get_typed(self.config, "LOCAL_PROJECT_NAME", str)
        self.docker_compose_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.prod.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.override.yml"),
            tutor_env.pathjoin(
                self.root, "local", "docker-compose.prod.override.yml"
            ),
            tutor_env.pathjoin(self.root, "local", "zhjx-base.yml"),
            tutor_env.pathjoin(self.root, "local", "zhjx-common.yml"),
            tutor_env.pathjoin(self.root, "local", "zhjx-zlmediakit.yml"),
            tutor_env.pathjoin(self.root, "local", "zhjx-ilive-ecom.yml"),
            tutor_env.pathjoin(self.root, "local", "zhjx-sup.yml"),
            tutor_env.pathjoin(self.root, "local", "zhjx-media.yml"),
            tutor_env.pathjoin(self.root, "local", "zhjx-ykt.yml"),
        ]
        self.docker_compose_job_files += [
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
            tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
        ]


class LocalContext(compose.BaseComposeContext):
    NAME = "local"
    OPENEDX_SERVICES = ["lms", "cms", "lms-worker", "cms-worker"]

    def job_runner(self, config: Config) -> LocalTaskRunner:
        return LocalTaskRunner(self.root, config)


@click.group(help="使用 docker-compose 在本地运行 EdOps 平台")
@click.pass_context
def local(context: click.Context) -> None:
    context.obj = LocalContext(context.obj.root)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_dev_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the local platform as soon as a platform with a different project name is
    started.
    """
    runner = LocalTaskRunner(root, config)
    if project_name != runner.project_name and runner.is_running():
        runner.docker_compose("stop")


@click.command(name="status", help="显示 EdOps 模块的详细状态")
@click.option(
    "--module",
    "module_filter",
    help="按模块名称过滤",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="输出格式",
)
@click.pass_obj
def edops_status(
    context: compose.LocalContext,
    module_filter: t.Optional[str],
    output_format: str,
) -> None:
    """显示详细状态，包括模块分组和健康信息。"""
    config = tutor_config.load(context.root)
    runner = LocalTaskRunner(context.root, config)

    # 获取容器状态
    try:
        ps_output = runner.docker_compose_output("ps", "--format", "json")
        containers = json.loads(ps_output.decode("utf-8"))
    except Exception:
        containers = []

    if not containers:
        fmt.echo_info("没有运行中的容器")
        return

    if output_format == "json":
        click.echo(json.dumps(containers, indent=2))
    else:
        # 表格格式
        fmt.echo_info("EdOps 模块状态:\n")
        for container in containers:
            name = container.get("Service", container.get("Name", ""))
            state = container.get("State", "unknown")
            status = container.get("Status", "")
            if module_filter and module_filter not in name:
                continue

            status_icon = "✓" if state == "running" else "✗"
            fmt.echo(f"{status_icon} {name:40} {state:10} {status}")


@click.command(name="healthcheck", help="对 EdOps 模块运行健康检查")
@click.argument("module_name", required=False)
@click.pass_obj
def healthcheck(
    context: compose.LocalContext, module_name: t.Optional[str]
) -> None:
    """对指定模块或所有模块运行健康检查。"""
    config = tutor_config.load(context.root)
    runner = LocalTaskRunner(context.root, config)

    module_files = {
        "base": "zhjx-base.yml",
        "common": "zhjx-common.yml",
        "zhjx_zlmediakit": "zhjx-zlmediakit.yml",
        "zhjx_ilive_ecom": "zhjx-ilive-ecom.yml",
        "zhjx_sup": "zhjx-sup.yml",
        "zhjx_media": "zhjx-media.yml",
        "zhjx_ykt": "zhjx-ykt.yml",
    }
    module_flags = {
        "base": "RUN_ZHJX_BASE",
        "common": "RUN_ZHJX_COMMON",
        "zhjx_zlmediakit": "RUN_ZHJX_ZLMEDIAKIT",
        "zhjx_ilive_ecom": "RUN_ZHJX_ILIVE_ECOM",
        "zhjx_sup": "RUN_ZHJX_SUP",
        "zhjx_media": "RUN_ZHJX_MEDIA",
        "zhjx_ykt": "RUN_ZHJX_YKT",
    }

    if module_name:
        if module_name not in module_files:
            raise exceptions.TutorError(f"未知模块: {module_name}")
        flag = module_flags.get(module_name)
        if flag and not config.get(flag, flag in {"RUN_ZHJX_BASE", "RUN_ZHJX_COMMON"}):
            raise exceptions.TutorError(f"模块未启用: {module_name}")
        modules = [module_name]
    else:
        modules = []
        for name, flag in module_flags.items():
            enabled = config.get(flag, flag in {"RUN_ZHJX_BASE", "RUN_ZHJX_COMMON"})
            if enabled:
                modules.append(name)

    target_services: set[str] = set()
    for name in modules:
        compose_file = tutor_env.pathjoin(
            context.root, "local", module_files[name]
        )
        try:
            output = utils.check_output(
                "docker",
                "compose",
                "-f",
                compose_file,
                "--project-name",
                runner.project_name,
                "config",
                "--services",
            )
        except Exception as exc:
            raise exceptions.TutorError(
                f"无法解析模块 {name} 的服务列表: {exc}"
            ) from exc
        services = [
            line.strip()
            for line in output.decode("utf-8").splitlines()
            if line.strip()
        ]
        for service in services:
            if service == "zhjx-permissions":
                continue
            target_services.add(service)

    if not target_services:
        fmt.echo_info("没有可检查的服务，跳过健康检查。")
        return

    fmt.echo_info("正在检查服务运行状态...")
    max_retries = 10
    interval_seconds = 3

    for attempt in range(max_retries):
        try:
            ps_output = runner.docker_compose_output("ps", "--format", "json")
            containers = json.loads(ps_output.decode("utf-8"))
        except Exception:
            containers = []

        states = {}
        for container in containers:
            name = container.get("Service", container.get("Name", ""))
            state = container.get("State", "unknown")
            states[name] = state

        failed = {
            service: states.get(service, "missing")
            for service in sorted(target_services)
            if states.get(service) != "running"
        }

        if not failed:
            fmt.echo_info("✓ 所有服务运行正常")
            return

        if attempt < max_retries - 1:
            time.sleep(interval_seconds)
            continue

        fmt.echo_error("以下服务未正常运行：")
        for service, state in failed.items():
            fmt.echo_error(f"  - {service}: {state}")
        raise exceptions.TutorError("健康检查失败")


@click.command(name="history", help="查看部署历史")
@click.option(
    "--module",
    "module_filter",
    help="按模块名称过滤",
)
@click.option(
    "--service",
    "service_filter",
    help="按服务名称过滤",
)
@click.option(
    "--limit",
    type=int,
    default=20,
    help="显示的记录数",
)
@click.pass_obj
def deployment_history(
    context: compose.LocalContext,
    module_filter: t.Optional[str],
    service_filter: t.Optional[str],
    limit: int,
) -> None:
    """查看部署历史记录。"""
    from pathlib import Path
    from tutor.edops import image_registry

    history_file = Path(context.root) / "deploy-history.yml"
    history = image_registry.DeployHistory(history_file)

    if not history.records:
        fmt.echo_info("未找到部署历史")
        return

    # 过滤记录
    records = history.records
    if module_filter:
        records = [r for r in records if r.module == module_filter]
    if service_filter:
        records = [r for r in records if r.service == service_filter]

    # 限制记录数
    records = records[-limit:]

    if not records:
        fmt.echo_info("未找到匹配的部署记录")
        return

    fmt.echo_info("部署历史:\n")
    for record in reversed(records):
        timestamp = record.timestamp.split("T")[0]  # 只显示日期
        operation_icon = "→" if record.operation == "deploy" else "←"
        fmt.echo(
            f"{operation_icon} {timestamp} {record.module:15} "
            f"{record.service:30} {record.tag:10} ({record.operation})"
        )


@click.command(name="rollback", help="将模块回滚到之前的版本")
@click.argument("module_name")
@click.option(
    "--version",
    "target_version",
    help="目标版本标签（默认：上一次部署）",
)
@click.pass_obj
def rollback(
    context: compose.LocalContext,
    module_name: str,
    target_version: t.Optional[str],
) -> None:
    """将模块回滚到之前的版本。"""
    from pathlib import Path

    from tutor import config as tutor_config
    from tutor.edops import image_registry

    config = tutor_config.load(context.root)
    history_file = Path(context.root) / "deploy-history.yml"
    history = image_registry.DeployHistory(history_file)

    # 获取模块历史
    module_history = history.get_module_history(module_name)
    if not module_history:
        fmt.echo_error(f"未找到模块 '{module_name}' 的部署历史")
        return

    # 查找目标版本
    if target_version:
        # 在历史中查找指定版本
        target_record = None
        for record in reversed(module_history):
            if record.tag == target_version:
                target_record = record
                break
        if not target_record:
            fmt.echo_error(
                f"在 '{module_name}' 的历史中未找到版本 '{target_version}'"
            )
            return
    else:
        # 获取上一个版本（倒数第二个）
        if len(module_history) < 2:
            fmt.echo_error(
                f"'{module_name}' 没有可用于回滚的上一个版本"
            )
            return
        target_record = module_history[-2]

    # 确认回滚
    current_version = module_history[-1].tag
    fmt.echo_info(
        f"将 {module_name} 从 {current_version} 回滚到 {target_record.tag}"
    )

    config_updated = False

    # 记录回滚操作
    history.add_record(
        module=module_name,
        service=target_record.service,
        image=target_record.image,
        tag=target_record.tag,
        operation="rollback",
    )

    if config_updated:
        fmt.echo_info("✓ 回滚已完成。请重启服务以使更改生效。")
    else:
        fmt.echo_info("✓ 回滚已在历史中记录。")
        fmt.echo_info(
            fmt.alert("⚠️  未能自动更新配置，请手动更新版本并重启。")
        )

    fmt.echo_info(f"  服务: {target_record.service}")
    fmt.echo_info(f"  镜像: {target_record.image}:{target_record.tag}")


@click.command(name="bootstrap", help="一键快速部署准备工具")
@click.option("--preset", help="使用预设配置 (minimal/standard/full)")
@click.pass_obj
def bootstrap(context: compose.LocalContext, preset: t.Optional[str]) -> None:
    """自动执行部署前的准备工作，包括环境检查和基础配置。"""
    fmt.echo(fmt.title("EdOps 部署准备工具"))

    # 1. 自动检测 IP
    detected_ip = utils.get_host_ip()
    fmt.echo_info(f"检测到本机 IP: {detected_ip}")

    # 2. 基础配置
    config = tutor_config.load_minimal(context.root)

    # 设置检测到的 IP
    if not config.get("EDOPS_MASTER_NODE_IP") or config.get("EDOPS_MASTER_NODE_IP") == "127.0.0.1":
        config["EDOPS_MASTER_NODE_IP"] = detected_ip
        fmt.echo(f"  ✓ 已自动设置 EDOPS_MASTER_NODE_IP={detected_ip}")

    # 处理预设
    if preset:
        from tutor.edops import presets
        fmt.echo_info(f"正在应用预设: {preset}...")
        try:
            presets.apply_preset(config, preset)
            fmt.echo(f"  ✓ 已成功应用 {preset} 预设")
        except Exception as e:
            fmt.echo_error(f"  ✗ 应用预设失败: {e}")
            return

    # 保存配置
    tutor_config.save_config_file(context.root, config)

    compose._local_preflight(context.root, config)

    fmt.echo_info("\n✓ 基础配置已完成！")
    fmt.echo_info("接下来您可以运行以下命令开始部署：")
    fmt.echo(fmt.command("edops local launch"))


compose.add_commands(local)
local.add_command(edops_status)
local.add_command(healthcheck)
local.add_command(deployment_history)
local.add_command(rollback)
local.add_command(bootstrap)
