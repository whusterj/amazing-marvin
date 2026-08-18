# CLAUDE.md

## Layout

- `amazing/` — the library and its tests. This is the reviewed, tested code. `main.py` holds the Cloudant client and the task statistics; `stats.ipynb` charts them.
- `agent_scripts/` — ad hoc task-review tooling. **AI-written, not human reviewed, and not tested.** Read `agent_scripts/README.md` before you add or run anything there.

## Task reviews

**Three scripts already cover this work. Reuse one before you write anything.** Run any of them with `--help` for its full options.

| Need | Command |
|---|---|
| Review a date window | `uv run python -m agent_scripts.weekly_review --start YYYY-MM-DD --end YYYY-MM-DD` |
| Narrow that review to a topic | add `--match word word` |
| Widen the slip window or the forward plan | add `--slip-from YYYY-MM-DD` or `--plan-through YYYY-MM-DD` |
| Confirm the credentials reach the database | `uv run python -m agent_scripts.check_connection` |
| Learn whether a task field is always set | `uv run python -m agent_scripts.probe_schema --state done` |

Four rules:

- Run every script as a module from the repository root, or `amazing` will not resolve.
- Add an option to one of the three before you add a file. A new script needs a job none of them does.
- Take the connection and the formatting from `agent_scripts._common`. Never rebuild the Cloudant client.
- Do not write a tool to recover a deleted document. `agent_scripts/README.md` records why that cannot work.

## Checks

CI runs ruff and mypy on every push, and pytest against the live API. Run them the same way before you push:

```bash
uv run ruff format --check . && uv run ruff check . && uv run mypy
```

ruff reads `stats.ipynb` as well as the `.py` files, which black and flake8 did not.

The five tests in `amazing/test_client.py` call the live Marvin API and Cloudant. They need credentials in `.env` and they will fail without them.
