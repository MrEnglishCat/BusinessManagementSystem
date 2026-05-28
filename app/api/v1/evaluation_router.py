from fastapi import APIRouter, Depends, Body, status

from app.config.response import ResponseFactory, ResponseOk, ResponseError
from app.schemas.evaluation import EvaluationResponseSchema, EvaluationSchema

evaluation_router = APIRouter(prefix="/evaluations", tags=["evaluations"])
MOCK_EVALUATIONS = [
    {"id": 1, "name": "Оценка 1", "score": 85, "status": "completed"},
    {"id": 2, "name": "Оценка 2", "score": 92, "status": "completed"},
    {"id": 3, "name": "Оценка 3", "score": 78, "status": "pending"},
]


def get_evaluations_depends():
    return MOCK_EVALUATIONS


@evaluation_router.get("/", response_model=ResponseOk)
async def get_evaluations(evaluations: list[dict] = Depends(get_evaluations_depends)):
    return ResponseFactory.ok(data=evaluations)


@evaluation_router.get("/{evaluation_id}", response_model=ResponseOk | ResponseError)
async def get_evaluation_by_id(evaluation_id: int):

    evaluation = next((e for e in MOCK_EVALUATIONS if e["id"] == evaluation_id), None)

    if not evaluation:
        return ResponseFactory.error(
            message=f"Evaluation with id {evaluation_id} not found",
            errors=[{"type": "not_found", "id": evaluation_id}],
        )

    return ResponseFactory.ok(
        data=evaluation, message=f"Evaluation {evaluation_id} found"
    )


@evaluation_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ResponseOk | ResponseError
)
async def create_evaluation(evaluation: EvaluationSchema = Body(EvaluationSchema)):

    if not evaluation:
        return ResponseFactory.error(
            message=f"Evaluation with  not found",
            errors=[
                {
                    "type": "not_found",
                }
            ],
        )

    return ResponseFactory.ok(data=evaluation, message=f"Evaluation  created")
