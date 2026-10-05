from pydantic import BaseModel, Field


class Project(BaseModel):
    name: str
    description: str = ""
    tech: list[str] = Field(default_factory=list)


class Profile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    years_experience: float | None = None
    target_roles: list[str] = Field(default_factory=list)
    summary: str = ""
    projects: list[Project] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    """Partial update: fields left as None are kept as they are."""

    skills: list[str] | None = None
    years_experience: float | None = Field(None, ge=0, le=60)
    target_roles: list[str] | None = None
    summary: str | None = None
    projects: list[Project] | None = None
