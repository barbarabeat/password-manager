from __future__ import annotations

"""CLI wrapper for password-manager operations."""

import argparse
import os
from pathlib import Path
from typing import Sequence

from .gpg_utils import decrypt_password, encrypt_file, merge_values


def resolve_store_path(path: Path, store: Path | None) -> Path:
    """Resolve a path relative to the provided secret store directory."""
    if path.is_absolute() or store is None:
        return path
    return (store / path).expanduser()


def default_store() -> Path:
    """Return the default secret store directory path."""
    return Path(os.getenv("PASSWORD_MANAGER_STORE", "~/.password-manager")).expanduser()


def build_parser() -> argparse.ArgumentParser:
    """Build and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Manage encrypted secrets with GPG in a reusable way across repositories."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a plaintext secret file.")
    encrypt_parser.add_argument("plaintext_file", type=Path, help="Plaintext secret file.")
    encrypt_parser.add_argument("output_gpg", type=Path, help="GPG output file name.")
    encrypt_parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help="Optional central secrets store directory.",
    )

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a GPG secret.")
    decrypt_parser.add_argument("gpg_file", type=Path, help="Encrypted GPG secret file.")
    decrypt_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write decrypted secret to a file. Defaults to stdout.",
    )
    decrypt_parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help="Optional central secrets store directory.",
    )

    merge_parser = subparsers.add_parser(
        "merge",
        help="Decrypt a secret and merge it into a YAML file at a key path.",
    )
    merge_parser.add_argument("gpg_file", type=Path, help="Encrypted GPG secret file.")
    merge_parser.add_argument("output_values", type=Path, help="Output YAML file.")
    merge_parser.add_argument(
        "--base",
        type=Path,
        default=Path("values.yaml"),
        help="Base YAML file to merge with (default: values.yaml).",
    )
    merge_parser.add_argument(
        "--yaml-path",
        type=str,
        default="password",
        help="Dot-separated key path where the secret should be placed in YAML.",
    )
    merge_parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help="Optional central secrets store directory.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse CLI arguments and execute the selected password-manager command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "encrypt":
        store = default_store() if args.store is None else args.store.expanduser()
        output_gpg = resolve_store_path(args.output_gpg, store)
        encrypt_file(args.plaintext_file, output_gpg)
        print(f"Encrypted file created at: {output_gpg}")
    elif args.command == "decrypt":
        store = default_store() if args.store is None else args.store.expanduser()
        gpg_file = resolve_store_path(args.gpg_file, store)
        secret = decrypt_password(gpg_file)
        if args.output:
            args.output.write_text(secret, encoding="utf-8")
            print(f"Decrypted secret written to: {args.output}")
        else:
            print(secret)
    elif args.command == "merge":
        store = default_store() if args.store is None else args.store.expanduser()
        gpg_file = resolve_store_path(args.gpg_file, store)
        password = decrypt_password(gpg_file)
        if not password:
            raise ValueError("Decrypted secret is empty.")
        merge_values(args.base, password, args.output_values, args.yaml_path)
        print(f"Secure YAML file created at: {args.output_values}")


if __name__ == "__main__":
    main()
