import asyncio
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import httpx

from app.constants.search import MAX_DESCRIPTION_CHARS
from app.errors import JobAssistantError
from app.matching import match_job
from app.repositories import ApplicationRepository, JobRepository, ProfileRepository
from app.schemas import Job, JobDetail, JobSummary, SearchParams, SearchResult, SourceQuery
from app.services.filters import dedupe, filter_jobs
from app.sources import JobSource


class SearchService:
    """Fetches postings from the boards, filters/scores them and serves cached lookups."""

    def __init__(
        self,
        jobs: JobRepository,
        applications: ApplicationRepository,
        profile: ProfileRepository,
        sources: dict[str, JobSource],
        client_factory: Callable[[], httpx.AsyncClient],
    ) -> None:
        self.jobs = jobs
        self.applications = applications
        self.profile = profile
        self.sources = sources
        self._client_factory = client_factory

    async def search(self, params: SearchParams) -> SearchResult:
        keywords = [k.strip() for k in params.keywords if k and k.strip()]
        names = params.sources or list(self.sources)
        unknown = [n for n in names if n not in self.sources]
        if unknown:
            raise JobAssistantError(
                f"Unknown source(s): {', '.join(unknown)}. Available: {', '.join(self.sources)}"
            )

        fetched, errors = await self._fetch_all(
            names, SourceQuery(keywords=keywords, remote_only=params.remote_only)
        )
        since = (
            datetime.now(UTC) - timedelta(days=params.posted_within_days)
            if params.posted_within_days
            else None
        )
        matched = dedupe(
            filter_jobs(
                fetched,
                keywords,
                remote_only=params.remote_only,
                since=since,
                match_all=params.match_all_keywords,
            )
        )

        by_source: dict[str, int] = {}
        for job in matched:
            by_source[job.source] = by_source.get(job.source, 0) + 1

        profile = self.profile.get()
        rows = []
        for job in matched:
            row = JobSummary.from_job(job)
            if profile:
                m = match_job(job, profile)
                row.score, row.verdict, row.matched_skills = m.score, m.verdict, m.matched_skills
            rows.append(row)
        rows.sort(key=lambda r: r.posted_at or datetime.min.date(), reverse=True)  # newest first...
        if profile:
            rows.sort(key=lambda r: r.score or 0, reverse=True)  # ...then best fit (stable)

        return SearchResult(
            total_found=len(rows),
            returned=min(len(rows), params.limit),
            by_source=by_source,
            errors=errors,
            scored_against_profile=profile is not None,
            jobs=rows[: params.limit],
        )

    async def _fetch_all(self, names: list[str], query: SourceQuery) -> tuple[list[Job], dict[str, str]]:
        """Query boards concurrently; one failing board never fails the search."""
        async with self._client_factory() as client:
            results = await asyncio.gather(
                *(self.sources[n].fetch(client, query) for n in names), return_exceptions=True
            )
        jobs: list[Job] = []
        errors: dict[str, str] = {}
        for name, res in zip(names, results, strict=True):
            if isinstance(res, BaseException):
                errors[name] = f"{type(res).__name__}: {res}"
                continue
            self.jobs.upsert_many(res)  # cache so job_ids stay resolvable in later calls
            jobs.extend(res)
        return jobs, errors

    def get_job(self, job_id: str) -> JobDetail:
        job = self.jobs.require(job_id)
        detail = JobDetail(**job.model_dump())
        detail.description = job.description[:MAX_DESCRIPTION_CHARS]
        detail.application = self.applications.get(job_id)
        return detail
