import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from .adapters import open_mem, true_mem
from .database import SQLiteMemoryStore
from .host import capture, install_plugin
from .models import Evidence, MemoryRecord
from .store import JsonlMemoryStore


def main(argv=None):
    p = argparse.ArgumentParser(description="AiMemory: local memory and explicit backend snapshots")
    p.add_argument(
        "--db",
        default=str(
            Path(
                os.environ.get(
                    "AIMEMORY_DB",
                    str(
                        Path(os.environ.get("AIMEMORY_DATA_DIR", str(Path.home() / ".aimemory")))
                        / "memory.sqlite3"
                    ),
                )
            )
        ),
    )
    p.add_argument("--namespace", default="default")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("capture", help="Read one explicit host memory from JSON stdin")
    install = sub.add_parser("install-opencode", help="Install plugin without changing host config")
    install.add_argument("project", nargs="?")
    install.add_argument("--api", choices=["v1", "v2"], default="v1")
    install.add_argument("--global", dest="global_install", action="store_true")
    install.add_argument(
        "--update", action="store_true", help="Update only an AiMemory-managed file"
    )
    add = sub.add_parser("add")
    add.add_argument("content")
    add.add_argument("--key")
    add.add_argument("--source")
    search = sub.add_parser("search")
    search.add_argument("query", nargs="?", default="")
    sub.add_parser("conflicts")
    sub.add_parser("doctor")
    sub.add_parser("export")
    context = sub.add_parser("context")
    context.add_argument("--max-chars", type=int, default=6000)
    imp = sub.add_parser("import")
    imp.add_argument("file")
    imp.add_argument(
        "--format", choices=["aimemory", "jsonl", "open-mem", "true-mem"], default="aimemory"
    )
    scopes = imp.add_mutually_exclusive_group()
    scopes.add_argument("--project")
    scopes.add_argument("--global-only", action="store_true")
    args = p.parse_args(argv)
    try:
        if args.command == "install-opencode":
            print(
                json.dumps(
                    install_plugin(
                        args.project,
                        global_install=args.global_install,
                        update=args.update,
                        api=args.api,
                    )
                )
            )
            return 0
        with SQLiteMemoryStore(args.db) as db:
            if args.command == "capture":
                text = sys.stdin.read(100001)
                if len(text) > 100000:
                    raise ValueError("capture payload too large")
                record = capture(json.loads(text))
                result = {"inserted": db.import_records(args.namespace, [record])}
            elif args.command == "add":
                record = MemoryRecord(
                    content=args.content,
                    metadata={"key": args.key} if args.key else {},
                    evidence=[Evidence(args.content, args.source)] if args.source else [],
                )
                db.import_records(args.namespace, [record])
                result = record.to_dict()
            elif args.command == "import":
                if Path(args.file).resolve() == Path(args.db).resolve():
                    raise ValueError("source and destination must differ")
                if args.format == "true-mem":
                    records = true_mem(args.file, args.namespace, args.project, args.global_only)
                else:
                    if Path(args.file).stat().st_size > 20000000:
                        raise ValueError("maximum import size 20 MB")
                    text = Path(args.file).read_text(encoding="utf-8-sig")
                    if args.format == "open-mem":
                        records = open_mem(text, args.namespace)
                    elif args.format == "jsonl":
                        records = list(JsonlMemoryStore(args.file).all())
                    else:
                        payload = json.loads(text)
                        if (
                            payload.get("version") != 1
                            or payload.get("namespace") != args.namespace
                        ):
                            raise ValueError("version or namespace mismatch")
                        records = [MemoryRecord.from_dict(r) for r in payload["records"]]
                result = {"inserted": db.import_records(args.namespace, records)}
            elif args.command == "context":
                print(db.context(args.namespace, args.max_chars))
                return 0
            elif args.command == "search":
                result = [r.to_dict() for r in db.search(args.namespace, args.query)]
            elif args.command == "export":
                result = {
                    "version": 1,
                    "namespace": args.namespace,
                    "records": [r.to_dict() for r in db.search(args.namespace)],
                }
            elif args.command == "conflicts":
                result = db.conflicts(args.namespace)
            else:
                integrity = db.db.execute("PRAGMA integrity_check").fetchone()[0]
                if integrity != "ok":
                    raise ValueError("integrity check failed: " + integrity)
                result = {
                    "integrity": integrity,
                    "database": str(Path(args.db).resolve()),
                    "network_calls": False,
                }
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        IndexError,
        OSError,
        sqlite3.Error,
    ) as exc:
        print("AiMemory: " + str(exc), file=sys.stderr)
        return 2
