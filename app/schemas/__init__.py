from .evaluation import (
    EvaluationBaseSchema,
    EvaluationResponseSchema,
    AverageEvaluationResponseSchema,
)
from .meetings import (
    MeetingBaseSchema,
    MeetingResponseSchema,
    MeetingCancelSchema,
    MeetingIDSchema,
    MeetingCreateSchema,
    MeetingUpdateSchema,
    MeetingParticipantUpdateSchema,
)
from .tasks import (
    TaskBaseSchema,
    TaskResponseSchema,
    TaskCommentBaseSchema,
    TaskCommentResponseSchema,
    TaskUpdateSchema,
    TaskCommentCreateSchema,
)
from .teams import TeamBaseSchema, TeamResponseSchema, TeamLinkUserSchema
from .users.users import (
    UserBaseSchema,
    UserResponseSchema,
    UserCreateSchema,
    AfterAuthUserSchema,
    UserIDSchema,
    UserMeetingSchema,
    UserResponseAllUsersSchema,
)

MeetingBaseSchema.model_rebuild()
MeetingResponseSchema.model_rebuild()
MeetingCreateSchema.model_rebuild()
MeetingUpdateSchema.model_rebuild()
UserMeetingSchema.model_rebuild()
MeetingParticipantUpdateSchema.model_rebuild()
