"""
validation.py — input validation for TaskFlow.

This is the "applied filtering and input validation to improve data quality"
part of the project. Every function returns (is_valid: bool, errors: list[str])
instead of raising, so callers (seed_data.py, a future API layer, etc.) can
decide how to handle bad records — e.g. log-and-skip during a bulk import,
which is exactly what seed_data.py does.
"""

from datetime import datetime

ALLOWED_STATUSES = {"pending", "in_progress", "completed"}
MAX_TITLE_LEN = 150


def validate_username(username):
    errors = []
    if not username or not username.strip():
        errors.append("username is required")
    elif len(username) > 50:
        errors.append("username must be 50 characters or fewer")
    return (len(errors) == 0, errors)


def validate_email(email):
    errors = []
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        errors.append(f"'{email}' is not a valid email address")
    return (len(errors) == 0, errors)


def validate_task(title, deadline_str, priority_name, status, existing_project_ids, existing_user_ids, project_id, assigned_to, valid_priorities):
    """
    Validate a task record before insert.
    deadline_str is expected in 'YYYY-MM-DD' format.
    """
    errors = []

    if not title or not title.strip():
        errors.append("title is required")
    elif len(title) > MAX_TITLE_LEN:
        errors.append(f"title exceeds {MAX_TITLE_LEN} characters")

    if status not in ALLOWED_STATUSES:
        errors.append(f"status '{status}' is not one of {sorted(ALLOWED_STATUSES)}")

    try:
        datetime.strptime(deadline_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        errors.append(f"deadline '{deadline_str}' is not a valid YYYY-MM-DD date")

    if priority_name not in valid_priorities:
        errors.append(f"priority '{priority_name}' is not one of {sorted(valid_priorities)}")

    if project_id not in existing_project_ids:
        errors.append(f"project_id {project_id} does not exist")

    if assigned_to not in existing_user_ids:
        errors.append(f"assigned_to user id {assigned_to} does not exist")

    return (len(errors) == 0, errors)
