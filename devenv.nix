{ pkgs, ... }: {
  # Enable Python 3.9 with venv support
  languages.python = {
    enable = true;
    version = "3.9";
    venv.enable = true;
  };

  # Core packages from Nixpkgs
  packages = with pkgs; [
    # Development tools
    black
    isort
    
    # System packages for matplotlib rendering
    cairo
    pango
    gdk-pixbuf
    fontconfig
  ];

  # Python packages via pip (installed into the venv)
  languages.python.venv.requirements = ''
    # Core application dependencies
    httpx>=0.23.0
    python-dotenv>=0.21.0
    ibmcloudant>=0.2.1

    # Data analysis and visualization
    matplotlib>=3.6.0
    numpy>=1.23.0
    mplcursors>=0.5.0

    # Development and testing
    pytest>=7.1.0
    pytest-asyncio>=0.19.0
    flake8>=5.0.0

    # Jupyter notebook environment
    jupyter>=1.0.0
  '';

  # Environment variables (can be overridden by .env file)
  env = {
    PYTHONPATH = "./";
  };

  # Development scripts and processes
  scripts = {
    test.exec = "pytest";
    format.exec = "black amazing/ && isort amazing/";
    lint.exec = "flake8 amazing/";
    notebook.exec = "jupyter notebook";
  };

  # Git hooks (replaces deprecated pre-commit)
  git-hooks.hooks = {
    black.enable = true;
    isort.enable = true;
    flake8.enable = true;
  };

  # Disable automatic cache management to avoid trust issues
  cachix.enable = false;

  # Automatically load .env file
  dotenv.enable = true;
}