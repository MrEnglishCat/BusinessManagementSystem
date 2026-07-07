from .base_view import BaseModelView


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

    label = "Meeting"

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
