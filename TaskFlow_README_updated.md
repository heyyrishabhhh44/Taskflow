# TaskFlow — Task & Productivity Management System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-schema-4169E1?logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-reporting-150458?logo=pandas&logoColor=white)

A task & productivity management system with a normalized PostgreSQL schema,
an input-validated data pipeline, pandas-based reporting, and a Flask
dashboard for tracking tasks across projects and users.

![Dashboard screenshot](dashboard_screenshot.png)

## Features

- **Normalized schema** — `users`, `projects`, `priorities`, `tasks` with
  foreign keys and a `CHECK` constraint on task status.
- **Input validation** (`validation.py`) — rejects bad records (missing
  title, invalid date, unknown status/priority, references to a
  nonexistent project or user) *before* they reach the database.
  `seed_data.py` demonstrates this by feeding in 5 intentionally bad
  records and showing all 5 get rejected.
- **Reporting** (`reports.py`) — uses pandas to classify tasks into
  pending / completed / overdue and exports each to CSV, plus a
  per-user productivity summary (completion rate, overdue count).
- **Dashboard** (`app.py`) — a Flask app that renders the same data as a
  live, filterable web page.

## Project structure

```
taskflow/
├── schema_postgres.sql   # target schema (PostgreSQL)
├── schema_sqlite.sql     # same schema, SQLite dialect, used for local dev
├── db.py                 # connection layer (SQLite by default)
├── validation.py         # input validation rules
├── seed_data.py          # populates sample data + proves validation works
├── reports.py            # pandas report generation
├── app.py                # Flask dashboard
├── templates/dashboard.html
└── requirements.txt
```

## Running it locally (SQLite, zero setup)

```bash
python -m venv venv && source venv/bin/activate   # optional
pip install -r requirements.txt
python db.py             # creates the schema
python seed_data.py      # loads sample data, prints validation results
python reports.py        # generates the CSV reports in reports/
python app.py             # starts the dashboard at http://127.0.0.1:5000
```

## Switching to real PostgreSQL

The schema was designed for PostgreSQL (`schema_postgres.sql`); SQLite is
just the zero-setup default for local development. To run it against real
Postgres:

```bash
pip install psycopg2-binary
createdb taskflow
psql -d taskflow -f schema_postgres.sql
export DATABASE_URL="postgresql://user:password@localhost/taskflow"
```

Then uncomment the two `psycopg2` lines in `db.py`'s `get_connection()`.
Every other file (`validation.py`, `seed_data.py`, `reports.py`, `app.py`)
talks only to `db.py`, so no other code changes are needed.

## Notes

This is a learning/portfolio project built to practice schema design, data
validation, and pandas reporting — not a production system (no auth, no
concurrent-write handling, dev server only).
