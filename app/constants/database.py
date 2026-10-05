SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id          TEXT PRIMARY KEY,
    source      TEXT NOT NULL,
    title       TEXT NOT NULL,
    company     TEXT NOT NULL DEFAULT '',
    url         TEXT NOT NULL,
    location    TEXT NOT NULL DEFAULT '',
    remote      INTEGER NOT NULL DEFAULT 0,
    description TEXT NOT NULL DEFAULT '',
    tags        TEXT NOT NULL DEFAULT '[]',
    salary      TEXT NOT NULL DEFAULT '',
    posted_at   TEXT,
    fetched_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS applications (
    job_id     TEXT PRIMARY KEY REFERENCES jobs(id),
    status     TEXT NOT NULL,
    notes      TEXT NOT NULL DEFAULT '',
    saved_at   TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS status_history (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    status TEXT NOT NULL,
    note   TEXT NOT NULL DEFAULT '',
    at     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS profile (
    id   INTEGER PRIMARY KEY CHECK (id = 1),
    data TEXT NOT NULL
);
"""
