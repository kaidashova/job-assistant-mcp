from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from app.constants.server import TOOL_READ_ONLY, TOOL_SEARCH, TOOL_WRITES_LOCAL
from app.container import Services
from app.errors import JobAssistantError
from app.schemas import (
    Application,
    JobDetail,
    MatchResult,
    Pipeline,
    Profile,
    ProfileUpdate,
    Project,
    SaveResult,
    SearchParams,
    SearchResult,
)
from app.sources import ALL_SOURCES


def tool_errors(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Surface domain errors to the model as clean tool errors (not 'unexpected exception')."""

    @wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await fn(*args, **kwargs)
        except JobAssistantError as exc:
            raise ToolError(str(exc)) from exc

    return wrapper


def register_tools(mcp: MCPServer, svc: Services) -> None:
    @mcp.tool(annotations=TOOL_SEARCH)
    @tool_errors
    async def search_jobs(
        keywords: Annotated[list[str], Field(description="Terms to look for, e.g. ['python', 'AI'].")],
        remote_only: Annotated[bool, Field(description="Only remote positions.")] = True,
        posted_within_days: Annotated[
            int, Field(ge=1, le=90, description="Only postings from the last N days.")
        ] = 7,
        sources: Annotated[
            list[str] | None,
            Field(description=f"Subset of boards to query. Available: {', '.join(ALL_SOURCES)}."),
        ] = None,
        match_all_keywords: Annotated[
            bool, Field(description="Require every keyword (AND) instead of any (OR).")
        ] = True,
        limit: Annotated[int, Field(ge=1, le=100)] = 20,
    ) -> SearchResult:
        """Search live job boards concurrently. If a profile is stored, each result carries a
        0-100 fit score and results are sorted best-first; otherwise newest-first."""
        params = SearchParams(
            keywords=keywords,
            remote_only=remote_only,
            posted_within_days=posted_within_days,
            sources=sources,
            match_all_keywords=match_all_keywords,
            limit=limit,
        )
        return await svc.search.search(params)

    @mcp.tool(annotations=TOOL_READ_ONLY)
    @tool_errors
    async def get_job(job_id: str) -> JobDetail:
        """Full details (description, tags, application status) of a job from search results."""
        return svc.search.get_job(job_id)

    @mcp.tool(annotations=TOOL_READ_ONLY)
    @tool_errors
    async def match_job_to_profile(job_id: str) -> MatchResult:
        """Compare a posting with the stored profile: score, matched/missing skills, seniority
        fit and which of your projects are most relevant to mention."""
        return svc.matching.match(job_id)

    @mcp.tool(annotations=TOOL_WRITES_LOCAL)
    @tool_errors
    async def save_job(job_id: str, notes: str = "") -> SaveResult:
        """Add a job to your application tracker with status 'saved'."""
        return svc.tracker.save(job_id, notes)

    @mcp.tool(annotations=TOOL_WRITES_LOCAL)
    @tool_errors
    async def update_status(
        job_id: str,
        status: Annotated[
            str,
            Field(description="saved | applied | screening | interview | offer | rejected | withdrawn"),
        ],
        notes: str | None = None,
    ) -> Application:
        """Move a job through the pipeline; every change is kept in its history."""
        return svc.tracker.update_status(job_id, status, notes)

    @mcp.tool(annotations=TOOL_READ_ONLY)
    @tool_errors
    async def list_applications(status: str | None = None) -> Pipeline:
        """Your tracked jobs (optionally filtered by status) plus counts per pipeline stage."""
        return svc.tracker.pipeline(status)

    @mcp.tool(annotations=TOOL_WRITES_LOCAL)
    @tool_errors
    async def set_profile(
        skills: list[str] | None = None,
        years_experience: float | None = None,
        target_roles: list[str] | None = None,
        summary: str | None = None,
        projects: list[Project] | None = None,
    ) -> Profile:
        """Create/update your profile. Only the fields you pass are changed."""
        return svc.profile.update(
            ProfileUpdate(
                skills=skills,
                years_experience=years_experience,
                target_roles=target_roles,
                summary=summary,
                projects=projects,
            )
        )

    @mcp.tool(annotations=TOOL_READ_ONLY)
    @tool_errors
    async def get_profile() -> Profile:
        """Return the stored profile (empty if none has been set yet)."""
        return svc.profile.get() or Profile()
