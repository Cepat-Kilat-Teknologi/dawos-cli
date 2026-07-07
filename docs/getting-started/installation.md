# Installation

## Recommended: pipx (isolated install)

=== "Linux / macOS"

    ```bash
    # One-line installer
    curl -fsSL https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.sh | bash
    ```

    Or manually:
    ```bash
    pipx install git+https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
    ```

=== "Windows"

    ```powershell
    irm https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.ps1 | iex
    ```

    Or manually:
    ```powershell
    pipx install git+https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git
    ```

=== "PyPI"

    ```bash
    pipx install dawos-cli
    # or
    pip install dawos-cli
    ```

## Requirements

| Requirement | Version |
|-------------|---------|
| Python      | 3.9+    |
| pipx        | Any     |

!!! tip "Don't have pipx?"
    The installer script will install pipx automatically if missing.

## Verify Installation

```bash
dawos --version
```

## Shell Completion

=== "Bash"

    ```bash
    dawos --install-completion bash
    source ~/.bashrc
    ```

=== "Zsh"

    ```bash
    dawos --install-completion zsh
    source ~/.zshrc
    ```

=== "Fish"

    ```bash
    dawos --install-completion fish
    ```

=== "PowerShell"

    ```powershell
    dawos --install-completion powershell
    ```

## Updating

```bash
dawos update
```

## Uninstalling

```bash
pipx uninstall dawos-cli
```
