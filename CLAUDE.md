# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal scripts for analyzing the Amazing Marvin task management system. The project uses two access methods:
- **API access** via httpx with full access token
- **Direct DB access** to the CloudAnt CouchDB instance using IBM Cloudant SDK

## Environment Setup

Uses Nix + devenv.sh for reproducible development environment with Python 3.9. Setup steps:

```bash
# Install Nix (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# Install devenv
nix profile add nixpkgs#devenv

# Enter development shell (first time takes ~3 minutes to build)
devenv shell

# Configure credentials
cp .env.example .env
# Edit .env with credentials from https://app.amazingmarvin.com/pre?api
```

Required `.env` variables:
- `CLOUDANT_URL`, `CLOUDANT_SYNC_DB`, `CLOUDANT_USERNAME`, `CLOUDANT_PASSWORD` - CouchDB access
- `FULL_ACCESS_TOKEN` - Marvin API token

## Development Commands

```bash
# Enter development shell
devenv shell

# Run tests
devenv shell test
# Or run specific test (after entering shell)
pytest amazing/test_client.py::test_cloudant_get_all_tasks

# Code formatting
devenv shell format

# Linting
devenv shell lint

# Interactive analysis (Jupyter)
devenv shell notebook
# Then open amazing/stats.ipynb
```

Code quality configured with:
- Black (line length: 140)
- isort (matching Black config)
- flake8 (line length: 140, ignores E203)

## VSCode Integration

Project includes VSCode configuration files:
- `.vscode/settings.json` - Python interpreter path, formatting, basic settings
- `.vscode/extensions.json` - Recommended extensions for Python, Jupyter, Black
- Python interpreter path: `.devenv/state/venv/bin/python` (not `.devenv/profile/default/bin/python`)
- Matplotlib configured for inline rendering in VSCode Jupyter (`%matplotlib inline`)

## Architecture

### Core Module: `amazing/main.py`

**AmazingCloudAntClient** - Main client class for CouchDB access:
- `get_all_tasks()` - Returns all tasks as Task objects
- `get_task_stats(since=None)` - Computes cumulative flow metrics over time
  - Calculates incomplete/complete task counts for each day
  - Accounts for recurring tasks (filters out "ghost" tasks marked done=False with recurring=True)
  - Returns cumulative_flow dict with daily stats plus aggregate metrics
- `get_task_stats_for_chart(since=None)` - Formats stats for matplotlib (returns x/y series)
- `get_tasks_added_removed_between(start, end)` - Returns tasks created/completed in date range

**Task** class - Wrapper around task document with properties:
- `title`, `done`, `is_starred` - Basic task attributes
- `cycle_time` - Time in days between creation and completion

**Timestamp utilities**: `date_to_timestamp()`, `timestamp_to_date()`, `timestamp_to_datefmt()`

### Data Visualization: `amazing/stats.ipynb`

Jupyter notebook with multiple visualizations:
- Stacked area plot: incomplete vs complete tasks over time
- Moving average of daily task completion
- Bar charts: backlog and completed tasks over time
- Task cycle time distribution (histogram with outlier filtering using IQR)
- Weighted histogram by priority (using `isStarred` field)

Uses matplotlib with mplcursors for interactive charts.

### Tests: `amazing/test_client.py`

Pytest tests covering:
- API connectivity (`test_call_amazing_test_endpoint`)
- CloudAnt client methods (server info, DB info, task retrieval, stats)

Tests expect >1500 tasks in the database (see line 24).

## Key Implementation Details

### Recurring Task Filtering

When computing incomplete tasks, the code filters out "ghost" recurring tasks - tasks marked as `done=False` with `recurring=True` (see `main.py:130-131`). These are soft-deleted recurring task instances that shouldn't count toward the backlog.

### Task Statistics Logic

The cumulative flow calculation (`get_task_stats()`) iterates day-by-day from the first task to today:
- **Incomplete count**: Tasks created on/before day AND (not done OR done after that day), excluding ghost recurring tasks
- **Complete count**: Tasks created on/before day AND done on/before that day
- **Avg daily complete**: Cumulative complete / days elapsed

This provides a complete picture of task accumulation and completion velocity over time.
