from app.errors import JobAssistantError
from app.repositories import ApplicationRepository, JobRepository
from app.schemas import Application, Pipeline, SaveResult, Status


def parse_status(value: str) -> Status:
    try:
        return Status(value.strip().lower())
    except ValueError:
        raise JobAssistantError(
            f"Invalid status '{value}'. Use one of: {', '.join(s.value for s in Status)}"
        ) from None


class TrackerService:
    """Application pipeline: saved -> applied -> ... with history."""

    def __init__(self, jobs: JobRepository, applications: ApplicationRepository) -> None:
        self.jobs = jobs
        self.applications = applications

    def save(self, job_id: str, notes: str = "") -> SaveResult:
        self.jobs.require(job_id)
        existing = self.applications.get(job_id)
        if existing:
            return SaveResult(already_saved=True, application=existing)
        return SaveResult(
            already_saved=False, application=self.applications.set_status(job_id, Status.SAVED, notes)
        )

    def update_status(self, job_id: str, status: str, notes: str | None = None) -> Application:
        self.jobs.require(job_id)
        return self.applications.set_status(job_id, parse_status(status), notes)

    def pipeline(self, status: str | None = None) -> Pipeline:
        return Pipeline(
            counts=self.applications.counts(),
            applications=self.applications.list(parse_status(status) if status else None),
        )
