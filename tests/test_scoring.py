from app.matching import match_job
from app.matching.scoring import job_level, profile_level
from app.schemas import Job, Profile, Project


def job(title="Python Developer", description="", **kw) -> Job:
    return Job(id="t:1", source="t", title=title, url="http://x", description=description, **kw)


def test_levels():
    assert job_level("Senior Python Engineer") == 3
    assert job_level("Junior QA") == 1
    assert job_level("Python Developer") is None
    assert profile_level(0.5) == 0 and profile_level(3) == 2 and profile_level(10) == 4


def test_strong_match_scores_high_and_reports_gaps():
    p = Profile(skills=["python", "fastapi", "docker"], years_experience=3, target_roles=["Python Developer"])
    j = job("Middle Python Developer", "Python, FastAPI, Docker and Kubernetes experience.")
    m = match_job(j, p)
    assert m.score >= 75 and m.verdict == "strong match"
    assert m.matched_skills == ["docker", "fastapi", "python"]
    assert m.missing_skills == ["kubernetes"]


def test_unrelated_job_scores_low():
    p = Profile(skills=["python"], years_experience=3, target_roles=["Python Developer"])
    m = match_job(job("Senior Java Engineer", "Java, Spring, Kafka, AWS"), p)
    assert m.score < 35 and m.matched_skills == []


def test_seniority_mismatch_is_penalised_and_explained():
    p = Profile(skills=["python"], years_experience=1)
    m = match_job(job("Lead Python Engineer", "python"), p)
    assert m.breakdown.seniority == 0
    assert any("lead-level" in n for n in m.notes)


def test_relevant_projects_ranked_by_overlap():
    p = Profile(
        skills=["python", "rag"],
        projects=[Project(name="A", tech=["python"]), Project(name="B", tech=["python", "rag"])],
    )
    m = match_job(job("AI Engineer", "Python and RAG pipelines"), p)
    assert [x.name for x in m.relevant_projects] == ["B", "A"]


def test_no_detected_skills_is_neutral_not_zero():
    m = match_job(job("Developer", "great team"), Profile(skills=["python"]))
    assert m.notes and m.score > 0
