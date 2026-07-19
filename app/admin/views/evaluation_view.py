from starlette_admin.exceptions import FormValidationError

from .base_view import BaseModelView


class EvaluationModelView(BaseModelView):
    fields = [
        "id",
        "score",
        "comment",
        "employee",
        "reviewer",
        "task",
        "created_at",
        "updated_at",
    ]

    label = "Evaluations"

    async def validate(self, request, data):
        if not any((data.get("employee"), data.get("reviewer"), data.get("task"))):
            raise FormValidationError(
                errors={
                    "employee": "The Task & User fields are required",
                    "reviewer": "The Task & User fields are required",
                    "task": "The Task & User fields are required",
                }
            )
        elif not (1 <= data.get("score") <= 5):
            raise FormValidationError({"score": "The rating must be from 1 to 5"})
