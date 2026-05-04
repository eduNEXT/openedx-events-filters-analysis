import sqlite3
from datetime import datetime, timezone


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at      TIMESTAMP NOT NULL,
            script      TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            notes       TEXT
        );

        CREATE TABLE IF NOT EXISTS results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          INTEGER NOT NULL REFERENCES runs(id),
            repository      TEXT NOT NULL,
            repository_url  TEXT NOT NULL,
            is_fork         BOOLEAN NOT NULL DEFAULT 0,
            file_path       TEXT NOT NULL,
            file_url        TEXT NOT NULL,
            signal          TEXT NOT NULL,
            phase           TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pr_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          INTEGER NOT NULL REFERENCES runs(id),
            pr_url          TEXT NOT NULL,
            title           TEXT,
            repository      TEXT NOT NULL,
            repository_url  TEXT NOT NULL,
            is_fork         BOOLEAN NOT NULL DEFAULT 0,
            author          TEXT,
            organization    TEXT
        );
    """)
    conn.commit()
    conn.close()


def record_run(db_path, script, signal_type, notes=None):
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        "INSERT INTO runs (run_at, script, signal_type, notes) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), script, signal_type, notes),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def record_results(db_path, run_id, results):
    conn = sqlite3.connect(db_path)
    conn.executemany(
        """INSERT INTO results
               (run_id, repository, repository_url, is_fork, file_path, file_url, signal, phase)
           VALUES
               (:run_id, :repository, :repository_url, :is_fork, :file_path, :file_url, :signal, :phase)""",
        [{"run_id": run_id, **r} for r in results],
    )
    conn.commit()
    conn.close()


def record_pr_results(db_path, run_id, pr_results):
    conn = sqlite3.connect(db_path)
    conn.executemany(
        """INSERT INTO pr_results
               (run_id, pr_url, title, repository, repository_url, is_fork, author, organization)
           VALUES
               (:run_id, :pr_url, :title, :repository, :repository_url, :is_fork, :author, :organization)""",
        [{"run_id": run_id, **r} for r in pr_results],
    )
    conn.commit()
    conn.close()
