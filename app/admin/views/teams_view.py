from starlette_admin.exceptions import FormValidationError
from starlette_admin import HasMany
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
        "members",
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

    exclude_fields_from_edit = ["creator", "created_by", "created_at", "updated_at"]
    exclude_fields_from_create = ["creator", "created_by", "created_at", "updated_at"]

    async def before_create(self, request, data, team):
        team.created_by = request.state.user.id
        team.invite_code = f"INV-{team.invite_code}"
        return await super().before_create(request, data, team)

    async def before_edit(self, request, data, team):
        if not team.invite_code.startswith("INV-"):
            team.invite_code = f"INV-{team.invite_code}"
        return await super().before_edit(request, data, team)
