"""
app.py — TaskFlow dashboard (Flask).

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request
import reports

app = Flask(__name__)


@app.route("/")
def dashboard():
    data = reports.generate()
    status_filter = request.args.get("status", "all")

    pending = data["pending"]
    completed = data["completed"]
    overdue = data["overdue"]

    if status_filter == "pending":
        shown = pending
    elif status_filter == "completed":
        shown = completed
    elif status_filter == "overdue":
        shown = overdue
    else:
        shown = None  # show all three sections

    return render_template(
        "dashboard.html",
        counts={
            "pending": len(pending),
            "completed": len(completed),
            "overdue": len(overdue),
        },
        summary=data["summary"].to_dict(orient="records"),
        status_filter=status_filter,
        shown=shown.to_dict(orient="records") if shown is not None else None,
        pending_rows=pending.to_dict(orient="records"),
        completed_rows=completed.to_dict(orient="records"),
        overdue_rows=overdue.to_dict(orient="records"),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
