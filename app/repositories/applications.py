from app.repositories.database import Database, utc_now
from app.schemas import Application, ApplicationRow, Status, StatusChange


class ApplicationRepository:
    def __init__(self, db: Database) -> None:
        self.conn = db.conn

    def set_status(self, job_id: str, status: Status, notes: str | None = None) -> Application:
        """Create or update the application and append the change to its history."""
        now = utc_now()
        existing = self.conn.execute("SELECT notes FROM applications WHERE job_id = ?", (job_id,)).fetchone()
        with self.conn:
            if existing is None:
                self.conn.execute(
                    "INSERT INTO applications (job_id, status, notes, saved_at, updated_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (job_id, status.value, notes or "", now, now),
                )
            else:
                self.conn.execute(
                    "UPDATE applications SET status = ?, notes = ?, updated_at = ? WHERE job_id = ?",
                    (status.value, existing["notes"] if notes is None else notes, now, job_id),
                )
            self.conn.execute(
                "INSERT INTO status_history (job_id, status, note, at) VALUES (?, ?, ?, ?)",
                (job_id, status.value, notes or "", now),
            )
        return self.get(job_id)  # type: ignore[return-value]

    def get(self, job_id: str) -> Application | None:
        row = self.conn.execute(
            """SELECT a.*, j.title, j.company, j.url FROM applications a
               JOIN jobs j ON j.id = a.job_id WHERE a.job_id = ?""",
            (job_id,),
        ).fetchone()
        if row is None:
            return None
        history = self.conn.execute(
            "SELECT status, note, at FROM status_history WHERE job_id = ? ORDER BY id", (job_id,)
        ).fetchall()
        return Application(**dict(row), history=[StatusChange(**dict(h)) for h in history])

    def list(self, status: Status | None = None) -> list[ApplicationRow]:
        sql = """SELECT a.job_id, a.status, a.notes, a.saved_at, a.updated_at,
                        j.title, j.company, j.url, j.source
                 FROM applications a JOIN jobs j ON j.id = a.job_id"""
        params: tuple = ()
        if status:
            sql += " WHERE a.status = ?"
            params = (status.value,)
        sql += " ORDER BY a.updated_at DESC, a.rowid DESC"
        return [ApplicationRow(**dict(r)) for r in self.conn.execute(sql, params).fetchall()]

    def counts(self) -> dict[str, int]:
        rows = self.conn.execute("SELECT status, COUNT(*) AS n FROM applications GROUP BY status").fetchall()
        return {r["status"]: r["n"] for r in rows}
