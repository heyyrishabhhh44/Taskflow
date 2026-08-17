"""
reports.py — generates downloadable productivity reports using pandas.

Produces:
  reports/pending_tasks.csv
  reports/completed_tasks.csv
  reports/overdue_tasks.csv
  reports/productivity_summary.csv   (tasks completed per user, avg turnaround)
"""

import os
from datetime import date
import pandas as pd
import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def load_tasks_df():
    conn = db.get_connection()
    query = """
        SELECT
            t.id, t.title, t.status, t.deadline, t.created_at, t.completed_at,
            p.name AS project, u.username AS assigned_to, pr.name AS priority
        FROM tasks t
        JOIN projects p ON p.id = t.project_id
        JOIN users u ON u.id = t.assigned_to
        JOIN priorities pr ON pr.id = t.priority_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["deadline"] = pd.to_datetime(df["deadline"])
    return df


def generate():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df = load_tasks_df()
    today = pd.Timestamp(date.today())

    pending_df = df[df["status"].isin(["pending", "in_progress"]) & (df["deadline"] >= today)]
    completed_df = df[df["status"] == "completed"]
    overdue_df = df[(df["status"] != "completed") & (df["deadline"] < today)]

    pending_df.to_csv(os.path.join(REPORTS_DIR, "pending_tasks.csv"), index=False)
    completed_df.to_csv(os.path.join(REPORTS_DIR, "completed_tasks.csv"), index=False)
    overdue_df.to_csv(os.path.join(REPORTS_DIR, "overdue_tasks.csv"), index=False)

    # Productivity summary: completed task count and priority mix per user
    overdue_counts = overdue_df.groupby("assigned_to").size().rename("overdue_tasks")

    summary = (
        df.groupby("assigned_to")
        .agg(
            total_tasks=("id", "count"),
            completed_tasks=("status", lambda s: (s == "completed").sum()),
        )
        .join(overdue_counts, how="left")
        .fillna({"overdue_tasks": 0})
        .reset_index()
    )
    summary["overdue_tasks"] = summary["overdue_tasks"].astype(int)
    summary["completion_rate_pct"] = (
        (summary["completed_tasks"] / summary["total_tasks"] * 100).round(1)
    )
    summary.to_csv(os.path.join(REPORTS_DIR, "productivity_summary.csv"), index=False)

    print(f"Pending:   {len(pending_df)} tasks -> reports/pending_tasks.csv")
    print(f"Completed: {len(completed_df)} tasks -> reports/completed_tasks.csv")
    print(f"Overdue:   {len(overdue_df)} tasks -> reports/overdue_tasks.csv")
    print(f"Productivity summary -> reports/productivity_summary.csv")
    print("\n" + summary.to_string(index=False))
    return {
        "pending": pending_df,
        "completed": completed_df,
        "overdue": overdue_df,
        "summary": summary,
    }


if __name__ == "__main__":
    generate()
