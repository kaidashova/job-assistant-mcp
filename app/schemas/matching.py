from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    skills: int = Field(description="out of 65")
    role: int = Field(description="out of 20")
    seniority: int = Field(description="out of 15")


class ProjectRelevance(BaseModel):
    name: str
    description: str
    relevant_tech: list[str]


class MatchResult(BaseModel):
    job_id: str
    title: str
    company: str
    url: str = ""
    score: int = Field(ge=0, le=100)
    verdict: str
    matched_skills: list[str]
    missing_skills: list[str]
    breakdown: ScoreBreakdown
    relevant_projects: list[ProjectRelevance]
    notes: list[str]
