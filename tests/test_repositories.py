from app.repositories import Database, JobRepository, ProfileRepository
from app.schemas import Job, Profile


def test_profile_persists_across_connections(tmp_path):
    path = tmp_path / "nested" / "x.db"  # parent dir is created on demand
    ProfileRepository(Database(path)).save(Profile(skills=["python"]))
    assert ProfileRepository(Database(path)).get().skills == ["python"]


def test_job_upsert_updates_existing_row():
    repo = JobRepository(Database())
    repo.upsert_many([Job(id="a:1", source="a", title="Old", url="http://x")])
    repo.upsert_many([Job(id="a:1", source="a", title="New", url="http://x", tags=["t"])])
    job = repo.get("a:1")
    assert job.title == "New" and job.tags == ["t"]
    assert repo.get("missing") is None
