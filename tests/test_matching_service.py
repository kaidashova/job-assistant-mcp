import pytest
from conftest import search

from app.errors import JobAssistantError
from app.schemas import ProfileUpdate


async def test_match_requires_profile(services):
    job_id = (await search(services, "python")).jobs[0].job_id
    with pytest.raises(JobAssistantError, match="No profile"):
        services.matching.match(job_id)


async def test_match_job_to_profile(services, profile_kwargs):
    services.profile.update(ProfileUpdate(**profile_kwargs))
    job_id = (await search(services, "AI", "python")).jobs[0].job_id
    m = services.matching.match(job_id)
    assert 0 <= m.score <= 100 and m.url.startswith("http")


def test_match_unknown_job(services):
    with pytest.raises(JobAssistantError, match="Unknown job_id"):
        services.matching.match("nope")
