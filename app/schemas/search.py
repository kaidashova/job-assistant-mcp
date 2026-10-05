from pydantic import BaseModel, Field

from app.schemas.job import JobSummary


class SearchParams(BaseModel):
    keywords: list[str] = Field(description="Terms to look for, e.g. ['python', 'AI'].")
    remote_only: bool = Field(True, description="Only remote positions.")
    posted_within_days: int | None = Field(7, ge=1, le=90, description="Only postings from the last N days.")
    sources: list[str] | None = Field(None, description="Subset of boards to query (default: all).")
    match_all_keywords: bool = Field(True, description="Require every keyword (AND) instead of any (OR).")
    limit: int = Field(20, ge=1, le=100)


class SearchResult(BaseModel):
    total_found: int
    returned: int
    by_source: dict[str, int]
    errors: dict[str, str] = Field(description="Boards that failed, with the reason")
    scored_against_profile: bool
    jobs: list[JobSummary]
