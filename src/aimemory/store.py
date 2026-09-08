"""Minimal local JSONL store.

This backend is intentionally boring: it makes the record format testable before
adapters for open-mem, true-mem, or a database are introduced.
"""

from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Iterator

from .models import Evidence, MemoryRecord, VerificationStatus


class JsonlMemoryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, record: MemoryRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    def all(self) -> Iterator[MemoryRecord]:
        if not self.path.exists():
            return
        allowed = {item.name for item in fields(MemoryRecord)}
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw = json.loads(line)
                raw["evidence"] = [
                    Evidence(
                        claim=item["claim"],
                        source=item["source"],
                        excerpt=item.get("excerpt"),
                        confidence=item.get("confidence", 0.5),
                        status=VerificationStatus(item.get("status", "unverified")),
                    )
                    for item in raw.get("evidence", [])
                ]
                yield MemoryRecord(**{key: value for key, value in raw.items() if key in allowed})
