"""List deleted Marvin documents, and restore one while its history survives.

CouchDB keeps a deleted document as a tombstone. A tombstone written by Marvin
carries only _id, _rev, db, and _deleted, so it holds no title and no content.
Recovery therefore depends on an earlier revision still being readable, and
Cloudant compacts those away. On this database every existing tombstone has
already lost its history, so --restore is useful only for a document you delete
by mistake and come back for before the next compaction.

Ask for revs_info at the tombstone revision. Without an explicit rev, CouchDB
tries to serve the current version, which is deleted, and answers 404.

Examples:
    uv run python -m agent_scripts.deleted_docs --type Categories
    uv run python -m agent_scripts.deleted_docs --restore <document-id>
"""

import argparse

from ibm_cloud_sdk_core.api_exception import ApiException
from ibmcloudant.cloudant_v1 import CloudantV1

from agent_scripts._common import db_name, get_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--type", dest="doc_type", help="Only report documents whose db field equals this, such as Categories or Tasks")
    parser.add_argument("--restore", metavar="DOC_ID", help="Restore this document from its previous revision")
    return parser.parse_args()


def find_tombstones(service: CloudantV1, db: str, doc_type: str | None = None) -> list[dict]:
    """Return the deleted documents from the _changes feed."""
    response = service.post_changes(
        db=db,
        include_docs=True,
        filter="_selector",
        selector={"_deleted": {"$eq": True}},
    ).get_result()

    results = response.get("results", [])
    if doc_type is None:
        return results
    return [r for r in results if r.get("doc", {}).get("db") == doc_type]


def previous_revision(service: CloudantV1, db: str, doc_id: str, tombstone_rev: str) -> dict | None:
    """Return the last readable revision before the delete, or None if it is gone.

    Compaction removes the body of an earlier revision and empties _revs_info,
    so expect None for any document deleted more than a short while ago.
    """
    try:
        rev_info = service.get_document(db=db, doc_id=doc_id, rev=tombstone_rev, revs_info=True).get_result()
    except ApiException as error:
        if error.code == 404:
            return None
        raise

    for rev in rev_info.get("_revs_info", []):
        if rev["status"] == "available" and rev["rev"] != tombstone_rev:
            try:
                return service.get_document(db=db, doc_id=doc_id, rev=rev["rev"]).get_result()
            except ApiException as error:
                if error.code == 404:
                    return None
                raise
    return None


def restore(service: CloudantV1, db: str, doc_id: str) -> None:
    """Write a document's previous revision back, which undoes the delete."""
    tombstones = {r["id"]: r for r in find_tombstones(service, db)}
    if doc_id not in tombstones:
        print(f"{doc_id} is not among the deleted documents.")
        return

    tombstone_rev = tombstones[doc_id]["doc"]["_rev"]
    old_doc = previous_revision(service, db, doc_id, tombstone_rev)
    if old_doc is None:
        print(f"{doc_id} has no readable earlier revision, so its content is gone and it cannot be restored.")
        return

    # Write onto the tombstone revision, so CouchDB accepts this as the next revision.
    document = {k: v for k, v in old_doc.items() if k != "_rev"}
    document["_rev"] = tombstone_rev
    result = service.put_document(db=db, doc_id=doc_id, document=document).get_result()
    print(f"restored {old_doc.get('title', '(no title)')!r} as revision {result.get('rev')}")


def main() -> None:
    args = parse_args()
    service = get_service()
    db = db_name()

    if args.restore:
        restore(service, db, args.restore)
        return

    tombstones = find_tombstones(service, db, args.doc_type)
    label = args.doc_type or "any type"
    print(f"{len(tombstones)} deleted document(s) of {label}\n")

    recoverable = 0
    for entry in tombstones:
        doc_id = entry["id"]
        old_doc = previous_revision(service, db, doc_id, entry["doc"]["_rev"])
        if old_doc is None:
            print(f"  {doc_id}  {entry['doc'].get('db', '?')}  (history gone, cannot restore)")
            continue
        recoverable += 1
        print(f"  {doc_id}  {old_doc.get('db', '?')}  {old_doc.get('title', '(no title)')!r}")

    print(f"\n{recoverable} of {len(tombstones)} still hold a readable earlier revision.")
    if tombstones and not recoverable:
        print("Compaction has removed every earlier revision, so none of these can be restored.")


if __name__ == "__main__":
    main()
