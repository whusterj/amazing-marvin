"""Check that the credentials in .env reach the database.

Two small requests, so a bad credential fails fast. Use probe_schema.py when
the question is about the task documents themselves; this one deliberately
does not read them.

Example:
    uv run python -m agent_scripts.check_connection
"""

import argparse

from agent_scripts._common import db_name, get_client


def main() -> None:
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    client = get_client()

    server = client.server_information()
    print(f"server: {server.get('couchdb')} (version {server.get('version')})")

    database = client.get_db_info()
    print(f"database {db_name()}: {database.get('doc_count')} documents, {database.get('doc_del_count')} deleted")


if __name__ == "__main__":
    main()
