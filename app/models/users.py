from app.config.db import BaseAlchemyModel


class UserModel(BaseAlchemyModel):
    __tablename__ = "users"
