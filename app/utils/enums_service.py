from enum import StrEnum


class ServiceTypeEnum(StrEnum):
    TASK_COMMENT = "task_comment"
    TASK = "task"
    EVALUATION = "evaluation"
    MEETING = "meeting"
    TEAM = "team"
    USER = "user"
