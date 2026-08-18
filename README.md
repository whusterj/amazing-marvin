# Amazing Marvin API Scripts

My personal scripts for the Amazing Marvin task management system. Will use the [Marvin API](https://github.com/amazingmarvin/MarvinAPI/wiki/Marvin-API) or [direct access to the CloudAnt CouchDB](https://github.com/amazingmarvin/MarvinAPI/wiki/Database-Access) instance as necessary.

- API access with [httpx](https://github.com/projectdiscovery/httpx)
- DB access with [cloudant-python-sdk](https://github.com/IBM/cloudant-python-sdk) ([docs](https://ibm.github.io/cloudant-python-sdk/docs/latest/))

## TODOS

- Visualize task throughput with plotting lib or export to GSheets, etc.
- [DONE] Compute task throughput - tasks created v. finished over time

## SETUP

The project uses [uv](https://docs.astral.sh/uv/). Install it once, then let it do the rest:

```bash
uv sync
```

That reads `pyproject.toml`, installs the exact versions in `uv.lock`, and fetches Python 3.12 if you do not have it. There is no virtual environment to activate. Put `uv run` in front of a command to run it in the project environment:

```bash
uv run pytest
uv run jupyter notebook amazing/stats.ipynb
```

Copy the `.env.example` file:

```bash
cp .env.example .env
```

Get Amazing Marvin credentials from [here](https://app.amazingmarvin.com/pre?api), and plug them into the `.env` file.

To add a package, use `uv add <package>`. To add a development tool, use `uv add --dev <package>`. Both write `pyproject.toml` and `uv.lock` together, so commit the two files as one change.
