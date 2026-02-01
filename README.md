# Amazing Marvin API Scripts

My personal scripts for the Amazing Marvin task management system. Will use the [Marvin API](https://github.com/amazingmarvin/MarvinAPI/wiki/Marvin-API) or [direct access to the CloudAnt CouchDB](https://github.com/amazingmarvin/MarvinAPI/wiki/Database-Access) instance as necessary.

- API access with [httpx](https://github.com/projectdiscovery/httpx)
- DB access with [cloudant-python-sdk](https://github.com/IBM/cloudant-python-sdk) ([docs](https://ibm.github.io/cloudant-python-sdk/docs/latest/))

## TODOS

- Visualize task throughput with plotting lib or export to GSheets, etc.
- [DONE] Compute task throughput - tasks created v. finished over time

## SETUP

This project uses Nix + devenv.sh to provide a reproducible development environment that works identically across macOS and Linux.

**Project files:**
- `devenv.nix` - Main environment configuration with Python packages and tools
- `devenv.yaml` - Inputs configuration (for nixpkgs-python)  
- `devenv.lock` - Lock file (like package-lock.json, should be committed)

### Prerequisites: Install Nix

**On macOS and Linux:**
```bash
# Install Nix using the Determinate Nix Installer (recommended)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

The Determinate Nix Installer is preferred over the official installer because:
- Easier to uninstall if needed
- Automatically enables Nix flakes
- Smoother installation experience

**Alternative (official installer):**
```bash
# macOS
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install)

# Linux (with systemd)
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
```

### Install devenv.sh

After Nix is installed and you've restarted your shell:

```bash
# Install devenv
nix profile add nixpkgs#devenv
```

### Using the Development Environment

```bash
# Enter the development environment (first time will take a few minutes)
devenv shell

# This automatically:
# - Sets up Python 3.9
# - Creates a virtual environment
# - Installs all dependencies
# - Loads environment variables from .env
# - Provides helpful scripts

# Available scripts:
devenv shell test      # Run pytest
devenv shell format    # Run black + isort
devenv shell lint      # Run flake8
devenv shell notebook  # Start Jupyter
```

### Credentials Setup

Copy the `.env.example` file and edit with your credentials:

```bash
cp .env.example .env
```

Get Amazing Marvin credentials from [here](https://app.amazingmarvin.com/pre?api) and add to `.env`:
- `CLOUDANT_URL`, `CLOUDANT_SYNC_DB`, `CLOUDANT_USERNAME`, `CLOUDANT_PASSWORD` - CouchDB access
- `FULL_ACCESS_TOKEN` - Marvin API token

## Development Commands

```bash
devenv shell test      # Run tests
devenv shell format    # Format code (black + isort) 
devenv shell lint      # Lint code (flake8)
devenv shell notebook  # Start Jupyter notebook
```

## VSCode Integration

VSCode is pre-configured to work seamlessly with the devenv environment:

### Setup:
1. **Open project in VSCode**
2. **Install recommended extensions** (popup should appear) 
3. **Select Python interpreter**: `Cmd+Shift+P` → "Python: Select Interpreter" → Choose `.devenv/state/venv/bin/python`
4. **Reload window** if needed: `Cmd+Shift+P` → "Developer: Reload Window"

### Features:
- **IntelliSense and debugging** with devenv Python
- **Jupyter notebooks** render properly (uses inline matplotlib backend)
- **Auto-formatting** on save with Black (140 character line length)
- **Environment variables** automatically loaded from `.env`

### VSCode Troubleshooting:
- **"Invalid Python interpreter"**: Use full path `/Users/.../amazing-marvin/.devenv/state/venv/bin/python`
- **Charts not rendering**: Ensure `%matplotlib inline` is used, restart kernel if needed
- **Import errors**: Verify correct interpreter selected, reload VSCode window

## Troubleshooting

### Nix Installation Issues
- **macOS Catalina/Big Sur**: May need to restart terminal after installation
- **Linux without systemd**: Use single-user install: `--no-daemon` flag
- **Permission issues**: Never run Nix installer with sudo, use your regular user

### devenv Issues
- **First run very slow**: Initial `devenv shell` can take 10+ minutes to build entire environment (downloads Python, all packages, compiles tools). This is normal and only happens once.
- **Commands timeout**: If `devenv shell` times out, try:
  - Run in background: `devenv shell &` then wait for completion  
  - Use `devenv info` to verify configuration without building
  - Check progress: `devenv shell --verbose` shows build status
- **Binary cache warnings**: "Failed to set up binary caches" warnings are non-fatal if you see `cachix.enable = false` in `devenv.nix`
- **eval-cores warnings**: `warning: unknown setting 'eval-cores'` is harmless Nix version incompatibility
- **Python package not found**: Some packages may need to be added to `devenv.nix`
- **GitHub API rate limits**: Set `GITHUB_TOKEN` in environment for faster package downloads

