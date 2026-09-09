import pytest

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
