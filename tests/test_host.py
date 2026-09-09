import pytest

from aimemory import host
from aimemory.host import capture, install_plugin


def test_capture_deterministic():
    p = {
        "content": "Deutsch",
        "source": "opencode:session:message",
        "created_at": "2026-09-09T00:00:00Z",
    }
    assert capture(p).to_dict() == capture(p).to_dict()
    with pytest.raises(ValueError):
        capture(dict(p, content=""))
    with pytest.raises(ValueError):
        capture(dict(p, instructions="bad"))


def test_install_preserves_existing(tmp_path):
    install_plugin(tmp_path)
    assert install_plugin(tmp_path)["status"] == "already installed"
    path = tmp_path / ".opencode/plugins/aimemory.js"
    path.write_text("user changes")
    with pytest.raises(ValueError):
        install_plugin(tmp_path)
    assert path.read_text() == "user changes"


def test_global_install_and_managed_update(tmp_path, monkeypatch):
    monkeypatch.setattr(host.Path, "home", lambda: tmp_path)
    result = install_plugin(global_install=True)
    path = tmp_path / ".config/opencode/plugins/aimemory.js"
    assert result["path"] == str(path)
    assert path.read_text().startswith("// AiMemory managed OpenCode plugin")
    path.write_text("// AiMemory managed OpenCode plugin\nold")
    assert "updated" in install_plugin(global_install=True, update=True)["status"]
    with pytest.raises(ValueError):
        install_plugin(tmp_path, global_install=True)
