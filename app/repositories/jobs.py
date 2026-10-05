import json
import sqlite3
from datetime import datetime

from app.errors import UnknownJobError
from app.repositories.database import Database, utc_now
from app.schemas import Job


def _to_job(row: sqlite3.Row) -> Job:
    return Job(
        id=row["id"],
        source=row["source"],
        title=row["title"],
        company=row["company"],
        url=row["url"],
        location=row["location"],
        remote=bool(row["remote"]),
        description=row["description"],
        tags=json.loads(row["tags"]),
        salary=row["salary"],
        posted_at=datetime.fromisoformat(row["posted_at"]) if row["posted_at"] else None,
    )


class JobRepository:
    def __init__(self, db: Database) -> None:
        self.conn = db.conn

    def upsert_many(self, jobs: list[Job]) -> None:
        now = utc_now()
        with self.conn:
            self.conn.executemany(
                """INSERT INTO jobs (id, source, title, company, url, location, remote,
                                     description, tags, salary, posted_at, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                     title=excluded.title, company=excluded.company, location=excluded.location,
                     remote=excluded.remote, description=excluded.description, tags=excluded.tags,
                     salary=excluded.salary, posted_at=excluded.posted_at,
                     fetched_at=excluded.fetched_at""",
                [
                    (
                        j.id,
                        j.source,
                        j.title,
                        j.company,
                        j.url,
                        j.location,
                        int(j.remote),
                        j.description,
                        json.dumps(j.tags),
                        j.salary,
                        j.posted_at.isoformat() if j.posted_at else None,
                        now,
                    )
                    for j in jobs
                ],
            )

    def get(self, job_id: str) -> Job | None:
        row = self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return _to_job(row) if row else None

    def require(self, job_id: str) -> Job:
        job = self.get(job_id)
        if job is None:
            raise UnknownJobError(job_id)
        return job
