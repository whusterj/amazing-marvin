# agent_scripts

> **Every file in this folder is AI-written and has not been reviewed by a human.** Treat it as a working draft, not as tested code. Every script reads a live personal database, and none of them writes to it. Read a script before you run it.

These are ad hoc tools for reviewing tasks in [Amazing Marvin](https://amazingmarvin.com/) through its Cloudant/CouchDB sync database. They exist because a question came up once and a script answered it. The code in `amazing/` is the tested part of this repository; nothing here is covered by the test suite.

## For an agent reading this

This folder is where task-review tooling for this repository lives. Use `weekly_review.py` for a review over a date window, and add a new script here rather than in the repository root. Import shared helpers from `agent_scripts._common`. Run every script as a module from the repository root, so that `amazing` resolves:

```bash
uv run python -m agent_scripts.weekly_review --start 2026-01-01 --end 2026-01-07
```

## The scripts

| Script | What it does |
|---|---|
| `weekly_review.py` | Reports tasks completed in a date window, open tasks that slipped, the forward plan, and the unscheduled P1 backlog. |
| `check_connection.py` | Confirms the credentials in `.env` reach the database. Two requests, so it fails fast; it reads no tasks. |
| `probe_schema.py` | Reports which fields task documents carry and how often, so a script can learn whether a field is always present. |

`_common.py` holds the shared connection and the priority and date formatting. Every script used to carry its own copy of that code.

## Setup

These scripts read the same `.env` as the rest of the repository. See the root `README.md`. They need `CLOUDANT_URL`, `CLOUDANT_USERNAME`, `CLOUDANT_PASSWORD`, and `CLOUDANT_SYNC_DB`.

## Known gaps

- No tests, and no error handling worth the name. A missing environment variable raises `KeyError`.
- `weekly_review.py` treats a task with `done=True` and no `doneAt` as not completed, which matches `amazing/main.py`.

## Do not build a delete-recovery tool

A script for recovering a deleted Marvin document existed here and was removed, because the job cannot be done. Three facts, measured against the live database in August 2026:

- A tombstone written by Marvin carries only `_id`, `_rev`, `db`, and `_deleted`. It holds no title and no content.
- Cloudant compacts earlier revisions away. `_revs_info` comes back empty for every tombstone, so no earlier revision can be read. **0 of 37 deleted Categories were recoverable.** Their revision generations ran from 2 to 600, so the history was long and all of it is gone.
- `revs_info` also has to be asked for at an explicit `rev`. Without one, CouchDB tries to serve the current version of a deleted document and answers 404. A tool that gets this wrong reports "no previous revision" for everything and looks like it works.

Recovery would have to come from a Marvin export or a backup, not from CouchDB.
