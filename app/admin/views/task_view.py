from .base_view import BaseModelView


class TaskModelView(BaseModelView):
    fields = [
        "id",
        "title",
        "description",
        "status",
        "deadline",
        "creator",
        "assignee",
        "team",
        "created_at",
        "updated_at",
    ]

    label = "Task"

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
        # print("request.state.user", request.user)
        # DEVELOPMENT заполнять поле created_by через реквест и аутентификационные данные авторизованного пользователя.

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
