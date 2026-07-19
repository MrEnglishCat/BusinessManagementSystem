from starlette_admin.exceptions import FormValidationError

from .base_view import BaseModelView
from starlette_admin import HasMany


class TaskModelView(BaseModelView):
    fields = [
        "id",
        "title",
        "description",
        "status",
        "deadline",
        "creator",
        "team",
        "assignee",
        "comments",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_edit = [
        "comments",
        "created_at",
        "updated_at",
        "creator",
        "team",
    ]
    exclude_fields_from_create = [
        "comments",
        "created_at",
        "updated_at",
        "creator",
        "team",
    ]
    label = "Tasks"

    searchable_fields = [
        "id",
        "title",
        "description",
        "status",
        "deadline",
        "created_at",
        "updated_at",
    ]

    async def before_create(self, request, data, task):
        task.created_by = request.state.user.id
        return await super().before_create(request, data, task)


class TaskCommentModelView(BaseModelView):
    fields = [
        "id",
        "content",
        "task",
        "user",
        "created_at",
        "updated_at",
    ]
    label = "Task comments"

    searchable_fields = [
        "id",
        "content",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]

    async def validate(self, request, data):
        if not any((data.get("task"), data.get("user"))):
            raise FormValidationError(
                errors={
                    "task": "The Task & User fields are required",
                    "user": "The Task & User fields are required",
                }
            )
        return await super().validate(request, data)
