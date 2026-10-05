class JobAssistantError(Exception):
    """User-facing domain error (unknown job id, invalid status, missing profile...)."""


class UnknownJobError(JobAssistantError):
    def __init__(self, job_id: str) -> None:
        super().__init__(f"Unknown job_id '{job_id}'. Run search_jobs first; ids come from its results.")
