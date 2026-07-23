# password-manager 🚀

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub](https://img.shields.io/badge/GitHub-Repository-black)

## Overview 🌐

`password-manager` is a standalone Python CLI for managing encrypted secrets across repositories.
It wraps common GPG operations, so you do not need to remember raw GPG commands.

It can:

- encrypt plaintext secrets to a GPG file
- decrypt the GPG file on demand
- merge decrypted secrets into arbitrary YAML files
- store repository secrets in a central directory for reuse across projects
- keep secret values out of version control

## Prerequisites 🧩

- Python 3.8+
- GnuPG (the `gpg` or `gpg2` executable must be available on your PATH)
- pip or pip3

## Installation 🛠️

Before installing the package, make sure GnuPG is installed on your machine.

- On Windows, install Gpg4win from https://www.gpg4win.org/
- On macOS, install GnuPG via Homebrew: `brew install gnupg`
- On Linux, install it with your package manager (for example `sudo apt install gnupg`)

Create and activate a local virtual environment named `.venv`:

```bash
python -m venv .venv
```

On Windows PowerShell:


```powershell
.\.venv\Scripts\activate.bat
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the package in editable mode from the repository root:

```bash
python -m pip install -e .
```

## Usage 🚀

Encrypt a plaintext secret file:

```bash
password-manager encrypt secret.txt secret.gpg
```

Decrypt a secret file to stdout:

```bash
password-manager decrypt secret.gpg
```

Decrypt a secret file to a local path:

```bash
password-manager decrypt secret.gpg --output decrypted.txt
```

Merge a decrypted secret into a YAML file.
The command injects the secret into an existing YAML structure at the specified nested key path.

For example, if `path/to/values.yaml` contains:

```yaml
database:
  user: app
  password: ""
```

then this command will produce a file where `database.password` is replaced with the decrypted secret:

```bash
password-manager merge secret.gpg values.secret.yaml --base path/to/values.yaml --yaml-path database.password
```

Use a shared secret store directory across repositories:

```bash
password-manager encrypt secret.txt secrets/secret.gpg --store ~/.password-manager
password-manager decrypt secret.gpg --store ~/.password-manager
```

## Project layout 📁

- `password_manager/` - Python package implementation
- `pyproject.toml` - package metadata and dependencies
- `README.md` - usage documentation
- `requirements.txt` - dependency list

## Notes 📝

- The package is intentionally standalone so any repository can reuse the password handling logic.
- The generated `values.secret.yaml` file should never be committed to source control.
