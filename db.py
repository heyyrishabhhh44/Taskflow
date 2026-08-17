"""
db.py — database connection layer for TaskFlow.

Defaults to a local SQLite file (data/taskflow.db) so the project runs with
zero setup. To point this at real PostgreSQL instead (recommended before you
publish this repo, since the schema was designed for Postgres):

    1. pip install psycopg2-binary
    2. createdb taskflow
    3. psql -d taskflow -f schema_postgres.sql
    4. set an environment variable:  export DATABASE_URL="postgresql://user:pass@localhost/taskflow"
    5. uncomment the psycopg2 branch below

Everything else in the project (validation.py, reports.py, app.py) talks to
this module only — it never touches sqlite3/psycopg2 directly — so the swap
is a one-file change.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "data", "taskflow.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema_sqlite.sql")

DATABASE_URL = os.environ.get("DATABASE_URL")  # set this to use real Postgres


def get_connection():
    """Return a DB connection. SQLite by default; Postgres if DATABASE_URL is set."""
    if DATABASE_URL:
        # import psycopg2  # pip install psycopg2-binary
        # return psycopg2.connect(DATABASE_URL)
        raise NotImplementedError(
            "Install psycopg2-binary and uncomment the two lines above to enable Postgres."
        )
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """(Re)create all tables from schema_sqlite.sql. Destructive — wipes existing data."""
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {SQLITE_PATH}")
