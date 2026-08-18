"""Print a weekly review of Amazing Marvin tasks for a date window.

Replaces three earlier scripts that each hardcoded their own dates. The window
and the forward horizon are arguments now.

Example:
    python -m agent_scripts.weekly_review --start 2026-01-01 --end 2026-01-07
"""

import argparse
from collections.abc import Callable, Sequence

from agent_scripts._common import get_client, star, to_day


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", required=True, help="First day of the review window, as YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Last day of the review window, as YYYY-MM-DD")
    parser.add_argument("--slip-from", help="Earliest day to report as slipped. Defaults to --start.")
    parser.add_argument("--plan-through", help="Last day of the forward plan. Omit to report every future day.")
    parser.add_argument("--match", nargs="*", default=[], help="Only report open tasks whose title holds one of these words")
    return parser.parse_args()


def scheduled_rows(tasks: Sequence, keep: Callable[[str], bool]) -> list[tuple[str, str, str]]:
    """Rows of (scheduled day, priority, title) for tasks whose day keep() accepts."""
    rows = []
    for task in tasks:
        doc = task.data["doc"]
        day = doc.get("day")
        if day and keep(day):
            rows.append((day, star(doc), task.title))
    return rows


def section(title: str, rows: Sequence[tuple[str, ...]]) -> None:
    print(f"\n=== {title} ===")
    for row in sorted(rows):
        print("  " + "  ".join(row))
    print(f"  (count: {len(rows)})")


def main() -> None:
    args = parse_args()
    slip_from = args.slip_from or args.start

    tasks = get_client().get_all_tasks()
    # Every recurring task is left out, not only the ones with no completion time.
    # A review asks what work is outstanding, and a repeating chore is not a
    # backlog item. amazing.main.is_ghost_recurring() draws the narrower line the
    # cumulative chart needs, which is a different question.
    open_tasks = [t for t in tasks if not t.done and not t.data["doc"].get("recurring", False)]

    if args.match:
        words = [w.lower() for w in args.match]
        open_tasks = [t for t in open_tasks if any(w in t.title.lower() for w in words)]

    completed = []
    for task in tasks:
        doc = task.data["doc"]
        if not task.done:
            continue
        day = to_day(doc.get("doneAt"))
        if day and args.start <= day <= args.end:
            completed.append((day, star(doc), "(rec)" if doc.get("recurring") else "     ", task.title))
    section(f"COMPLETED {args.start} .. {args.end}", completed)
    print(f"  (non-recurring: {sum(1 for row in completed if row[2].strip() == '')})")

    slipped = scheduled_rows(open_tasks, lambda day: slip_from <= day <= args.end)
    section(f"OPEN, scheduled {slip_from} .. {args.end} (slipping)", slipped)

    planned = scheduled_rows(open_tasks, lambda day: day > args.end and (args.plan_through is None or day <= args.plan_through))
    section("OPEN, scheduled after the window (the plan)", planned)

    unscheduled_p1 = [
        (star(task.data["doc"]), task.title)
        for task in open_tasks
        if task.data["doc"].get("isStarred") == 3 and not task.data["doc"].get("day")
    ]
    section("UNSCHEDULED P1 backlog", unscheduled_p1)

    print(f"\nTotal open, non-recurring: {len(open_tasks)}")


if __name__ == "__main__":
    main()
