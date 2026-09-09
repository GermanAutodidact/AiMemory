import json
import sqlite3

import pytest

from aimemory import Evidence, MemoryRecord, SQLiteMemoryStore
from aimemory.adapters import open_mem, true_mem
from aimemory.cli import main


def test_atomic_id_collision(tmp_path):
    with SQLiteMemoryStore(tmp_path / "db") as db:
        r = MemoryRecord("one")
        assert db.import_records("a", [r]) == 1
        assert db.import_records("a", [r]) == 0
        with pytest.raises(ValueError):
            db.import_records("a", [MemoryRecord("new"), MemoryRecord("different", id=r.id)])
        assert len(db.search("a")) == 1
        assert db.search("b") == []
        assert db.search("a' OR 1=1 --") == []
    with SQLiteMemoryStore(tmp_path / "db") as db:
        assert db.search("a")[0].content == "one"


@pytest.mark.parametrize("confidence", [True, -1, 2, float("nan"), float("inf"), "high"])
def test_confidence(confidence):
    with pytest.raises(ValueError):
        Evidence("a", "source", confidence=confidence)


@pytest.mark.parametrize(
    "values",
    [
        {"content": ""},
        {"content": "ok", "tags": "bad"},
        {"content": "ok", "created_at": "2026-01-01"},
    ],
)
def test_record_validation(values):
    with pytest.raises(ValueError):
        MemoryRecord(**values)


def test_mutated_evidence_is_revalidated():
    e = Evidence("a", "b")
    r = MemoryRecord("a", evidence=[e])
    e.confidence = float("nan")
    with pytest.raises(ValueError):
        r.to_dict()


def test_context_and_conflicts(tmp_path):
    with SQLiteMemoryStore(tmp_path / "db") as db:
        db.import_records(
            "a",
            [
                MemoryRecord("red", metadata={"key": "colour"}),
                MemoryRecord("blue", metadata={"key": "colour"}),
                MemoryRecord("inactive", metadata={"inactive": True}),
            ],
        )
        assert len(db.conflicts("a")["colour"]) == 2
        assert db.context("a", 0) == ""
        for line in db.context("a").splitlines():
            assert json.loads(line)["content"] in ["red", "blue"]
        assert len(db.context("a", 400)) <= 400


def test_open_mem_export_mapping():
    item = {
        "id": "obs1",
        "narrative": "SQLite selected",
        "type": "decision",
        "createdAt": "2026-09-09T00:00:00Z",
        "concepts": ["db"],
        "facts": ["local"],
    }
    data = {"version": 1, "project": "/demo", "observations": [item], "summaries": []}
    result = open_mem("Exported 1 observation(s).\n\n" + json.dumps(data), "demo")
    assert result[0].content == "SQLite selected"
    assert result[0].metadata["original"]["facts"] == ["local"]
    assert result[0].evidence[0].status == "unverified"
    assert open_mem(json.dumps(data), "demo")[0].id == result[0].id
    assert open_mem(json.dumps(data), "other")[0].id != result[0].id
    data["version"] = 2
    with pytest.raises(ValueError):
        open_mem(json.dumps(data), "demo")


def test_true_mem_readonly_scope(tmp_path):
    path = tmp_path / "true.db"
    with sqlite3.connect(path) as source:
        source.execute(
            "CREATE TABLE memory_units (id TEXT, summary TEXT, classification TEXT, project_scope TEXT, created_at TEXT, source_event_ids TEXT, confidence REAL, status TEXT)"
        )
        for ident, project, status in [
            ("1", "/demo", "active"),
            ("2", None, "active"),
            ("3", "/other", "active"),
            ("4", "/demo", "decayed"),
        ]:
            source.execute(
                "INSERT INTO memory_units VALUES (?,?,?,?,?,?,?,?)",
                (
                    ident,
                    "fact",
                    "decision",
                    project,
                    "2026-09-09T00:00:00Z",
                    '["event1"]',
                    0.7,
                    status,
                ),
            )
    before = path.read_bytes()
    records = true_mem(path, "demo", project="/demo")
    assert len(records) == 1
    assert records[0].metadata["original"]["id"] == "1"
    assert records[0].metadata["source_event_ids"] == ["event1"]
    assert len(true_mem(path, "global", global_only=True)) == 1
    assert before == path.read_bytes()
    with pytest.raises(ValueError):
        true_mem(path, "demo")
    with pytest.raises(FileNotFoundError):
        true_mem(tmp_path / "missing", "demo", project="/demo")


def test_cli_export_import(tmp_path, capsys):
    base = ["--db", str(tmp_path / "db"), "--namespace", "demo"]
    assert main(base + ["add", "Grüße", "--source", "user:explicit"]) == 0
    capsys.readouterr()
    assert main(base + ["export"]) == 0
    file = tmp_path / "export.json"
    file.write_text(capsys.readouterr().out, encoding="utf-8")
    assert main(base + ["import", str(file)]) == 0
    assert json.loads(capsys.readouterr().out)["inserted"] == 0
    assert main(base + ["doctor"]) == 0
    file.write_text("[]")
    assert main(base + ["import", str(file)]) == 2
