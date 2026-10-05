from enum import StrEnum

from pydantic import BaseModel, Field


class Status(StrEnum):
    SAVED = "saved"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class StatusChange(BaseModel):
    status: Status
    note: str = ""
    at: str


class Application(BaseModel):
    job_id: str
    title: str
    company: str
    url: str
    status: Status
    notes: str = ""
    saved_at: str
    updated_at: str
    history: list[StatusChange] = Field(default_factory=list)


class ApplicationRow(BaseModel):
    """Application without history, for list views."""

    job_id: str
    title: str
    company: str
    url: str
    source: str
    status: Status
    notes: str
    saved_at: str
    updated_at: str


class SaveResult(BaseModel):
    already_saved: bool
    application: Application


class Pipeline(BaseModel):
    counts: dict[str, int] = Field(description="Number of applications per status")
    applications: list[ApplicationRow]
