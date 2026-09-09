"""Transactional store using the existing public MemoryRecord format."""

import json
import sqlite3
from pathlib import Path

from .models import MemoryRecord


class SQLiteMemoryStore:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS records (namespace TEXT, id TEXT, payload TEXT NOT NULL, PRIMARY KEY(namespace,id))"
        )
        self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.db.close()

    def import_records(self, namespace, records):
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError("namespace must be nonempty")
        records = list(records)
        if len(records) > 10000:
            raise ValueError("maximum 10000 records per import")
        payloads = [
            json.dumps(r.to_dict(), ensure_ascii=False, sort_keys=True, allow_nan=False)
            for r in records
        ]
        count = 0
        with self.db:
            for record, payload in zip(records, payloads):
                row = self.db.execute(
                    "SELECT payload FROM records WHERE namespace=? AND id=?", (namespace, record.id)
                ).fetchone()
                if row:
                    if row[0] != payload:
                        raise ValueError("ID collision: " + record.id)
                    continue
                self.db.execute(
                    "INSERT INTO records VALUES (?,?,?)", (namespace, record.id, payload)
                )
                count += 1
        return count

    def search(self, namespace, query=""):
        rows = self.db.execute(
            "SELECT payload FROM records WHERE namespace=? ORDER BY rowid", (namespace,)
        )
        return [
            r
            for row in rows
            if query.casefold()
            in (r := MemoryRecord.from_dict(json.loads(row[0]))).content.casefold()
        ]

    def context(self, namespace, max_chars=6000):
        if max_chars < 0:
            raise ValueError("max_chars must be nonnegative")
        result = []
        size = 0
        for record in self.search(namespace):
            if record.metadata.get("inactive"):
                continue
            line = json.dumps(record.to_dict(), ensure_ascii=False)
            cost = len(line) + bool(result)
            if size + cost <= max_chars:
                result.append(line)
                size += cost
        return "\n".join(result)

    def conflicts(self, namespace):
        groups = {}
        for r in self.search(namespace):
            key = r.metadata.get("key")
            if isinstance(key, str) and key and not r.metadata.get("inactive"):
                groups.setdefault(key, []).append(r)
        return {
            k: [r.to_dict() for r in rows]
            for k, rows in groups.items()
            if len({r.content.strip().casefold() for r in rows}) > 1
        }
