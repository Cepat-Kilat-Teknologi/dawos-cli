# Installation

## Recommended: pip or pipx

=== "pip (Quick)"

    ```bash
    pip install dawos-cli
    ```

=== "pipx (Isolated)"

    ```bash
    pipx install dawos-cli
    ```

=== "Homebrew"

    ```bash
    brew install Cepat-Kilat-Teknologi/tap/dawos-cli
    ```

=== "One-line Installer"

    **Linux / macOS:**
    ```bash
    curl -fsSL https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.sh | bash
    ```

    **Windows (PowerShell):**
    ```powershell
    irm https://raw.githubusercontent.com/Cepat-Kilat-Teknologi/dawos-cli/main/installer.ps1 | iex
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
# Built-in (recommended)
dawos update

# Or manually
pip install --upgrade dawos-cli
```

## Uninstalling

```bash
# pip
pip uninstall dawos-cli

# pipx
pipx uninstall dawos-cli
```
