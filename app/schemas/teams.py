from pydantic import BaseModel, Field
from .base import BasePydanticModel, BaseDataTimePydanticModel


class TeamIDSchema(BaseModel):
    id: int = Field(title="Team")


class TeamBaseSchema(BasePydanticModel):
    name: str = Field(title="Name")
    description: str = Field(title="Description")
    invite_code: str = Field(title="Invite code")
    created_by: int = Field(title="Created by")


class TeamResponseSchema(
    BaseDataTimePydanticModel,
    TeamBaseSchema,
    TeamIDSchema,
): ...


class TeamLinkUserSchema(BasePydanticModel):
    username: str = Field(title="Username")
    invite_code: str = Field(
        title="Invite code",
    )


2
