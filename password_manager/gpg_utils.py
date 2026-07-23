"""Utility methods for encrypting, decrypting, and merging secrets using GPG and YAML."""

import shutil
import subprocess
from pathlib import Path
from typing import List

import yaml


def _resolve_gpg_command() -> str:
    """Return the first available GPG executable, preferring gpg2 on Unix-like systems."""
    for candidate in ("gpg2", "gpg"):
        if shutil.which(candidate):
            return candidate
    raise RuntimeError(
        "Unable to find a GnuPG executable. Install GnuPG and ensure 'gpg' or 'gpg2' is on PATH."
    )


def run_gpg(arguments: List[str]) -> bytes:
    """Run a GPG command and return the raw output bytes."""
    executable = _resolve_gpg_command()
    command = [executable] + arguments[1:] if arguments and arguments[0] == "gpg" else arguments
    completed = subprocess.run(command, check=True, capture_output=True)
    return completed.stdout


def encrypt_file(plaintext_path: Path, output_path: Path) -> None:
    """Encrypt a plaintext file into a GPG file using symmetric AES256 encryption."""
    if not plaintext_path.is_file():
        raise FileNotFoundError(f"Plaintext file not found: {plaintext_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    arguments = [
        "gpg",
        "--batch",
        "--yes",
        "--symmetric",
        "--cipher-algo",
        "AES256",
        "-o",
        str(output_path),
        str(plaintext_path),
    ]
    run_gpg(arguments)


def decrypt_password(gpg_path: Path) -> str:
    """Decrypt a GPG file and return its plaintext content as a string."""
    if not gpg_path.is_file():
        raise FileNotFoundError(f"GPG file not found: {gpg_path}")

    arguments = ["gpg", "--batch", "--quiet", "--decrypt", str(gpg_path)]
    output = run_gpg(arguments)
    return output.decode().strip()


def merge_values(base_path: Path, password: str, output_path: Path, yaml_path: str = "password") -> None:
    """Merge a secret into a YAML file at the specified dot-separated path.

    The provided YAML path is a nested key path in the destination file.
    For example, yaml_path="database.password" will set:

        database:
          password: <secret>

    Existing YAML content is preserved, and only the final key is replaced.
    """
    if not base_path.is_file():
        raise FileNotFoundError(f"Base values file not found: {base_path}")

    with base_path.open("r", encoding="utf-8") as base_file:
        base_values = yaml.safe_load(base_file) or {}

    target = base_values
    keys = yaml_path.split(".") if yaml_path else ["password"]
    for key in keys[:-1]:
        target = target.setdefault(key, {})
    target[keys[-1]] = password

    with output_path.open("w", encoding="utf-8") as output_file:
        yaml.safe_dump(base_values, output_file, default_flow_style=False, sort_keys=False)
