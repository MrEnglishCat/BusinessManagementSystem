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

    label = "Evaluation"
