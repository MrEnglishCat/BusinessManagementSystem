from starlette_admin.exceptions import FormValidationError
from typing import Any
from email_validator import validate_email, EmailSyntaxError
from .base_view import BaseModelView


class TeamView(BaseModelView):

    fields = [
        "id",
        "name",
        "description",
        "invite_code",
        "creator",
        "created_at",
        "updated_at",
    ]
    label = "Teams"
    searchable_fields = [
        "id",
        "name",
        "description",
        "invite_code",
        "created_by",
        "created_at",
        "updated_at",
    ]
