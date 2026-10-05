from app.errors import JobAssistantError
from app.matching import match_job
from app.repositories import JobRepository, ProfileRepository
from app.schemas import MatchResult


class MatchingService:
    """Compares a cached posting with the stored profile."""

    def __init__(self, jobs: JobRepository, profile: ProfileRepository) -> None:
        self.jobs = jobs
        self.profile = profile

    def match(self, job_id: str) -> MatchResult:
        job = self.jobs.require(job_id)
        profile = self.profile.get()
        if profile is None or not profile.skills:
            raise JobAssistantError(
                "No profile stored yet. Call set_profile with your skills (and projects) first."
            )
        return match_job(job, profile)
