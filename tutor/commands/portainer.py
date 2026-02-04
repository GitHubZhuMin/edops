"""EdOps 的 Portainer / Docker Swarm 部署命令。"""
from __future__ import annotations

from pathlib import Path

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt, utils
from tutor.commands.context import Context
from tutor.types import Config, get_typed

MODULE_FILES: dict[str, str] = {
    "base": "zhjx-base.yml",
    "common": "zhjx-common.yml",
    "zhjx_zlmediakit": "zhjx-zlmediakit.yml",
    "zhjx_ilive_ecom": "zhjx-ilive-ecom.yml",
    "zhjx_sup": "zhjx-sup.yml",
    "zhjx_media": "zhjx-media.yml",
    "zhjx_ykt": "zhjx-ykt.yml",
}

MODULE_DEPS: dict[str, list[str]] = {
    "base": [],
    "common": ["base"],
    "zhjx_zlmediakit": ["base"],
    "zhjx_ilive_ecom": ["common"],
    "zhjx_sup": ["common"],
    "zhjx_media": ["common", "zhjx_zlmediakit"],
    "zhjx_ykt": ["common"],
}

OPTIONAL_MODULE_FLAGS: dict[str, str] = {
    "zhjx_zlmediakit": "RUN_ZHJX_ZLMEDIAKIT",
    "zhjx_ilive_ecom": "RUN_ZHJX_ILIVE_ECOM",
    "zhjx_sup": "RUN_ZHJX_SUP",
    "zhjx_media": "RUN_ZHJX_MEDIA",
    "zhjx_ykt": "RUN_ZHJX_YKT",
}


def _resolve_module_closure(module_name: str) -> list[str]:
    if module_name not in MODULE_FILES:
        available = ", ".join(MODULE_FILES.keys())
        raise exceptions.TutorError(
            f"未知模块 '{module_name}'。可选值: {available}"
        )

    ordered: list[str] = []
    seen: set[str] = set()

    def add_module(name: str) -> None:
        if name in seen:
            return
        for dep in MODULE_DEPS.get(name, []):
            add_module(dep)
        seen.add(name)
        ordered.append(name)

    add_module(module_name)
    return ordered


def _get_enabled_modules(config: Config) -> list[str]:
    enabled = ["base", "common"]
    for module_name, flag_name in OPTIONAL_MODULE_FLAGS.items():
        if config.get(flag_name, False):
            enabled.append(module_name)
    return enabled


def _build_compose_files(
    root: str, module_names: list[str], include_overrides: bool
) -> list[str]:
    files = [
        tutor_env.pathjoin(root, "local", "docker-compose.yml"),
        tutor_env.pathjoin(root, "local", "docker-compose.prod.yml"),
    ]
    if include_overrides:
        files.extend(
            [
                tutor_env.pathjoin(root, "local", "docker-compose.override.yml"),
                tutor_env.pathjoin(root, "local", "docker-compose.prod.override.yml"),
            ]
        )
    for module_name in module_names:
        files.append(tutor_env.pathjoin(root, "local", MODULE_FILES[module_name]))

    return [path for path in files if Path(path).exists()]


@click.group(help="部署 EdOps 到 Portainer / Docker Swarm")
@click.pass_context
def portainer(context: click.Context) -> None:
    """Portainer 部署命令。"""
    context.obj = Context(context.obj.root)


@click.command(help="渲染 Portainer / Swarm 模板")
@click.argument("module_name", required=False)
@click.pass_obj
def render(context: Context, module_name: str | None) -> None:
    """渲染 Portainer 部署模板并输出 stack 文件。"""
    config = tutor_config.load_full(context.root)
    tutor_env.save(context.root, config)

    if module_name:
        module_names = _resolve_module_closure(module_name)
        output_name = f"docker-stack.{module_name}.yml"
    else:
        module_names = _get_enabled_modules(config)
        output_name = "docker-stack.yml"

    compose_files = _build_compose_files(
        context.root, module_names, include_overrides=True
    )
    if not compose_files:
        raise exceptions.TutorError("未找到可用的 compose 文件，无法渲染 Portainer stack。")

    project_name = get_typed(config, "LOCAL_PROJECT_NAME", str, "edops_local")
    command: list[str] = ["docker", "compose"]
    for compose_file in compose_files:
        command.extend(["-f", compose_file])
    command.extend(["--project-name", project_name, "config"])

    rendered = utils.check_output(*command).decode("utf-8")

    output_dir = Path(context.root) / "portainer"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_name
    output_path.write_text(rendered, encoding="utf-8")

    stack_name = project_name.replace("_", "-")
    fmt.echo_info(f"已生成 Portainer Stack 文件: {output_path}")
    fmt.echo_info(f"包含模块: {', '.join(module_names)}")
    fmt.echo_info("部署示例：")
    fmt.echo(fmt.command(f"docker stack deploy -c {output_path} {stack_name}"))


portainer.add_command(render)
