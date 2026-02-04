import os
import pathlib
import tempfile
import unittest
import json
from unittest.mock import patch

from tests.helpers import temporary_root

from .base import TestCommandMixin


class LocalTests(unittest.TestCase, TestCommandMixin):
    def test_local_help(self) -> None:
        result = self.invoke(["local", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_local_launch_help(self) -> None:
        result = self.invoke(["local", "launch", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_local_upgrade_help(self) -> None:
        result = self.invoke(["local", "upgrade", "--help"])
        self.assertIsNone(result.exception)
        self.assertEqual(0, result.exit_code)

    def test_copyfrom(self) -> None:
        with temporary_root() as root:
            with tempfile.TemporaryDirectory() as directory:
                # resolve actual path, just like click.Path does it.
                directory = os.fsdecode(pathlib.Path(directory).resolve())
                with patch("tutor.utils.docker_compose") as mock_docker_compose:
                    self.invoke_in_root(root, ["config", "save"])

                    # Copy to existing directory
                    result = self.invoke_in_root(
                        root, ["local", "copyfrom", "lms", "/openedx/venv", directory]
                    )
                    self.assertIsNone(result.exception)
                    self.assertEqual(0, result.exit_code)
                    self.assertIn(
                        f"--volume={directory}:/tmp/mount",
                        mock_docker_compose.call_args[0],
                    )
                    self.assertIn(
                        "cp --recursive --preserve /openedx/venv /tmp/mount",
                        mock_docker_compose.call_args[0],
                    )

                    # Copy to non-existing directory
                    result = self.invoke_in_root(
                        root,
                        [
                            "local",
                            "copyfrom",
                            "lms",
                            "/openedx/venv",
                            os.path.join(directory, "venv2"),
                        ],
                    )
                    self.assertIsNone(result.exception)
                    self.assertEqual(0, result.exit_code)
                    self.assertIn(
                        f"--volume={directory}:/tmp/mount",
                        mock_docker_compose.call_args[0],
                    )
                    self.assertIn(
                        "cp --recursive --preserve /openedx/venv /tmp/mount/venv2",
                        mock_docker_compose.call_args[0],
                    )

    def test_local_bootstrap_copies_nginx_assets(self) -> None:
        with temporary_root() as root:
            base_path = os.path.join(root, "edops-base")
            result = self.invoke_in_root(
                root, ["config", "save", "--set", f"EDOPS_BASE_PATH={base_path}"]
            )
            self.assertIsNone(result.exception)

            with patch("tutor.utils.check_output") as mock_check_output:
                mock_check_output.return_value = ""
                result = self.invoke_in_root(root, ["local", "bootstrap"])
                self.assertIsNone(result.exception)
                self.assertEqual(0, result.exit_code)

            for filename in (
                "nginx.conf",
                "portal_ly-sky_com.key",
                "portal_ly-sky_com.crt",
            ):
                self.assertTrue(os.path.exists(os.path.join(base_path, filename)))

    def test_local_healthcheck_success(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])

            def fake_check_output(*args, **kwargs):
                if "config" in args and "--services" in args:
                    return b"zhjx-nacos\nzhjx-redis\n"
                if "ps" in args and "--format" in args:
                    return json.dumps(
                        [
                            {"Service": "zhjx-nacos", "State": "running", "Status": "Up"},
                            {"Service": "zhjx-redis", "State": "running", "Status": "Up"},
                        ]
                    ).encode("utf-8")
                return b""

            with patch("tutor.utils.check_output", side_effect=fake_check_output), patch(
                "tutor.commands.local.time.sleep"
            ):
                result = self.invoke_in_root(root, ["local", "healthcheck", "base"])
            self.assertIsNone(result.exception)
            self.assertEqual(0, result.exit_code)

    def test_local_healthcheck_failure(self) -> None:
        with temporary_root() as root:
            self.invoke_in_root(root, ["config", "save"])

            def fake_check_output(*args, **kwargs):
                if "config" in args and "--services" in args:
                    return b"zhjx-nacos\nzhjx-redis\n"
                if "ps" in args and "--format" in args:
                    return json.dumps(
                        [
                            {"Service": "zhjx-nacos", "State": "running", "Status": "Up"},
                        ]
                    ).encode("utf-8")
                return b""

            with patch("tutor.utils.check_output", side_effect=fake_check_output), patch(
                "tutor.commands.local.time.sleep"
            ):
                result = self.invoke_in_root(root, ["local", "healthcheck", "base"])
            self.assertNotEqual(0, result.exit_code)
            self.assertIn("zhjx-redis", result.output)
