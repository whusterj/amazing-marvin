"""Report which fields Marvin task documents carry, and print one sample.

Useful when a script must know whether a field is always present. It answers,
for example, whether a task marked done always carries doneAt.

Example:
    python -m agent_scripts.probe_schema --state done
"""

import argparse
import json

from agent_scripts._client import get_client

SKIP_FIELDS = ("note",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--state", choices=("done", "open", "all"), default="all", help="Which tasks to inspect")
    parser.add_argument("--sample", action="store_true", help="Print one whole document, minus its note")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = get_client().get_all_tasks()

    if args.state == "done":
        tasks = [t for t in tasks if t.done]
    elif args.state == "open":
        tasks = [t for t in tasks if not t.done]

    print(f"{len(tasks)} task(s) in state {args.state!r}\n")
    if not tasks:
        return

    counts: dict[str, int] = {}
    for task in tasks:
        for field in task.data["doc"]:
            counts[field] = counts.get(field, 0) + 1

    print(f"{'field':<24} {'present':>8} {'of':>8}  always?")
    for field, count in sorted(counts.items(), key=lambda pair: -pair[1]):
        always = "yes" if count == len(tasks) else "NO"
        print(f"{field:<24} {count:>8} {len(tasks):>8}  {always}")

    if args.sample:
        doc = {k: v for k, v in tasks[-1].data["doc"].items() if k not in SKIP_FIELDS}
        print("\nsample document:")
        print(json.dumps(doc, indent=1)[:1500])


if __name__ == "__main__":
    main()
