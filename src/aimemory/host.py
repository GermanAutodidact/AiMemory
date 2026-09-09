"""Explicit host capture and non-destructive local plugin installation."""

import hashlib
import json
from importlib.resources import files
from pathlib import Path

from .models import Evidence, MemoryRecord


def capture(payload):
    if not isinstance(payload, dict) or set(payload) != {"content", "source", "created_at"}:
        raise ValueError("capture requires content, source and created_at")
    if not isinstance(payload["content"], str) or len(payload["content"]) > 20000:
        raise ValueError("capture content must be text of at most 20000 characters")
    ident = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return MemoryRecord(
        content=payload["content"],
        id="capture:" + ident,
        created_at=payload["created_at"],
        kind="explicit-memory",
        evidence=[Evidence(payload["content"], payload["source"])],
        metadata={"backend": "opencode", "capture": "explicit"},
    )


def install_plugin(project):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    destination = project / ".opencode" / "plugins" / "aimemory.js"
    content = files("aimemory").joinpath("opencode/aimemory.js").read_text(encoding="utf-8")
    if destination.exists():
        if destination.read_text(encoding="utf-8") == content:
            return {"path": str(destination), "status": "already installed"}
        raise ValueError("existing plugin differs; preserve it and review before replacing")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(content)
    return {"path": str(destination), "status": "installed; restart OpenCode"}
