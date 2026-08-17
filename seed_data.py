"""
seed_data.py — populates TaskFlow with realistic sample data.

Also feeds a handful of deliberately invalid records through validation.py
to demonstrate that bad data actually gets caught and rejected, not just
silently written to the database. Run this after db.py has initialized
the schema.
"""

from datetime import date, timedelta
import db
import validation

USERS = [
    ("rgupta", "rgupta@example.com"),
    ("aiyer", "aiyer@example.com"),
    ("skhan", "skhan@example.com"),
    ("pverma", "pverma@example.com"),
]

PROJECTS = [
    ("Website Redesign", "Revamp the marketing site UI/UX", 1),
    ("Data Pipeline Migration", "Move batch jobs to a new ETL stack", 2),
    ("Q3 Analytics Report", "Prepare quarterly performance analysis", 3),
]

today = date.today()

# (title, days_from_today_for_deadline, priority, status, project_idx, assigned_to_idx)
GOOD_TASKS = [
    ("Draft homepage wireframe", 5, "Medium", "pending", 0, 1),
    ("Set up staging environment", -3, "High", "in_progress", 0, 2),   # overdue, still open
    ("Migrate users table to new schema", 10, "High", "pending", 1, 3),
    ("Write ETL unit tests", -1, "Medium", "completed", 1, 1),          # completed, deadline passed
    ("Collect Q3 raw metrics", 2, "High", "in_progress", 2, 4),
    ("Build revenue trend chart", 7, "Low", "pending", 2, 2),
    ("Review copy for landing page", -5, "Low", "pending", 0, 3),       # overdue
    ("Deploy pipeline to prod", 14, "High", "pending", 1, 4),
    ("Finalize Q3 report summary", 4, "Medium", "completed", 2, 1),
    ("Fix broken nav on mobile", -2, "High", "completed", 0, 2),
]

# Records that SHOULD fail validation — proves the guardrails actually work.
BAD_TASKS = [
    dict(title="", deadline="2026-09-01", priority="Medium", status="pending", project_id=1, assigned_to=1),
    dict(title="Task with bad date", deadline="not-a-date", priority="Low", status="pending", project_id=1, assigned_to=1),
    dict(title="Task with bad status", deadline="2026-09-01", priority="Low", status="archived", project_id=1, assigned_to=1),
    dict(title="Task with bad priority", deadline="2026-09-01", priority="Urgent!!", status="pending", project_id=1, assigned_to=1),
    dict(title="Task with unknown project", deadline="2026-09-01", priority="Low", status="pending", project_id=999, assigned_to=1),
]


def run():
    conn = db.get_connection()
    cur = conn.cursor()

    print("Inserting users...")
    for username, email in USERS:
        ok, errors = validation.validate_username(username)
        ok2, errors2 = validation.validate_email(email)
        if not (ok and ok2):
            print(f"  SKIPPED user {username}: {errors + errors2}")
            continue
        cur.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
    conn.commit()

    print("Inserting projects...")
    for name, desc, owner_id in PROJECTS:
        cur.execute(
            "INSERT INTO projects (name, description, owner_id) VALUES (?, ?, ?)",
            (name, desc, owner_id),
        )
    conn.commit()

    # Lookups needed for validation
    priority_rows = cur.execute("SELECT id, name FROM priorities").fetchall()
    priority_id_by_name = {row["name"]: row["id"] for row in priority_rows}
    valid_priorities = set(priority_id_by_name.keys())
    existing_project_ids = {row["id"] for row in cur.execute("SELECT id FROM projects").fetchall()}
    existing_user_ids = {row["id"] for row in cur.execute("SELECT id FROM users").fetchall()}

    print("Inserting valid tasks...")
    inserted = 0
    for title, offset, priority, status, proj_idx, user_idx in GOOD_TASKS:
        deadline = (today + timedelta(days=offset)).isoformat()
        project_id = proj_idx + 1
        assigned_to = user_idx
        ok, errors = validation.validate_task(
            title, deadline, priority, status,
            existing_project_ids, existing_user_ids,
            project_id, assigned_to, valid_priorities,
        )
        if not ok:
            print(f"  SKIPPED '{title}': {errors}")
            continue
        completed_at = deadline if status == "completed" else None
        cur.execute(
            """INSERT INTO tasks (project_id, assigned_to, title, priority_id, status, deadline, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, assigned_to, title, priority_id_by_name[priority], status, deadline, completed_at),
        )
        inserted += 1
    conn.commit()
    print(f"  {inserted}/{len(GOOD_TASKS)} valid tasks inserted.")

    print("\nAttempting to insert deliberately BAD tasks (should all be rejected)...")
    rejected = 0
    for bad in BAD_TASKS:
        ok, errors = validation.validate_task(
            bad["title"], bad["deadline"], bad["priority"], bad["status"],
            existing_project_ids, existing_user_ids,
            bad["project_id"], bad["assigned_to"], valid_priorities,
        )
        if not ok:
            rejected += 1
            print(f"  REJECTED: {bad} -> {errors}")
        else:
            print(f"  WARNING: bad record unexpectedly passed validation: {bad}")

    print(f"\n{rejected}/{len(BAD_TASKS)} bad records correctly rejected before reaching the database.")
    conn.close()


if __name__ == "__main__":
    run()
