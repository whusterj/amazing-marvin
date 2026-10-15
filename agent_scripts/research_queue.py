"""List open research-link tasks, and mark processed ones done.

The weekly tn-research link aggregation reads tasks whose title starts with a
prefix such as "Read:" or "Save:", folds the relevant links into notes, and
then closes the tasks it used.

This is the only script in agent_scripts that writes. It writes in one way: it
marks a task done through the Marvin API's /markDone endpoint, the same path
the Marvin app uses, so Marvin sets doneAt, fieldUpdates, and any reward
itself. It never edits a Cloudant document directly. Before it writes, it
re-reads each ID and refuses any task that is missing, already done, or does
not carry a research prefix.

Examples:
    uv run python -m agent_scripts.research_queue list
    uv run python -m agent_scripts.research_queue list --json
    uv run python -m agent_scripts.research_queue done ID [ID ...] --dry-run
    uv run python -m agent_scripts.research_queue done ID [ID ...]
"""

import argparse
import json
import os
import re
import sys
import time

import httpx

from agent_scripts._common import get_client, star
from amazing.main import API_BASE, Task

# "Review:" is left out on purpose. Those tasks ask William to review a PR
# that the aggregation opened; they are not links to aggregate.
DEFAULT_PREFIXES = ["Save", "Read", "Watch", "Listen", "Research"]


def prefix_pattern(prefixes: list[str]) -> re.Pattern[str]:
    alternatives = "|".join(re.escape(p) for p in prefixes)
    return re.compile(rf"^\s*({alternatives})\s*:", re.IGNORECASE)


def is_research(task: Task, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.match(task.title or ""))


def open_research_tasks(pattern: re.Pattern[str]) -> list[Task]:
    tasks = get_client().get_all_tasks()
    return [t for t in tasks if not t.done and not t.data["doc"].get("recurring", False) and is_research(t, pattern)]


def cmd_list(args: argparse.Namespace) -> None:
    tasks = open_research_tasks(prefix_pattern(args.prefix))
    rows = [
        {
            "id": t.data["doc"]["_id"],
            "priority": star(t.data["doc"]),
            "title": t.title,
            "note": (t.data["doc"].get("note") or "").strip(),
        }
        for t in tasks
    ]
    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        print()
        return
    for row in rows:
        print(f"{row['id']}  {row['priority']}  {row['title']}")
        if row["note"]:
            for line in row["note"].splitlines():
                print(f"    {line}")
    print(f"(count: {len(rows)})")


def mark_done(item_id: str) -> httpx.Response:
    # Marvin wants the offset in minutes, with the sign JavaScript's
    # getTimezoneOffset() uses: positive west of UTC.
    offset_minutes = (time.altzone if time.localtime().tm_isdst > 0 else time.timezone) // 60
    return httpx.post(
        f"{API_BASE}/markDone",
        headers={"X-API-Token": os.environ["API_TOKEN"]},
        json={"itemId": item_id, "timeZoneOffset": offset_minutes},
        timeout=30,
    )


def cmd_done(args: argparse.Namespace) -> None:
    pattern = prefix_pattern(args.prefix)
    by_id = {t.data["doc"]["_id"]: t for t in get_client().get_all_tasks()}

    refused = []
    for item_id in args.ids:
        task = by_id.get(item_id)
        if task is None:
            refused.append(f"{item_id}: no such task")
        elif task.done:
            refused.append(f"{item_id}: already done ({task.title})")
        elif not is_research(task, pattern):
            refused.append(f"{item_id}: not a research task ({task.title})")
    if refused:
        print("Refusing to write; nothing was marked done:", file=sys.stderr)
        for line in refused:
            print(f"  {line}", file=sys.stderr)
        sys.exit(2)

    failed = 0
    for item_id in args.ids:
        title = by_id[item_id].title
        if args.dry_run:
            print(f"would mark done: {item_id}  {title}")
            continue
        response = mark_done(item_id)
        if response.is_success:
            print(f"marked done: {item_id}  {title}")
        else:
            failed += 1
            print(f"FAILED ({response.status_code}): {item_id}  {title}  {response.text[:200]}", file=sys.stderr)
    if failed:
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--prefix",
        nargs="+",
        default=DEFAULT_PREFIXES,
        help=f"Title prefixes that mark a research task. Default: {' '.join(DEFAULT_PREFIXES)}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="Print open research tasks with their IDs and notes. Read-only.")
    list_parser.add_argument("--json", action="store_true", help="Print JSON instead of text")
    list_parser.set_defaults(func=cmd_list)

    done_parser = sub.add_parser("done", help="Mark the given research tasks done through the Marvin API.")
    done_parser.add_argument("ids", nargs="+", help="Task _id values, as printed by list")
    done_parser.add_argument("--dry-run", action="store_true", help="Check the IDs and print what would change, without writing")
    done_parser.set_defaults(func=cmd_done)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
