from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from pathlib import Path

import httpx
import pytest

from app.container import Services, build_services
from app.repositories import Database
from app.schemas import SearchParams

FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime.now(UTC)


def fixture(name: str) -> str:
    return (
        (FIXTURES / name)
        .read_text()
        .replace("{RECENT_ISO}", (NOW - timedelta(days=1)).isoformat())
        .replace("{RECENT}", format_datetime(NOW - timedelta(days=1)))
        .replace("{OLD}", format_datetime(NOW - timedelta(days=30)))
        .replace("{EPOCH}", str(int((NOW - timedelta(days=1)).timestamp())))
    )


def mock_transport(failing: set[str] = frozenset()) -> httpx.MockTransport:
    """Serve fixtures for every board; hosts listed in ``failing`` return HTTP 500."""
    routes = {
        "jobs.dou.ua": "dou.xml",
        "djinni.co": "djinni.xml",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if host in failing:
            return httpx.Response(500)
        return httpx.Response(200, text=fixture(routes[host]))

    return httpx.MockTransport(handler)


def make_services(failing: set[str] = frozenset(), db: Database | None = None) -> Services:
    return build_services(
        db=db or Database(":memory:"),
        client_factory=lambda: httpx.AsyncClient(transport=mock_transport(failing)),
    )


@pytest.fixture
def services() -> Services:
    return make_services()


@pytest.fixture
def profile_kwargs() -> dict:
    return dict(
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "LLM", "RAG"],
        years_experience=3,
        target_roles=["Python Developer", "AI Engineer"],
        projects=[
            {"name": "Job MCP", "description": "MCP server", "tech": ["python", "sqlite", "mcp"]},
            {"name": "RAG bot", "description": "Docs Q&A", "tech": ["python", "rag", "postgres"]},
        ],
    )


async def search(services: Services, *keywords: str, **kw):
    return await services.search.search(SearchParams(keywords=list(keywords), **kw))
