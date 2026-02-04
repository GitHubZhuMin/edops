import unittest

from .base import TestCommandMixin


class K8sTests(unittest.TestCase, TestCommandMixin):
    def test_k8s_command_is_hidden(self) -> None:
        result = self.invoke(["k8s", "--help"])
        self.assertNotEqual(0, result.exit_code)
        self.assertIn("No such command", result.output)
