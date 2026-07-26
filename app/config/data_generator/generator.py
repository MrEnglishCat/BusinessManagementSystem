import asyncio
import random
import secrets
from datetime import datetime, timedelta, UTC
from mimesis import Person, Address, Text, Datetime, Finance, Code
from mimesis.locales import Locale
from app.config.settings import settings
import argon2
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    UserModel,
    TeamModel,
    TaskModel,
    TaskCommentModel,
    MeetingModel,
    EvaluationModel,
    meeting_participants,
    TaskStatus,
)
from app.utils.enums_service import UserRole

from app.schemas.users.users import UserResponseSchema

# Провайдеры Mimesis
person = Person(locale=Locale.RU)
address = Address(locale=Locale.RU)
text = Text(locale=Locale.RU)
dt = Datetime()
finance = Finance(locale=Locale.RU)
code = Code()

passwd_hasher = argon2.PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    hash_len=64,
    salt_len=16,
)


def generate_invite_code() -> str:
    token = secrets.token_urlsafe(6).upper()[:6]
    return f"INV-{token}"


from sqlalchemy import select


async def generate_users(
    session: AsyncSession, count: int = settings.GENERATE_USERS_COUNT
) -> list[UserModel]:
    users = []
    used_emails = set()
    used_usernames = set()

    admin_user = None
    result = await session.execute(
        select(UserModel).where(UserModel.username == "admin")
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        admin_user = existing_admin
    else:
        admin_user = UserModel(
            email="admin@admin.admin",
            username="admin",
            hashed_password=passwd_hasher.hash("admin"),
            full_name="Системный Администратор",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            team_id=None,
        )
        users.append(admin_user)

    used_emails.add("admin@admin.admin")
    used_usernames.add("admin")

    for _ in range(count):
        email = person.email()
        while email in used_emails:
            email = person.email()
        used_emails.add(email)

        username = person.username()
        while username in used_usernames:
            username = person.username()
        used_usernames.add(username)

        role = random.choice([UserRole.USER, UserRole.MANAGER, UserRole.ADMIN])
        user = UserModel(
            email=email,
            username=username,
            hashed_password=passwd_hasher.hash(person.password(length=12)),
            full_name=person.full_name(),
            role=role,
            is_active=random.choice([True, True, True, False]),
            team_id=None,
        )
        users.append(user)

    if users:
        session.add_all(users)
        await session.commit()
        await session.flush()

    if existing_admin:
        all_users_result = await session.execute(select(UserModel))
        all_users = all_users_result.scalars().all()
        return [UserResponseSchema.model_validate(user) for user in all_users]

    return [UserResponseSchema.model_validate(user) for user in users]


async def generate_teams(
    session: AsyncSession, users: list[UserModel], count: int
) -> list[TeamModel]:
    teams = []
    used_names = set()

    for _ in range(count):
        name = f"{finance.company()} Team"
        while name in used_names:
            name = f"{finance.company()} Team"
        used_names.add(name)

        creator = random.choice(users)
        team = TeamModel(
            name=name,
            description=text.text(quantity=3),
            invite_code=generate_invite_code(),
            created_by=creator.id,
        )
        teams.append(team)

    session.add_all(teams)
    await session.flush()

    for user in users:
        if user.is_superuser:
            continue

        if random.random() < 0.6:
            team = random.choice(teams)
            user.team_id = team.id

    await session.flush()
    return teams


async def generate_tasks(
    session: AsyncSession, users: list[UserModel], teams: list[TeamModel], count: int
) -> list[TaskModel]:
    tasks = []
    statuses = list(TaskStatus)

    for _ in range(count):
        creator = random.choice(users)

        assignee = random.choice(users) if random.random() < 0.8 else None
        team = random.choice(teams) if random.random() < 0.5 else None
        deadline = None
        if random.random() < 0.7:
            deadline = datetime.now(UTC) + timedelta(days=random.randint(-30, 60))

        task = TaskModel(
            title=text.sentence(),
            description=text.text(quantity=3),
            status=random.choice(statuses),
            deadline=deadline,
            created_by=creator.id,
            assignee_id=assignee.id if assignee else None,
            team_id=team.id if team else None,
        )
        tasks.append(task)

    session.add_all(tasks)
    await session.flush()
    return tasks


async def generate_comments(
    session: AsyncSession,
    tasks: list[TaskModel],
    users: list[UserModel],
    min_comments: int = settings.GENERATE_COMMENTS_PER_TASK_MIN,
    max_comments: int = settings.GENERATE_COMMENTS_PER_TASK_MAX,
):
    comments = []
    for task in tasks:
        num = random.randint(min_comments, max_comments)

        for _ in range(num):
            user = random.choice(users)
            comment = TaskCommentModel(
                content=text.text(quantity=3),
                task_id=task.id,
                user_id=user.id,
                created_at=datetime.now(UTC) - timedelta(days=random.randint(0, 30)),
            )
            comments.append(comment)

    session.add_all(comments)
    await session.flush()


async def generate_meetings(
    session: AsyncSession, users: list[UserModel], teams: list[TeamModel], count: int
) -> list[MeetingModel]:
    meetings = []
    for _ in range(count):
        creator = random.choice(users)
        team = random.choice(teams) if random.random() < 0.5 else None

        start = datetime.now(UTC) + timedelta(days=random.randint(-60, 60))
        end = start + timedelta(hours=random.randint(1, 4))

        meeting = MeetingModel(
            title=text.sentence()[:255],
            description=text.text(quantity=3),
            start_time=start,
            end_time=end,
            location=address.address() if random.random() < 0.5 else None,
            created_by=creator.id,
            team_id=team.id if team else None,
        )
        meetings.append(meeting)

    session.add_all(meetings)
    await session.flush()

    for meeting in meetings:
        participants = random.sample(users, k=random.randint(1, min(10, len(users))))
        for user in participants:
            await session.execute(
                meeting_participants.insert().values(
                    meeting_id=meeting.id, user_id=user.id
                )
            )

    return meetings


async def generate_evaluations(
    session: AsyncSession, users: list, tasks: list, count: int
):
    if not tasks:
        return []

    evaluations_to_add = []

    fake_comments = [
        "Отличная работа, код чистый и хорошо структурирован.",
        "Задача выполнена в срок, замечаний нет.",
        "Есть небольшие замечания по архитектуре, требуется рефакторинг.",
        "Превосходный результат, превзошел ожидания!",
        "Слабое понимание требований, необходимо доработать.",
        "Хорошая работа, но не хватает unit-тестов.",
        "Комментарий отсутствует, но работа принята.",
    ]

    for _ in range(count):
        random_task = random.choice(tasks)

        employee = random.choice(users)
        reviewer = random.choice(users)
        score = random.randint(1, 5)

        evaluation = EvaluationModel(
            score=score,
            comment=random.choice(fake_comments),
            employee_id=employee.id,
            reviewer_id=reviewer.id,
            task_id=random_task.id,
        )
        evaluations_to_add.append(evaluation)

    session.add_all(evaluations_to_add)
    await session.flush()
    return evaluations_to_add


async def run_generate(
    session: AsyncSession,
    users_count: int | None = None,
    teams_count: int | None = None,
    tasks_count: int | None = None,
    meetings_count: int | None = None,
    evaluations_count: int | None = None,
    comments_per_task_min: int | None = None,
    comments_per_task_max: int | None = None,
):
    _users_count = (
        users_count if users_count is not None else settings.GENERATE_USERS_COUNT
    )
    _teams_count = (
        teams_count if teams_count is not None else settings.GENERATE_TEAMS_COUNT
    )
    _tasks_count = (
        tasks_count if tasks_count is not None else settings.GENERATE_TASKS_COUNT
    )
    _meetings_count = (
        meetings_count
        if meetings_count is not None
        else settings.GENERATE_MEETINGS_COUNT
    )
    _evaluations_count = (
        evaluations_count
        if evaluations_count is not None
        else settings.GENERATE_EVALUATIONS_COUNT
    )
    _comments_min = (
        comments_per_task_min
        if comments_per_task_min is not None
        else settings.GENERATE_COMMENTS_PER_TASK_MIN
    )
    _comments_max = (
        comments_per_task_max
        if comments_per_task_max is not None
        else settings.GENERATE_COMMENTS_PER_TASK_MAX
    )

    users = await generate_users(session, _users_count)
    teams = await generate_teams(session, users, _teams_count)
    tasks = await generate_tasks(session, users, teams, _tasks_count)
    await generate_comments(session, tasks, users, _comments_min, _comments_max)
    await generate_meetings(session, users, teams, _meetings_count)
    await generate_evaluations(session, users, tasks, _evaluations_count)
    await session.commit()
