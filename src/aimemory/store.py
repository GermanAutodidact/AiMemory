"""Minimal local JSONL store.

This backend is intentionally boring: it makes the record format testable before
adapters for open-mem, true-mem, or a database are introduced.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from .models import MemoryRecord


class JsonlMemoryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, record: MemoryRecord) -> None:
        payload = json.dumps(record.to_dict(), ensure_ascii=False, allow_nan=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    def all(self) -> Iterator[MemoryRecord]:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw = json.loads(line)
                yield MemoryRecord.from_dict(raw)
