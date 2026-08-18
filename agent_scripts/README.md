# agent_scripts

> **Every file in this folder is AI-written and has not been reviewed by a human.** Treat it as a working draft, not as tested code. It reads a live personal database, and `deleted_docs.py` can write to it. Read a script before you run it.

These are ad hoc tools for reviewing tasks in [Amazing Marvin](https://amazingmarvin.com/) through its Cloudant/CouchDB sync database. They exist because a question came up once and a script answered it. The code in `amazing/` is the tested part of this repository; nothing here is covered by the test suite.

## For an agent reading this

This folder is where task-review tooling for this repository lives. Use `weekly_review.py` for a review over a date window, and add a new script here rather than in the repository root. Import shared helpers from `agent_scripts._client`. Run every script as a module from the repository root, so that `amazing` resolves:

```bash
python -m agent_scripts.weekly_review --start 2026-01-01 --end 2026-01-07
```

Prefix that with `uv run` once the project uses uv.

## The scripts

| Script | What it does |
|---|---|
| `weekly_review.py` | Reports tasks completed in a date window, open tasks that slipped, the forward plan, and the unscheduled P1 backlog. |
| `check_connection.py` | Confirms the credentials in `.env` reach the database, and prints a task count. |
| `probe_schema.py` | Reports which fields task documents carry and how often, so a script can learn whether a field is always present. |
| `deleted_docs.py` | Lists deleted documents that CouchDB has not yet compacted, and restores one by id. **This one writes to the database.** |

`_client.py` holds the shared connection. Every script used to carry its own copy of that code.

## Setup

These scripts read the same `.env` as the rest of the repository. See the root `README.md`. They need `CLOUDANT_URL`, `CLOUDANT_USERNAME`, `CLOUDANT_PASSWORD`, and `CLOUDANT_SYNC_DB`.

## Known gaps

- No tests, and no error handling worth the name. A missing environment variable raises `KeyError`.
- `weekly_review.py` treats a task with `done=True` and no `doneAt` as not completed, which matches `amazing/main.py`.
- `deleted_docs.py` reads the `_changes` feed on every call, so listing many documents makes many requests.
