# EdOps: A Unified Deployment CLI for ZHJX Systems

## What is EdOps?

EdOps is a command-line interface (CLI) tool designed to standardize the deployment and configuration of the ZHJX family of business systems. It is a fork of the powerful [Tutor](https://github.com/overhangio/tutor) framework, inheriting its robust architecture based on template rendering, Docker Compose, and a modular plugin system.

While Tutor is primarily focused on deploying Open edX, EdOps is tailored specifically for the needs of ZHJX, providing a consistent workflow for managing environments from local development to production clusters.

## Core Concepts

### 1. A Deployment Framework, Not a Business System

The most important thing to understand about EdOps is its role: it is a **deployment and configuration tool**. It does not contain business logic itself. Instead, it provides the scaffolding to deploy and manage other applications, ensuring that they are configured and launched in a consistent and reproducible way.

### 2. Modular Architecture

EdOps uses a modular architecture to manage different components of the ZHJX system. This architecture is organized in a clear hierarchy:

- **`base` Module:** This module is always enabled and provides the core infrastructure services that all other modules depend on. This includes services like Nacos, MySQL, Minio, Redis, and message queues.
- **`common` Module:** Also always enabled, this module provides the shared services that are common across all ZHJX business systems. This typically includes user management, authentication, a backend admin panel, and an API gateway.
- **`zhjx-*` Modules:** These are the optional business modules that provide specific functionalities, such as `zhjx-zlmediakit` for media streaming. Each of these modules can be enabled or disabled based on the needs of a particular deployment.

### 3. Centralized Configuration

All configuration for an EdOps deployment is managed through a single `edops-config.yml` file. This file controls everything from image versions and domain names to database credentials. This centralized approach allows for easy environment replication and auditing.

To enable or disable `zhjx-*` modules, you use the `EDOPS_ENABLED_MODULES` setting in your configuration file. For example:

```yaml
EDOPS_ENABLED_MODULES:
  - zhjx-zlmediakit
  - zhjx-another-module
```

The `base` and `common` modules are always enabled and do not need to be listed here.

### 4. Consistent Environments

EdOps inherits Tutor's support for multiple deployment environments, ensuring that the behavior of your applications is consistent whether you are running them on your local machine for development, on a single server, or in a Kubernetes cluster.

- **`dev`:** For local development, with support for hot-reloading and easy debugging.
- **`local`:** For single-server production deployments, using Docker Compose.
- **`k8s`:** For multi-node, scalable deployments on Kubernetes.

## Quickstart

1.  **Clone the repository:**
    ```bash
    git clone https://your-repo-url/edops.git
    cd edops
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install EdOps in editable mode:**
    ```bash
    pip install -e .
    ```

4.  **Initialize your configuration:**
    ```bash
    edops config save --interactive
    ```
    This will walk you through the initial setup and create your `edops-config.yml` file.

5.  **Launch the platform:**
    ```bash
    edops local launch
    ```

For more detailed instructions, please refer to the [QUICKSTART_CN.md](QUICKSTART_CN.md) guide.

## For Developers and Contributors

This repository is managed with the help of AI agents. To ensure smooth collaboration, please read the [agents.md](agents.md) file, which contains important guidelines for the AI on how to interact with this codebase.

## Further Reading

- **Quickstart:** [QUICKSTART_CN.md](QUICKSTART_CN.md) - A 5-minute guide to get started.
- **Reference:**
  - [CLI Reference](docs/edops-cli.md) - A complete reference manual for the CLI.
  - [Design Decisions](docs/DESIGN_DECISIONS_CN.md) - Core design decisions and technical consensus.
  - [Module Guide](docs/zhjx-modules.md) - Descriptions and configuration for modules.
- **Reports:**
  - [Reports Archive](docs/reports/) - Implementation reports, bug fix records, and test guides.
