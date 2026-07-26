from pydantic import BaseModel, Field


class GenerateDataRequest(BaseModel):
    users_count: int | None = Field(
        default=None, ge=0, le=10000, description="Количество пользователей"
    )
    teams_count: int | None = Field(
        default=None, ge=0, le=1000, description="Количество команд"
    )
    tasks_count: int | None = Field(
        default=None, ge=0, le=10000, description="Количество задач"
    )
    meetings_count: int | None = Field(
        default=None, ge=0, le=1000, description="Количество встреч"
    )
    evaluations_count: int | None = Field(
        default=None, ge=0, le=10000, description="Количество оценок"
    )
    comments_per_task_min: int | None = Field(
        default=None, ge=0, le=50, description="Мин. комментариев на задачу"
    )
    comments_per_task_max: int | None = Field(
        default=None, ge=0, le=50, description="Макс. комментариев на задачу"
    )
