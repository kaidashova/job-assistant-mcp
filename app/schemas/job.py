from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, Field

from app.schemas.application import Application


class Job(BaseModel):
    """A normalized posting, independent of the board it came from."""

    id: str
    source: str
    title: str
    company: str = ""
    url: str
    location: str = ""
    remote: bool = False
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    salary: str = ""
    posted_at: datetime | None = None


class JobSummary(BaseModel):
    """Compact row for search results (no description). Score fields need a stored profile."""

    job_id: str
    title: str
    company: str
    source: str
    location: str
    remote: bool
    salary: str
    posted_at: date | None
    url: str
    score: int | None = Field(None, description="0-100 fit with your profile")
    verdict: str | None = None
    matched_skills: list[str] | None = None

    @classmethod
    def from_job(cls, job: Job) -> Self:
        return cls(
            job_id=job.id,
            title=job.title,
            company=job.company,
            source=job.source,
            location=job.location,
            remote=job.remote,
            salary=job.salary,
            posted_at=job.posted_at.date() if job.posted_at else None,
            url=job.url,
        )


class JobDetail(Job):
    application: Application | None = None
