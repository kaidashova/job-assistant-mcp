from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import __version__


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,  # env vars use the aliases below; code/tests may use field names
    )

    db_path: Path = Field(
        default_factory=lambda: Path.home() / ".job-assistant" / "jobs.db",
        alias="JOB_ASSISTANT_DB",
        description="SQLite database file",
    )
    transport: Literal["stdio", "streamable-http"] = Field("stdio", alias="MCP_TRANSPORT")
    host: str = Field("127.0.0.1", alias="MCP_HOST")
    port: int = Field(8000, ge=1, le=65535, alias="MCP_PORT")
    http_timeout: float = Field(20.0, gt=0, alias="JOB_ASSISTANT_HTTP_TIMEOUT")
    user_agent: str = f"job-assistant-mcp/{__version__} (personal job search tool)"

    @field_validator("db_path")
    @classmethod
    def _expand_user(cls, value: Path) -> Path:
        return value.expanduser()
