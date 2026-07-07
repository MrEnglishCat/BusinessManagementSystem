from starlette_admin.contrib.sqla import ModelView


class BaseModelView(ModelView):
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_edit = [
        "created_at",
        "updated_at",
    ]
    fields_default_sort = [("created_at", True)]
    page_size = 20
    page_size_options = [10, 20, 25, 50, 100, -1]
