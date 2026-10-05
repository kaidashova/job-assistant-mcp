import httpx

from app.constants.sources import DJINNI_FEED_URL, DJINNI_KEYWORDS
from app.schemas import Job, SourceQuery
from app.sources.base import make_job_id
from app.sources.rss import parse_items
from app.utils.text import looks_remote


class DjinniSource:
    name = "djinni"

    async def fetch(self, client: httpx.AsyncClient, query: SourceQuery) -> list[Job]:
        params: dict[str, str] = {}
        for kw in query.keywords:
            if kw.lower() in DJINNI_KEYWORDS:
                params["primary_keyword"] = DJINNI_KEYWORDS[kw.lower()]
                break
        if query.remote_only:
            params["employment"] = "remote"
        resp = await client.get(DJINNI_FEED_URL, params=params)
        resp.raise_for_status()
        jobs = []
        for item in parse_items(resp.text):
            if not item["link"]:
                continue
            jobs.append(
                Job(
                    id=make_job_id("djinni", item["link"]),
                    source="djinni",
                    title=item["title"],
                    url=item["link"],
                    # the feed is already filtered by employment=remote when requested
                    remote=query.remote_only or looks_remote(item["title"], item["description"][:400]),
                    description=item["description"],
                    tags=[c for c in item["categories"] if c],
                    posted_at=item["published"],
                )
            )
        return jobs
