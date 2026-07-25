from enum import StrEnum


class ServiceTypeEnum(StrEnum):
    TASK_COMMENT = "task_comment"
    TASK = "task"
    EVALUATION = "evaluation"
    MEETING = "meeting"
    TEAM = "team"
    USER = "user"
    INVITE = "invite"


class MeetingStatusEmun(StrEnum):
    PLANNED = "planned"  # только что создана, указано время
    CANCELED = "canceled"  # отменена
    COMPLETED = "completed"  # завершеная встреча, или прошло время
    IN_PROGRESS = (
        "in_progress"  # когда текущее время между началом и окончанием встречи
    )
