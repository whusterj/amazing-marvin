# Amazing Marvin API Scripts

My personal scripts for the Amazing Marvin task management system. Will use the Marvin API or direct access to the CloudAnt CouchDB instance as necessary.

- API access with [httpx](https://github.com/projectdiscovery/httpx)
- DB access with [cloudant-python-sdk](https://github.com/IBM/cloudant-python-sdk)

## TODOS

- Visualize task throughput - tasks created v. finished over time

## SETUP

The scripts were developed using **Python 3.9.7**. The requirements may not work with other Python versions.

Create a local virtual environment (venv):

```bash
python -m venv /venv
```

Activate the environment and install requirements from `requirements.txt`:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the `.env.example` file:

```bash
cp .env.example .env
```

Get Amazing Marvin credentials from [here](https://app.amazingmarvin.com/pre?api), and plug them into the `.env` file.
