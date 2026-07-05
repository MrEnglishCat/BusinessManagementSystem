from enum import StrEnum


class ServiceTypeEnum(StrEnum):
    task_comment = "task_comment"
    task = "task"
    evaluation = "evaluation"
    meeting = "meeting"
    team = "team"
    user = "user"
