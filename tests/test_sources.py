import httpx
import pytest
from conftest import mock_transport

from app.schemas import SourceQuery
from app.sources import ALL_SOURCES
from app.sources.base import make_job_id
from app.sources.rss import parse_items
from app.utils.text import strip_html


async def fetch(name: str, **kw):
    async with httpx.AsyncClient(transport=mock_transport()) as client:
        return await ALL_SOURCES[name].fetch(client, SourceQuery(keywords=["python"], **kw))


async def test_dou_parses_title_company_location():
    jobs = await fetch("dou")
    job = jobs[0]
    assert job.title == "Python Software Engineer"
    assert job.company == "PlantIn"
    assert job.location == "Київ, віддалено"
    assert job.remote is True
    assert "utm_source" not in job.url
    assert "LLM" in job.description and "<" not in job.description
    assert [j.remote for j in jobs] == [True, False, False]


async def test_djinni_parses_rss():
    old, new = await fetch("djinni")
    assert old.source == "djinni" and old.remote is True  # feed already filtered by remote
    assert old.tags == ["Python"] and old.posted_at is not None
    assert new.title == "Senior AI Engineer (R&D)"  # double-escaped entity decoded
    assert new.tags == ["Python", "Data Science"]


async def test_djinni_remote_flag_follows_query():
    jobs = await fetch("djinni", remote_only=False)
    assert [j.remote for j in jobs] == [True, False]  # only the first mentions "Remote"


async def test_djinni_query_params():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(request.url.params)
        return httpx.Response(200, text="<rss><channel></channel></rss>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await ALL_SOURCES["djinni"].fetch(client, SourceQuery(keywords=["python"]))
    assert seen == {"primary_keyword": "Python", "employment": "remote"}


async def test_dou_query_params_use_category_and_remote():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(request.url.params)
        return httpx.Response(200, text="<rss><channel></channel></rss>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await ALL_SOURCES["dou"].fetch(client, SourceQuery(keywords=["python", "ai"]))
    assert seen["category"] == "Python" and "remote" in seen


def test_job_id_is_stable_and_ignores_tracking_params():
    a = make_job_id("dou", "https://x.io/job/1/?utm_source=a")
    assert a == make_job_id("dou", "https://x.io/job/1")
    assert a.startswith("dou:")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("<p>Hi&nbsp;<b>there</b></p><ul><li>A</li><li>B</li></ul>", "Hi there\n- A\n- B"),
        ("&lt;p&gt;escaped&lt;/p&gt;", "escaped"),
        ("", ""),
    ],
)
def test_strip_html(raw, expected):
    assert strip_html(raw) == expected


def test_rss_titles_are_unescaped():
    xml = "<rss><channel><item><title>Engineer (R&amp;amp;D)</title><link>http://x</link></item></channel></rss>"
    assert parse_items(xml)[0]["title"] == "Engineer (R&D)"
