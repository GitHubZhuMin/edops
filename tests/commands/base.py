from __future__ import annotations

<<<<<<< HEAD
import inspect

import click.testing

from tests.helpers import TestContext, temporary_root
from tutor.commands import compose
=======
import click.testing

from tests.helpers import TestContext, temporary_root
>>>>>>> origin/refactor/config-system-refactor
from tutor.commands.cli import cli


class TestCommandMixin:
    """
    Run CLI tests in an isolated test root.
    """

    @staticmethod
    def invoke(args: list[str]) -> click.testing.Result:
        with temporary_root() as root:
            return TestCommandMixin.invoke_in_root(root, args)

    @staticmethod
    def invoke_in_root(
        root: str, args: list[str], catch_exceptions: bool = True
    ) -> click.testing.Result:
        """
        Use this method for commands that all need to run in the same root:

            with temporary_root() as root:
                result1 = self.invoke_in_root(root, ...)
                result2 = self.invoke_in_root(root, ...)
        """
<<<<<<< HEAD
        compose.ComposeTaskRunner.HOOK_FIRED = True
        runner_kwargs = {
            "env": {
                "TUTOR_ROOT": root,
                "TUTOR_IGNORE_ENTRYPOINT_PLUGINS": "1",
                "TUTOR_IGNORE_DICT_PLUGINS": "1",
                # Disable plugin auto-loading and root warnings during tests
                "TUTOR_PLUGINS": "[]",
                "TUTOR_IGNORE_ROOT_WARNING": "1",
            }
        }
        if "mix_stderr" in inspect.signature(click.testing.CliRunner).parameters:
            runner_kwargs["mix_stderr"] = False
        runner = click.testing.CliRunner(**runner_kwargs)
        return runner.invoke(
            cli,
            args,
            obj=TestContext(root),
            catch_exceptions=catch_exceptions,
            input="\n" * 50,
=======
        runner = click.testing.CliRunner(
            env={
                "TUTOR_ROOT": root,
                "TUTOR_IGNORE_ENTRYPOINT_PLUGINS": "1",
                "TUTOR_IGNORE_DICT_PLUGINS": "1",
            },
            mix_stderr=False,
        )
        return runner.invoke(
            cli, args, obj=TestContext(root), catch_exceptions=catch_exceptions
>>>>>>> origin/refactor/config-system-refactor
        )
