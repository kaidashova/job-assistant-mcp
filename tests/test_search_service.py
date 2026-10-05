import httpx
import pytest
from conftest import make_services, search

from app.container import build_services
from app.errors import JobAssistantError
from app.schemas import ProfileUpdate, SearchParams


async def test_filters_remote_keywords_and_dates(services):
    res = await search(services, "python", "AI", posted_within_days=7)
    titles = {j.title for j in res.jobs}
    # the keyword must appear in the posting itself (title/tags/description)
    assert "Senior AI Engineer (R&D)" in titles
    assert "Middle Python Developer (ML)" not in titles  # 30 days old
    assert "Senior Java Developer" not in titles
    assert res.errors == {}


async def test_remote_only_excludes_onsite(services):
    assert "Python Dev" not in {j.title for j in (await search(services, "python")).jobs}
    res = await search(services, "python", remote_only=False)
    assert "Python Dev" in {j.title for j in res.jobs}


async def test_any_vs_all_keywords(services):
    all_ = await search(services, "python", "kubernetes", match_all_keywords=True)
    any_ = await search(services, "python", "kubernetes", match_all_keywords=False)
    assert all_.total_found < any_.total_found


async def test_one_failing_source_does_not_break_search():
    res = await search(make_services(failing={"djinni.co"}), "python")
    assert "djinni" in res.errors and res.total_found > 0


async def test_unknown_source_rejected(services):
    with pytest.raises(JobAssistantError, match="Unknown source"):
        await search(services, "python", sources=["linkedin"])


async def test_source_subset(services):
    res = await search(services, "python", sources=["dou"])
    assert set(res.by_source) == {"dou"}


async def test_scored_and_sorted_when_profile_exists(services, profile_kwargs):
    services.profile.update(ProfileUpdate(**profile_kwargs))
    res = await search(services, "python", posted_within_days=90, limit=2)
    scores = [j.score for j in res.jobs]
    assert res.scored_against_profile and scores == sorted(scores, reverse=True)
    assert res.total_found == 3 and res.returned == 2 and len(res.jobs) == 2


async def test_unscored_without_profile(services):
    res = await search(services, "python")
    assert not res.scored_against_profile and res.jobs[0].score is None


async def test_get_job_returns_detail_with_application(services):
    job_id = (await search(services, "python")).jobs[0].job_id
    assert services.search.get_job(job_id).application is None
    services.tracker.save(job_id)
    assert services.search.get_job(job_id).application.status == "saved"


def test_get_unknown_job(services):
    with pytest.raises(JobAssistantError, match="Unknown job_id"):
        services.search.get_job("nope")


def test_search_params_validation():
    with pytest.raises(ValueError):
        SearchParams(keywords=["x"], limit=0)
    with pytest.raises(ValueError):
        SearchParams(keywords=["x"], posted_within_days=500)


async def test_failure_message_names_the_error():
    def boom(request):
        raise httpx.ConnectError("no network")

    svc = build_services(client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(boom)))
    res = await svc.search.search(SearchParams(keywords=["python"]))
    assert res.total_found == 0 and all("ConnectError" in e for e in res.errors.values())
