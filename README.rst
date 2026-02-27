.. _Tutor: https://github.com/overhangio/tutor
.. _QUICKSTART_CN.md: QUICKSTART_CN.md
.. _agents.md: agents.md
.. _docs/edops-cli.md: docs/edops-cli.md
.. _docs/DESIGN_DECISIONS_CN.md: docs/DESIGN_DECISIONS_CN.md
.. _docs/zhjx-modules.md: docs/zhjx-modules.md
.. _docs/reports/: docs/reports/

EdOps：面向 zhjx 体系的统一部署 CLI
===================================

EdOps 是什么？
-------------

EdOps 是一款命令行界面（CLI）工具，旨在为 zhjx 系列业务系统提供标准化的部署与配置方案。它是强大的 `Tutor`_ 框架的一个分支，继承了其基于模板渲染、Docker Compose 和模块化插件系统的稳健架构。

Tutor 主要专注于部署 Open edX，而 EdOps 则专门针对 zhjx 的需求进行了定制，为管理从本地开发到生产集群的各种环境提供了统一的工作流。

核心概念
--------

### 1. 部署框架，而非业务系统

理解 EdOps 的关键在于其定位：它是一个 **部署与配置工具**。它本身不包含任何业务逻辑，而是提供了一套脚手架，用于部署和管理其他应用，确保它们以一致且可复现的方式进行配置和启动。

### 2. 模块化架构

EdOps 采用模块化架构来管理 zhjx 系统的不同组件。该架构层次清晰：

- **`base` 模块：** 此模块始终启用，提供所有其他模块所依赖的核心基础设施服务，如 Nacos、MySQL、Minio、Redis 和消息队列。
- **`common` 模块：** 此模块也始终启用，提供 zhjx 所有业务系统共享的通用服务，通常包括用户管理、认证、后台管理面板和 API 网关。
- **`zhjx_*` 模块：** 这些是可选的业务模块，提供特定功能，例如用于媒体流处理的 `zhjx_zlmediakit`。可以根据具体部署需求启用或禁用这些模块。

### 3. 集中化配置

EdOps 部署的所有配置都通过单一的 `config.yml` 文件进行管理。该文件控制着从镜像版本、域名到数据库凭据的所有内容。这种集中化的方法使得环境复制和审计变得简单。

要启用或禁用 `zhjx_*` 模块，您需要在配置文件中使用 `RUN_ZHJX_*` 开关。例如：

.. code-block:: yaml

  RUN_ZHJX_ZLMEDIAKIT: true
  RUN_ZHJX_ILIVE_ECOM: true

`base` 和 `common` 模块始终处于启用状态，无需在此处修改。

### 4. 环境一致性

EdOps 本期聚焦 `local` 与 `portainer` 两种可交付模式，K8s 入口在 CLI 中屏蔽（代码保留，后续迭代再开放）。

- **`dev`：** 用于本地开发，支持热重载和便捷调试。
- **`local`：** 用于单机生产部署，使用 Docker Compose。
- **`portainer`：** 用于输出 Docker Swarm stack 文件并在 Portainer/Swarm 中部署。

快速入门
--------

**方式 A（推荐）：一键下载安装并初始化**

.. code-block:: bash

  curl -fsSL https://raw.githubusercontent.com/GitHubZhuMin/edops/edops/install.sh | bash

默认会执行安装与初始化流程：

- 克隆源码到 ``~/.edops/src``
- 安装 CLI 到 ``~/.edops/venv``
- 自动写入 shell 环境变量（可直接全局执行 ``edops``）
- 默认自动激活 EdOps 虚拟环境（可用 ``--skip-auto-activate`` 关闭）
- 执行 ``edops config save --init --preset standard``
- 执行 ``edops local bootstrap``

若 Docker daemon 尚未启动，脚本会自动跳过 bootstrap，并提示后续手动补跑命令。

如需跳过 bootstrap（仅安装+初始化配置）：

.. code-block:: bash

  curl -fsSL https://raw.githubusercontent.com/GitHubZhuMin/edops/edops/install.sh | \
    bash -s -- --skip-bootstrap

**方式 B：手动安装**

1.  **克隆仓库：**

    .. code-block:: bash

      git clone https://your-repo-url/edops.git
      cd edops

2.  **创建并激活虚拟环境：**

    .. code-block:: bash

      python3 -m venv venv
      source venv/bin/activate

3.  **以可编辑模式安装 EdOps：**

    .. code-block:: bash

      pip install -e .

4.  **初始化配置：**

    .. code-block:: bash

      edops config save --interactive

    此命令将引导您完成初始设置并创建 `config.yml` 文件。

5.  **启动平台：**

    .. code-block:: bash

      edops local launch

更详细的说明，请参阅 `QUICKSTART_CN.md`_ 指南。

致开发者和贡献者
--------------------

本仓库在 AI Agent 的协助下进行管理。为确保顺畅协作，请阅读 `agents.md`_ 文件，其中包含了 AI 在与此代码库互动时需遵循的重要准则。

进一步阅读
----------

- **快速上手:** `QUICKSTART_CN.md`_ - 5 分钟快速入门指南。
- **参考文档:**
  - `CLI 参考`_ - 完整的 CLI 命令参考手册。
  - `设计决策`_ - 核心设计决策与技术共识。
  - `模块指南`_ - 模块说明与配置。
- **报告:**
  - `报告归档`_ - 实施报告、错误修复记录和测试指南。
