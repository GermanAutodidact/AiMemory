"""Explicit snapshot adapters. Source stores are never modified."""

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .models import Evidence, MemoryRecord


def stable_id(backend, namespace, source_id, payload):
    data = json.dumps([backend, namespace, source_id, payload], sort_keys=True, ensure_ascii=False)
    return backend + ":" + hashlib.sha256(data.encode()).hexdigest()


def open_mem(text, namespace):
    # Upstream mem-export returns a human-readable count before the JSON object.
    if text.startswith("Exported "):
        text = text.split("\n\n", 1)[1]
    data = json.loads(text)
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("expected open-mem export version 1")
    if not isinstance(data.get("project"), str):
        raise TypeError("open-mem project missing")
    result = []
    for collection in ("observations", "summaries"):
        items = data.get(collection)
        if not isinstance(items, list):
            raise TypeError(collection + " must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise TypeError("invalid open-mem record")
            content = item["narrative"] if collection == "observations" else item["summary"]
            source = "open-mem:" + data["project"] + ":" + str(item["id"])
            result.append(
                MemoryRecord(
                    id=stable_id("open-mem", namespace, item["id"], item),
                    content=content,
                    kind=item.get("type", "summary"),
                    created_at=item["createdAt"],
                    tags=item.get("concepts", []),
                    evidence=[Evidence(claim=content, source=source)],
                    metadata={
                        "backend": "open-mem",
                        "project": data["project"],
                        "original": item,
                        "inactive": bool(item.get("deletedAt") or item.get("supersededBy")),
                    },
                )
            )
    return result


def true_mem(path, namespace, project=None, global_only=False):
    if (project is None) == (not global_only):
        raise ValueError("select exactly one project or global_only")
    path = Path(path).resolve(strict=True)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        db.row_factory = sqlite3.Row
        columns = {r[1] for r in db.execute("PRAGMA table_info(memory_units)")}
        needed = {
            "id",
            "summary",
            "classification",
            "project_scope",
            "created_at",
            "source_event_ids",
            "confidence",
            "status",
        }
        if not needed <= columns:
            raise ValueError(
                "unsupported true-mem schema: missing " + str(sorted(needed - columns))
            )
        condition, args = (
            ("project_scope IS NULL", ()) if global_only else ("project_scope=?", (project,))
        )
        rows = db.execute(
            "SELECT * FROM memory_units WHERE status='active' AND " + condition, args
        ).fetchmany(10001)
        if len(rows) > 10000:
            raise ValueError("maximum 10000 memories per snapshot")
        result = []
        for row in rows:
            source = "true-mem:" + str(row["id"])
            events = json.loads(row["source_event_ids"])
            if not isinstance(events, list) or any(not isinstance(e, str) for e in events):
                raise ValueError("invalid true-mem source_event_ids")
            original = {k: row[k] for k in needed}
            result.append(
                MemoryRecord(
                    id=stable_id("true-mem", namespace, row["id"], original),
                    content=row["summary"],
                    kind=row["classification"],
                    created_at=row["created_at"],
                    evidence=[
                        Evidence(claim=row["summary"], source=source, confidence=row["confidence"])
                    ],
                    metadata={
                        "backend": "true-mem",
                        "source_event_ids": events,
                        "project": row["project_scope"],
                        "original": original,
                    },
                )
            )
        return result
