from pydantic_core import ValidationError


def pydantic_errors_to_form_errors(e: ValidationError) -> dict:
    errors = {}
    for error in e.errors():
        field = error["loc"][0] if error["loc"] else "__all__"
        if field in errors:
            errors[field] += f"; {error['msg']}"
        else:
            errors[field] = error["msg"]
    return errors
