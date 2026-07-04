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
    UserRole,
    TaskStatus,
)

from app.schemas.users import UserResponseSchema

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


async def generate_users(
    session: AsyncSession, count: int = settings.GENERATE_USERS_COUNT
) -> list[UserModel]:
    users = []
    used_emails = set()
    used_usernames = set()

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
            password=passwd_hasher.hash(person.password(length=12)),
            full_name=person.full_name(),
            role=role,
            is_active=random.choice([True, True, True, False]),
            team_id=None,
        )
        users.append(user)

    session.add_all(users)
    await session.commit()
    await session.flush()
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
        if random.random() < 0.6:
            team = random.choice(teams)
            user.team_id = team.id

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
    session: AsyncSession, tasks: list[TaskModel], users: list[UserModel]
):
    comments = []
    for task in tasks:
        num = random.randint(
            settings.GENERATE_COMMENTS_PER_TASK_MIN,
            settings.GENERATE_COMMENTS_PER_TASK_MAX,
        )
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
    session: AsyncSession, users: list[UserModel], tasks: list[TaskModel], count: int
):
    evaluations = []
    for _ in range(count):
        employee = random.choice(users)
        available_reviewers = [u for u in users if u.id != employee.id]
        if not available_reviewers:
            continue

        reviewer = random.choice(available_reviewers)
        task = random.choice(tasks) if random.random() < 0.6 else None

        ev = EvaluationModel(
            score=random.randint(1, 5),
            comment=text.text(quantity=3) if random.random() < 0.5 else None,
            employee_id=employee.id,
            reviewer_id=reviewer.id,
            task_id=task.id if task else None,
        )
        evaluations.append(ev)

    session.add_all(evaluations)
    await session.flush()


async def run_generate(session: AsyncSession):
    users = await generate_users(session, settings.GENERATE_USERS_COUNT)
    teams = await generate_teams(session, users, settings.GENERATE_TEAMS_COUNT)
    tasks = await generate_tasks(session, users, teams, settings.GENERATE_TASKS_COUNT)
    await generate_comments(session, tasks, users)
    await generate_meetings(session, users, teams, settings.GENERATE_MEETINGS_COUNT)
    await generate_evaluations(
        session, users, tasks, settings.GENERATE_EVALUATIONS_COUNT
    )
    await session.commit()
