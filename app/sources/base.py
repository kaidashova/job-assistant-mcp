import hashlib
import re
from typing import Protocol

import httpx

from app.schemas import Job, SourceQuery


class JobSource(Protocol):
    name: str

    async def fetch(self, client: httpx.AsyncClient, query: SourceQuery) -> list[Job]: ...


def make_job_id(source: str, url: str) -> str:
    """Stable id derived from the posting URL, e.g. ``dou:3f9a1c0b2d``."""
    clean = re.sub(r"[?#].*$", "", url).rstrip("/")
    return f"{source}:{hashlib.sha1(clean.encode()).hexdigest()[:10]}"
