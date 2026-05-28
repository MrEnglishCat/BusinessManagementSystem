from app.config.db import BaseAlchemyModel


class TaskModel(BaseAlchemyModel):
    __tablename__ = "tasks"
