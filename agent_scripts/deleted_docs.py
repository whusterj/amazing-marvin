"""List deleted Marvin documents, and restore one by id.

CouchDB keeps a deleted document as a tombstone until compaction, so the
previous revision is often still readable. This lists what can be recovered,
and restores a chosen document by writing its previous revision back.

Examples:
    python -m agent_scripts.deleted_docs --type Categories
    python -m agent_scripts.deleted_docs --restore <document-id>
"""

import argparse

from agent_scripts._client import db_name, get_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--type", dest="doc_type", help="Only report documents whose db field equals this, such as Categories or Tasks")
    parser.add_argument("--restore", metavar="DOC_ID", help="Restore this document from its previous revision")
    return parser.parse_args()


def find_tombstones(doc_type: str | None) -> list[dict]:
    """Return the deleted documents from the _changes feed."""
    service = get_service()
    response = service.post_changes(
        db=db_name(),
        include_docs=True,
        filter="_selector",
        selector={"_deleted": {"$eq": True}},
    ).get_result()

    results = response.get("results", [])
    if doc_type is None:
        return results
    return [r for r in results if r.get("doc", {}).get("db") == doc_type]


def previous_revision(doc_id: str, tombstone_rev: str) -> dict | None:
    """Return the last readable revision of a document before it was deleted."""
    service = get_service()
    rev_info = service.get_document(db=db_name(), doc_id=doc_id, revs_info=True, latest=True).get_result()

    for rev in rev_info.get("_revs_info", []):
        if rev["status"] == "available" and rev["rev"] != tombstone_rev:
            return service.get_document(db=db_name(), doc_id=doc_id, rev=rev["rev"]).get_result()
    return None


def restore(doc_id: str) -> None:
    """Write a document's previous revision back, which undoes the delete."""
    service = get_service()
    tombstones = {r["id"]: r for r in find_tombstones(None)}
    if doc_id not in tombstones:
        print(f"{doc_id} is not among the deleted documents.")
        return

    old_doc = previous_revision(doc_id, tombstones[doc_id]["doc"]["_rev"])
    if old_doc is None:
        print(f"{doc_id} has no readable previous revision. The database compacted it.")
        return

    # Write onto the tombstone revision, so CouchDB accepts this as the next revision.
    document = {k: v for k, v in old_doc.items() if k != "_rev"}
    document["_rev"] = tombstones[doc_id]["doc"]["_rev"]
    result = service.put_document(db=db_name(), doc_id=doc_id, document=document).get_result()
    print(f"restored {old_doc.get('title', '(no title)')!r} as revision {result.get('rev')}")


def main() -> None:
    args = parse_args()
    if args.restore:
        restore(args.restore)
        return

    tombstones = find_tombstones(args.doc_type)
    label = args.doc_type or "any type"
    print(f"{len(tombstones)} deleted document(s) of {label}\n")

    for entry in tombstones:
        doc_id = entry["id"]
        old_doc = previous_revision(doc_id, entry["doc"]["_rev"])
        if old_doc is None:
            print(f"  {doc_id}  (compacted, cannot recover)")
            continue
        print(f"  {doc_id}  {old_doc.get('db', '?')}  {old_doc.get('title', '(no title)')!r}")


if __name__ == "__main__":
    main()
