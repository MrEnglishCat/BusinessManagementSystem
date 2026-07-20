from .base_view import BaseModelView


# DEVELOPMENT добавить возможность добавления участников митинга. По выбранной команде. Добавить возможность создавать общий митинг для любых участников.
class MeetingModelView(BaseModelView):
    fields = [
        "id",
        "title",
        "description",
        "start_time",
        "end_time",
        "location",
        "creator",
        "team",
        "created_at",
        "updated_at",
    ]

    label = "Meetings"

    searchable_fields = [
        "id",
        "title",
        "description",
        "start_time",
        "end_time",
        "location",
        "creator",
        "team",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_create = [
        "creator",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_edit = [
        "creator",
        "created_at",
        "updated_at",
    ]

    async def before_create(self, request, data, meeting) -> None:
        meeting.created_by = request.state.user.id
