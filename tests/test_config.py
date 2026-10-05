import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_read_env(tmp_path, monkeypatch):
    monkeypatch.setenv("JOB_ASSISTANT_DB", str(tmp_path / "a.db"))
    monkeypatch.setenv("MCP_PORT", "9000")
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("MCP_HOST", "0.0.0.0")
    s = Settings(_env_file=None)
    assert (s.port, s.transport, s.host) == (9000, "streamable-http", "0.0.0.0")
    assert s.db_path == tmp_path / "a.db"


def test_settings_defaults(monkeypatch):
    for var in ("JOB_ASSISTANT_DB", "MCP_TRANSPORT", "MCP_HOST", "MCP_PORT"):
        monkeypatch.delenv(var, raising=False)
    s = Settings(_env_file=None)
    assert (s.transport, s.host, s.port) == ("stdio", "127.0.0.1", 8000)
    assert s.db_path.name == "jobs.db" and ".job-assistant" in str(s.db_path)


def test_settings_validation(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "carrier-pigeon")
    with pytest.raises(ValidationError, match="MCP_TRANSPORT"):
        Settings(_env_file=None)
    monkeypatch.setenv("MCP_TRANSPORT", "stdio")
    monkeypatch.setenv("MCP_PORT", "99999")
    with pytest.raises(ValidationError, match="MCP_PORT"):
        Settings(_env_file=None)


def test_settings_accept_field_names_and_expand_home():
    s = Settings(db_path="~/x.db", port=1234, _env_file=None)
    assert s.port == 1234 and "~" not in str(s.db_path)
