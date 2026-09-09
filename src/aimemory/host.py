"""Explicit host capture and non-destructive local plugin installation."""

import hashlib
import json
from importlib.resources import files
from pathlib import Path

from .models import Evidence, MemoryRecord


def capture(payload):
    if not isinstance(payload, dict) or set(payload) != {"content", "source", "created_at"}:
        raise ValueError("capture requires content, source and created_at")
    if (
        not isinstance(payload["content"], str)
        or not payload["content"].strip()
        or len(payload["content"]) > 20000
    ):
        raise ValueError("capture content must be non-empty text of at most 20000 characters")
    ident = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return MemoryRecord(
        content=payload["content"],
        id="capture:" + ident,
        created_at=payload["created_at"],
        kind="explicit-memory",
        evidence=[Evidence(payload["content"], payload["source"])],
        metadata={"backend": "opencode", "capture": "explicit"},
    )


def install_plugin(project=None, *, global_install=False, update=False):
    if global_install:
        if project is not None:
            raise ValueError("global installation does not accept a project")
        destination = Path.home() / ".config" / "opencode" / "plugins" / "aimemory.js"
    else:
        if project is None:
            raise ValueError("project is required unless --global is selected")
        project = Path(project).resolve(strict=True)
        if not project.is_dir():
            raise ValueError("project must be an existing directory")
        destination = project / ".opencode" / "plugins" / "aimemory.js"
    content = files("aimemory").joinpath("opencode/aimemory.js").read_text(encoding="utf-8")
    if destination.exists():
        if destination.read_text(encoding="utf-8") == content:
            return {"path": str(destination), "status": "already installed"}
        if not update or not destination.read_text(encoding="utf-8").startswith(
            "// AiMemory managed OpenCode plugin"
        ):
            raise ValueError("existing plugin differs; preserve it and review before replacing")
        destination.write_text(content, encoding="utf-8")
        return {"path": str(destination), "status": "managed plugin updated; restart OpenCode"}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(content)
    return {"path": str(destination), "status": "installed; restart OpenCode"}
