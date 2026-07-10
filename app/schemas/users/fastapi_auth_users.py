from fastapi_users import schemas


class UserAuthRead(schemas.BaseUser[int]):
    pass


class UserAuthCreate(schemas.BaseUserCreate):
    pass


class UserAuthUpdate(schemas.BaseUserUpdate):
    pass
