from __future__ import annotations

import os

import click
import yaml

from tutor import bindmount, exceptions, fmt, hooks
from tutor import config as tutor_config
from tutor.commands.config import save as config_save
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam


class MountParamType(ConfigLoaderParam):
    name = "mount"

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        mounts = bindmount.get_mounts(self.config)
        return [
            click.shell_completion.CompletionItem(mount)
            for mount in mounts
            if mount.startswith(incomplete)
        ]


@click.group(name="mounts")
def mounts_command() -> None:
    """
<<<<<<< HEAD
    Manage host bind-mounts

    Bind-mounted folders are used both in image building, development (`dev` commands)
    and `local` deployments.
=======
    管理主机绑定挂载

    绑定挂载的文件夹在镜像构建、开发（`dev` 命令）和 `local` 部署中都会使用。
>>>>>>> origin/refactor/config-system-refactor
    """


@click.command(name="list")
@click.pass_obj
def mounts_list(context: Context) -> None:
    """
<<<<<<< HEAD
    List bind-mounted folders

    Entries will be fetched from the `MOUNTS` project setting.
=======
    列出绑定挂载的文件夹

    条目将从 `MOUNTS` 项目设置中获取。
>>>>>>> origin/refactor/config-system-refactor
    """
    config = tutor_config.load(context.root)
    mounts = []
    for mount_name in bindmount.get_mounts(config):
        build_mounts = [
            {"image": image_name, "context": stage_name}
            for image_name, stage_name in hooks.Filters.IMAGES_BUILD_MOUNTS.iterate(
                mount_name
            )
        ]
        compose_mounts = [
            {
                "service": service,
                "container_path": container_path,
            }
            for service, _host_path, container_path in bindmount.parse_mount(mount_name)
        ]
        mounts.append(
            {
                "name": mount_name,
                "build_mounts": build_mounts,
                "compose_mounts": compose_mounts,
            }
        )
    fmt.echo(yaml.dump(mounts, default_flow_style=False, sort_keys=False))


@click.command(name="add")
@click.argument("mounts", metavar="mount", type=click.Path(), nargs=-1)
@click.pass_context
def mounts_add(context: click.Context, mounts: list[str]) -> None:
    """
<<<<<<< HEAD
    Add a bind-mounted folder

    The bind-mounted folder will be added to the project configuration, in the ``MOUNTS``
    setting.

    Values passed to this command can take one of two forms. The first is explicit::

        tutor mounts add myservice:/host/path:/container/path

    The second is implicit::

        tutor mounts add /host/path

    With the explicit form, the value means "bind-mount the host folder /host/path to
    /container/path in the "myservice" container at run time".

    With the implicit form, plugins are in charge of automatically detecting in which
    containers and locations the /host/path folder should be bind-mounted. In this case,
    folders can be bind-mounted at build-time -- which cannot be achieved with the
    explicit form.
=======
    添加绑定挂载的文件夹

    绑定挂载的文件夹将添加到项目配置的 ``MOUNTS`` 设置中。

    传递给此命令的值可以采用两种形式。第一种是显式形式::

        edops mounts add myservice:/host/path:/container/path

    第二种是隐式形式::

        edops mounts add /host/path

    使用显式形式时，值表示"在运行时将主机文件夹 /host/path 绑定挂载到
    myservice 容器中的 /container/path"。

    使用隐式形式时，插件负责自动检测 /host/path 文件夹应该绑定挂载到
    哪些容器和位置。在这种情况下，文件夹可以在构建时绑定挂载
    -- 这在显式形式中无法实现。
>>>>>>> origin/refactor/config-system-refactor
    """
    new_mounts = []
    for mount in mounts:
        if not bindmount.parse_explicit_mount(mount):
<<<<<<< HEAD
            # Path is implicit: check that this path is valid
            # (we don't try to validate explicit mounts)
            mount = os.path.abspath(os.path.expanduser(mount))
            if not os.path.exists(mount):
                raise exceptions.TutorError(f"Path {mount} does not exist on the host")
        new_mounts.append(mount)
        fmt.echo_info(f"Adding bind-mount: {mount}")
=======
            # 路径是隐式的：检查此路径是否有效
            # （我们不尝试验证显式挂载）
            mount = os.path.abspath(os.path.expanduser(mount))
            if not os.path.exists(mount):
                raise exceptions.TutorError(f"路径 {mount} 在主机上不存在")
        new_mounts.append(mount)
        fmt.echo_info(f"正在添加绑定挂载: {mount}")
>>>>>>> origin/refactor/config-system-refactor

    context.invoke(config_save, append_vars=[("MOUNTS", mount) for mount in new_mounts])


@click.command(name="remove")
@click.argument("mounts", metavar="mount", type=MountParamType(), nargs=-1)
@click.pass_context
def mounts_remove(context: click.Context, mounts: list[str]) -> None:
    """
<<<<<<< HEAD
    Remove a bind-mounted folder

    The bind-mounted folder will be removed from the ``MOUNTS`` project setting.
=======
    移除绑定挂载的文件夹

    绑定挂载的文件夹将从 ``MOUNTS`` 项目设置中移除。
>>>>>>> origin/refactor/config-system-refactor
    """
    removed_mounts = []
    for mount in mounts:
        if not bindmount.parse_explicit_mount(mount):
<<<<<<< HEAD
            # Path is implicit: expand it
            mount = os.path.abspath(os.path.expanduser(mount))
        removed_mounts.append(mount)
        fmt.echo_info(f"Removing bind-mount: {mount}")
=======
            # 路径是隐式的：展开它
            mount = os.path.abspath(os.path.expanduser(mount))
        removed_mounts.append(mount)
        fmt.echo_info(f"正在移除绑定挂载: {mount}")
>>>>>>> origin/refactor/config-system-refactor

    context.invoke(
        config_save, remove_vars=[("MOUNTS", mount) for mount in removed_mounts]
    )


mounts_command.add_command(mounts_list)
mounts_command.add_command(mounts_add)
mounts_command.add_command(mounts_remove)
