"""Check that the Cloudant credentials in .env work, and show a few tasks.

Example:
    python -m agent_scripts.check_connection
"""

import argparse

from agent_scripts._client import get_client


def main() -> None:
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    client = get_client()
    info = client.server_information()
    print(f"server: {info.get('couchdb')} (version {info.get('version')})")

    tasks = client.get_all_tasks()
    done = sum(1 for t in tasks if t.done)
    print(f"tasks: {len(tasks)} total, {done} done, {len(tasks) - done} open")

    print("\nfirst five by title:")
    for task in sorted(tasks, key=lambda t: t.title)[:5]:
        print(f"  {task.title[:100]}")


if __name__ == "__main__":
    main()
