from collections.abc import Callable

import httpx
from pydantic import BaseModel, ConfigDict

from app.config import Settings
from app.repositories import ApplicationRepository, Database, JobRepository, ProfileRepository
from app.services.matching import MatchingService
from app.services.profile import ProfileService
from app.services.search import SearchService
from app.services.tracker import TrackerService
from app.sources import ALL_SOURCES, JobSource


class Services(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    search: SearchService
    tracker: TrackerService
    profile: ProfileService
    matching: MatchingService


def build_services(
    settings: Settings | None = None,
    *,
    db: Database | None = None,
    sources: dict[str, JobSource] | None = None,
    client_factory: Callable[[], httpx.AsyncClient] | None = None,
) -> Services:
    settings = settings or Settings()
    db = db or Database(settings.db_path)
    jobs, apps, profile = JobRepository(db), ApplicationRepository(db), ProfileRepository(db)
    client_factory = client_factory or (
        lambda: httpx.AsyncClient(
            timeout=settings.http_timeout,
            follow_redirects=True,
            headers={"User-Agent": settings.user_agent},
        )
    )
    return Services(
        search=SearchService(jobs, apps, profile, sources or ALL_SOURCES, client_factory),
        tracker=TrackerService(jobs, apps),
        profile=ProfileService(profile),
        matching=MatchingService(jobs, profile),
    )
