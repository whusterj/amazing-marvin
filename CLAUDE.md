# CLAUDE.md

## Layout

- `amazing/` — the library and its tests. This is the reviewed, tested code. `main.py` holds the Cloudant client and the task statistics; `stats.ipynb` charts them.
- `agent_scripts/` — ad hoc task-review tooling. **AI-written, not human reviewed, and not tested.** Read `agent_scripts/README.md` before you add or run anything there.

## Task reviews

Use `agent_scripts/weekly_review.py` for a review over a date window. Put a new review script in `agent_scripts/`, not in the repository root, and take shared helpers from `agent_scripts._common`.

Run a script as a module from the repository root, so that `amazing` resolves:

```bash
uv run python -m agent_scripts.weekly_review --start 2026-01-01 --end 2026-01-07
```

## Checks

CI runs black, flake8, isort, and mypy on every push, and pytest against the live API. Run them the same way before you push:

```bash
uv run black --check . && uv run flake8 . && uv run isort --check-only . && uv run mypy
```

The five tests in `amazing/test_client.py` call the live Marvin API and Cloudant. They need credentials in `.env` and they will fail without them.
