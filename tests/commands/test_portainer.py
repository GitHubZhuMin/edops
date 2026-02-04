import os
import unittest
from unittest.mock import patch

from tests.helpers import temporary_root

from .base import TestCommandMixin


class PortainerTests(unittest.TestCase, TestCommandMixin):
    def test_portainer_render_generates_stack(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            with patch(
                "tutor.utils.check_output",
                return_value=b"services:\n  demo:\n    image: demo:latest\n",
            ):
                result = self.invoke_in_root(root, ["portainer", "render"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            stack_file = os.path.join(root, "portainer", "docker-stack.yml")
            self.assertTrue(os.path.exists(stack_file))
            self.assertIn("docker stack deploy -c", result.output)

    def test_portainer_render_module_uses_dependency_closure(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])
            captured: list[str] = []

            def fake_check_output(*args, **kwargs):
                captured.extend([str(arg) for arg in args])
                return b"services:\n  demo:\n    image: demo:latest\n"

            with patch("tutor.utils.check_output", side_effect=fake_check_output):
                result = self.invoke_in_root(
                    root, ["portainer", "render", "zhjx_media"]
                )
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)
            stack_file = os.path.join(root, "portainer", "docker-stack.zhjx_media.yml")
            self.assertTrue(os.path.exists(stack_file))
            compose_line = " ".join(captured)
            self.assertIn("zhjx-base.yml", compose_line)
            self.assertIn("zhjx-common.yml", compose_line)
            self.assertIn("zhjx-zlmediakit.yml", compose_line)
            self.assertIn("zhjx-media.yml", compose_line)
