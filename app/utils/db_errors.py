import re
from typing import Optional
from sqlalchemy.exc import IntegrityError, DataError, OperationalError

from psycopg2.errors import (
    UniqueViolation,
    NotNullViolation,
    ForeignKeyViolation,
    CheckViolation,
    StringDataRightTruncation,
    NumericValueOutOfRange,
)

CONSTRAINT_MAP = {
    # unique
    "users_email_key": ("email", "A user with this email already exists"),
    "users_username_key": ("username", "This login is already taken."),
    "teams_invite_code_key": ("invite_code", "This invitation code is already in use."),
    # check
    "users_role_check": ("role", "Invalid role value"),
    "tasks_score_check": ("score", "The rating must be from 1 to 5"),
    # foreign key
    "tasks_team_id_fkey": ("team_id", "Command not found"),
    "tasks_created_by_fkey": ("created_by", "User not found"),
}


def parse_integrity_error(exc: IntegrityError) -> tuple[int, dict[str, str]]:
    """
    Returns:
        (status_code, errors_dict)
        Example: (409, {"email": "A user with this email already exists."})
    """

    orig = getattr(exc, "orig", None) or exc.__cause__
    message = str(orig) if orig else str(exc)

    if isinstance(orig, UniqueViolation):
        constraint = _extract_constraint_name(message)
        if constraint and constraint in CONSTRAINT_MAP:
            field, msg = CONSTRAINT_MAP[constraint]
            return 409, {field: msg}

        field = _extract_field_from_unique(message)
        return 409, {field: f"The value in field '{field}' already exists"}

    if isinstance(orig, NotNullViolation):
        field = _extract_column_name(message)
        return 422, {field: f"Field '{field}' is required."}

    if isinstance(orig, ForeignKeyViolation):
        constraint = _extract_constraint_name(message)
        if constraint and constraint in CONSTRAINT_MAP:
            field, msg = CONSTRAINT_MAP[constraint]
            return 422, {field: msg}

        field, ref_table = _extract_fk_details(message)
        return 422, {field: f"No related entry found in '{ref_table}'"}

    if isinstance(orig, CheckViolation):
        constraint = _extract_constraint_name(message)
        if constraint and constraint in CONSTRAINT_MAP:
            field, msg = CONSTRAINT_MAP[constraint]
            return 422, {field: msg}
        return 422, {"__all__": "No related entry found in '{ref_table}'"}

    return 500, {"__all__": "Database error"}


def _extract_constraint_name(message: str) -> Optional[str]:
    """
    Example: 'duplicate key value violates unique constraint "users_email_key"'
    """
    match = re.search(r'constraint "([^"]+)"', message)
    return match.group(1) if match else None


def _extract_column_name(message: str) -> str:
    """
    Example: col name: 'null value in column "email" of relation "users"'
    """
    match = re.search(r'column "([^"]+)"', message)
    return match.group(1) if match else "__all__"


def _extract_field_from_unique(message: str) -> str:
    """
    unique field
    example: 'Key (email)=(test@test.com) already exists.'
    """

    match = re.search(r"Key \(([^)]+)\)=", message)
    if match:
        return match.group(1).split(",")[0].strip()

    constraint = _extract_constraint_name(message)
    if constraint:
        parts = constraint.replace("_key", "").split("_", 1)
        if len(parts) > 1:
            return parts[1]

    return "__all__"


def _extract_fk_details(message: str) -> tuple[str, str]:
    """
    FK violation.
    Example: '...key (user_id)=(999) is not present in table "users"'
    """
    field_match = re.search(r"Key \(([^)]+)\)=", message)
    table_match = re.search(r'table "([^"]+)"', message)

    field = field_match.group(1) if field_match else "__all__"
    ref_table = table_match.group(1) if table_match else "unknown"

    return field, ref_table


def handle_integrity_error(exc: IntegrityError) -> str:
    """Парсит IntegrityError и возвращает понятное сообщение"""
    error_msg = str(exc.orig)

    constraint_match = re.search(r'constraint "([^"]+)"', error_msg)
    if not constraint_match:
        return "Integrity data error"

    constraint = constraint_match.group(1)

    messages = {
        "teams_created_by_fkey": (
            "Cannot delete user: they are a team creator. "
            "Delete or reassign teams first."
        ),
        "tasks_created_by_fkey": (
            "Cannot delete user: they created tasks. " "Delete or reassign tasks first."
        ),
        "tasks_assignee_id_fkey": (
            "Cannot delete user: tasks are assigned to them. "
            "Delete or reassign tasks first."
        ),
        "evaluations_employee_id_fkey": (
            "Cannot delete user: they participate in evaluations. "
            "Delete related records first."
        ),
        "evaluations_reviewer_id_fkey": (
            "Cannot delete user: they conducted evaluations. "
            "Delete related records first."
        ),
    }

    return messages.get(
        constraint,
        f"Cannot delete a record: it is in use in other tables (constraint: {constraint})",
    )
