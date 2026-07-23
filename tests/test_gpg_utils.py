import unittest
from types import SimpleNamespace
from unittest.mock import patch

from password_manager.gpg_utils import run_gpg


class RunGpgTests(unittest.TestCase):
    def test_missing_gpg_binary_raises_helpful_error(self):
        with patch("password_manager.gpg_utils.shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Install GnuPG"):
                run_gpg(["gpg", "--version"])

    def test_uses_gpg2_when_available(self):
        with patch("password_manager.gpg_utils.shutil.which", side_effect=lambda name: "/usr/bin/gpg2" if name == "gpg2" else None):
            with patch("password_manager.gpg_utils.subprocess.run", return_value=SimpleNamespace(stdout=b"ok")) as mock_run:
                output = run_gpg(["gpg", "--version"])

        self.assertEqual(output, b"ok")
        self.assertEqual(mock_run.call_args.args[0][0], "gpg2")


if __name__ == "__main__":
    unittest.main()
