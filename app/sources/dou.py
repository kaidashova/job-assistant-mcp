import httpx

from app.constants.sources import DOU_CATEGORIES, DOU_FEED_URL
from app.schemas import Job, SourceQuery
from app.sources.base import make_job_id
from app.sources.rss import parse_items
from app.utils.text import looks_remote


class DouSource:
    name = "dou"

    async def fetch(self, client: httpx.AsyncClient, query: SourceQuery) -> list[Job]:
        params: dict[str, str] = {}
        for kw in query.keywords:
            if kw.lower() in DOU_CATEGORIES:
                params["category"] = DOU_CATEGORIES[kw.lower()]
                break
        if query.remote_only:
            params["remote"] = ""
        resp = await client.get(DOU_FEED_URL, params=params)
        resp.raise_for_status()
        return [self._to_job(i) for i in parse_items(resp.text) if i["link"]]

    @staticmethod
    def _to_job(item: dict) -> Job:
        # Titles look like "Python Software Engineer в PlantIn, Київ, віддалено"
        title, sep, rest = item["title"].rpartition(" в ")
        if not sep:
            title, rest = item["title"], ""
        company, _, location = rest.partition(",")
        location = location.strip()
        return Job(
            id=make_job_id("dou", item["link"]),
            source="dou",
            title=title.strip(),
            company=company.strip(),
            url=item["link"].split("?")[0],
            location=location,
            remote=looks_remote(location, item["title"]),
            description=item["description"],
            posted_at=item["published"],
        )
