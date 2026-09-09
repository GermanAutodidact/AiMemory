"""Typed records shared by memory, research, and cross-check roles."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class VerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    SUPPORTED = "supported"
    DISPUTED = "disputed"
    REJECTED = "rejected"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class Evidence:
    claim: str
    source: str
    excerpt: str | None = None
    confidence: float = 0.5
    status: VerificationStatus = VerificationStatus.UNVERIFIED

    def __post_init__(self) -> None:
        for value in (self.claim, self.source):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("claim and source must be nonempty strings")
        if (
            isinstance(self.confidence, bool)
            or not isinstance(self.confidence, (int, float))
            or not math.isfinite(self.confidence)
            or not 0.0 <= self.confidence <= 1.0
        ):
            raise ValueError("confidence must be between 0.0 and 1.0")
        self.status = VerificationStatus(self.status)
        if self.excerpt is not None and not isinstance(self.excerpt, str):
            raise ValueError("excerpt must be text")


@dataclass(slots=True)
class MemoryRecord:
    content: str
    kind: str = "note"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    tags: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("id", "content", "kind", "created_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(name + " must be nonempty text")
        if datetime.fromisoformat(self.created_at).tzinfo is None:
            raise ValueError("created_at must include timezone")
        if not isinstance(self.tags, list) or any(not isinstance(t, str) for t in self.tags):
            raise ValueError("tags must be a list of strings")
        if not isinstance(self.evidence, list) or any(
            not isinstance(e, Evidence) for e in self.evidence
        ):
            raise ValueError("evidence must contain Evidence records")
        for item in self.evidence:
            item.__post_init__()
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be an object")
        json.dumps(self.metadata, allow_nan=False)

    @classmethod
    def from_dict(cls, raw: dict) -> MemoryRecord:
        if not isinstance(raw, dict):
            raise TypeError("record must be an object")
        values = dict(raw)
        values["evidence"] = [Evidence(**e) for e in values.get("evidence", [])]
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        self.__post_init__()
        return asdict(self)
