from pydantic import BaseModel


class SourceQuery(BaseModel):
    """What a job source is asked to fetch; filtering is finished centrally by SearchService."""

    keywords: list[str]
    remote_only: bool = True
