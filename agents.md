# AGENTS.md

## Repository Expectations

This document provides guidelines for AI agents working in the `edops` repository. Adhering to these rules is crucial for maintaining code quality, stability, and a clear architectural vision.

### Core Principles

- **`edops` is a unified deployment CLI, not a business application.** Its primary role is to provide a consistent deployment and configuration framework based on Tutor. All modifications must reinforce this identity.
- **Modularity is key.** The system is designed with a clear hierarchy: `base` provides fundamental infrastructure, `common` offers shared services, and `zhjx-*` modules contain specific business logic. Respect this separation.
- **Backward compatibility is a priority.** Legacy configurations (e.g., `RUN_*` flags) are maintained for a transition period but are not the source of truth. The `EDOPS_ENABLED_MODULES` setting is the definitive configuration driver.

## Agent Responsibilities

### Module Governance

- **`base` and `common` are foundational.** Do not add business-specific logic to these modules. They should remain generic and reusable.
- **Business logic belongs in `zhjx-*` modules.** When adding new features, create or extend a `zhjx-*` module.
- **Module dependencies must be explicit.** A `zhjx-*` module should depend on `common` and `base`, but not on other `zhjx-*` modules unless explicitly approved.

### Prohibited Actions

- **Do not alter the upstream Tutor structure.** The `tutor/` directory is named to maintain compatibility with the original Tutor framework. Do not rename it or fundamentally change its internal structure.
- **Do not modify Open edX deployment paths.** `edops` is designed to coexist with and manage Open edX, not to alter its core deployment mechanisms. Any changes that could break compatibility with upstream Open edX are forbidden.
- **Do not introduce new core configuration mechanisms.** All module enablement and configuration should be managed through `EDOPS_ENABLED_MODULES` and the existing `edops-config.yml` system. Avoid creating new, parallel configuration systems.

### Handling Legacy Code

- **Treat `RUN_*` flags as a compatibility layer.** When encountering `RUN_*` flags in the code, understand that they are synchronized with `EDOPS_ENABLED_MODULES`. The modern `EDOPS_ENABLED_MODULES` is the single source of truth.
- **Do not extend legacy systems.** When implementing new features, do not add new `RUN_*` flags. Use the `EDOPS_ENABLED_MODULES` list.
- **Prioritize `EDOPS_ENABLED_MODULES` in logic.** When reading configuration, your code should prefer `EDOPS_ENABLED_MODULES`.

## Safety and Verification

- **Always run tests.** After making any changes to Python code, run the relevant tests using `python -m pytest tests/`.
- **Verify template rendering.** If you modify any templates in `tutor/templates/`, use `edops config render <module-name>` to ensure your changes render correctly.
- **Ask for clarification.** If a task seems to conflict with these guidelines or the project's architecture, ask for confirmation before proceeding.
