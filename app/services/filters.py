import re
from datetime import datetime

from app.matching.skills import VOCAB, normalize_skill
from app.schemas import Job


def keyword_pattern(keyword: str) -> re.Pattern[str]:
    """Word-boundary regex for a keyword, including its known aliases (ml, k8s, ...)."""
    canon = normalize_skill(keyword)
    terms = {keyword.lower(), canon, *VOCAB.get(canon, [])}
    alternatives = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    return re.compile(rf"(?<![\w+#]){alternatives}(?![\w+#])", re.IGNORECASE)


def filter_jobs(
    jobs: list[Job],
    keywords: list[str],
    *,
    remote_only: bool,
    since: datetime | None,
    match_all: bool,
) -> list[Job]:
    patterns = [keyword_pattern(k) for k in keywords]
    quantifier = all if match_all else any
    out = []
    for job in jobs:
        if remote_only and not job.remote:
            continue
        if since and job.posted_at and job.posted_at < since:
            continue
        haystack = f"{job.title}\n{' '.join(job.tags)}\n{job.description}"
        if patterns and not quantifier(p.search(haystack) for p in patterns):
            continue
        out.append(job)
    return out


def dedupe(jobs: list[Job]) -> list[Job]:
    """Drop cross-posted duplicates (same title + company)."""
    seen: set[tuple[str, str]] = set()
    out = []
    for job in jobs:
        key = (job.title.lower().strip(), job.company.lower().strip())
        if job.company and key in seen:
            continue
        seen.add(key)
        out.append(job)
    return out
