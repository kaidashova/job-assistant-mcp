from app.repositories.database import Database
from app.schemas import Profile


class ProfileRepository:
    def __init__(self, db: Database) -> None:
        self.conn = db.conn

    def get(self) -> Profile | None:
        row = self.conn.execute("SELECT data FROM profile WHERE id = 1").fetchone()
        return Profile.model_validate_json(row["data"]) if row else None

    def save(self, profile: Profile) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO profile (id, data) VALUES (1, ?)"
                " ON CONFLICT(id) DO UPDATE SET data = excluded.data",
                (profile.model_dump_json(),),
            )
