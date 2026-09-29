"""Foundation CLI behavior, independent of any provider data."""

import importlib.util
import shutil
import subprocess
import unittest
from pathlib import Path


class CliContract(unittest.TestCase):
    def test_package_is_installable(self):
        self.assertIsNotNone(
            importlib.util.find_spec("changecost"), "foundation package is missing"
        )

    def test_offline_read_only_entrypoint(self):
        self.assertIsNotNone(
            importlib.util.find_spec("changecost"), "foundation package is missing"
        )
        import os

        entrypoint = shutil.which("changecost")
        self.assertIsNotNone(entrypoint, "installed console script missing from PATH")
        assert entrypoint is not None
        import tempfile
        from importlib.metadata import version

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            guard = root / "guard"
            guard.mkdir()
            (guard / "sitecustomize.py").write_text(
                'import socket\ndef blocked(*a, **k):\n raise RuntimeError("network forbidden")\n'
                "socket.socket = blocked\nsocket.create_connection = blocked\n"
            )
            home = root / "home"
            home.mkdir()
            work = root / "work"
            work.mkdir()
            env = dict(
                os.environ,
                HOME=str(home),
                XDG_CONFIG_HOME=str(home),
                XDG_DATA_HOME=str(home),
                PYTHONPATH=str(guard),
                PYTHONDONTWRITEBYTECODE="1",
                NO_COLOR="1",
                TERM="dumb",
            )
            for args, expected in [(["--help"], 0), (["--version"], 0), ([], 2), (["quote"], 2)]:
                with self.subTest(args=args):
                    result = subprocess.run(
                        [entrypoint, *args],
                        cwd=work,
                        env=env,
                        capture_output=True,
                        check=False,
                        text=True,
                    )
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                    if args == ["--version"]:
                        self.assertEqual(result.stdout.strip(), version("changecost"))
                    if args == ["--help"]:
                        self.assertIn("--version", result.stdout)
                        for command in ("bind", "settle", "explain"):
                            self.assertIn(command, result.stdout)
                    self.assertEqual(list(home.iterdir()), [])
                    self.assertEqual(list(work.iterdir()), [])
            self.prove_contract_roundtrip(entrypoint, work, env)

    def prove_contract_roundtrip(self, entrypoint, work, env):
        """Exercise the installed distribution without source imports or network."""

        def invoke(db, *args):
            result = subprocess.run(
                [entrypoint, "--db", str(work / db), *args],
                cwd=work,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result.stdout

        invoke(
            "source.sqlite",
            "bind",
            "--register-change",
            "--repository-id",
            "demo",
            "--change-id",
            "c",
        )
        invoke(
            "source.sqlite",
            "bind",
            "--register-run",
            "--repository-id",
            "demo",
            "--change-id",
            "c",
            "--provider",
            "synthetic",
            "--surface",
            "cli",
            "--run-id",
            "r",
        )
        invoke(
            "source.sqlite",
            "settle",
            "--repository-id",
            "demo",
            "--provider",
            "synthetic",
            "--surface",
            "cli",
            "--run-id",
            "r",
            "--run-outcome",
            "failed",
        )
        invoke("source.sqlite", "explain", "--export-artifact", str(work / "bundle.json"))
        for _ in range(2):
            invoke("destination.sqlite", "bind", "--import-artifact", str(work / "bundle.json"))
        result = invoke(
            "destination.sqlite",
            "explain",
            "--repository-id",
            "demo",
            "--provider",
            "synthetic",
            "--surface",
            "cli",
            "--run-id",
            "r",
        )
        import json

        self.assertEqual(json.loads(result)["revisions"][0]["outcome"], "failed")


if __name__ == "__main__":
    unittest.main()
