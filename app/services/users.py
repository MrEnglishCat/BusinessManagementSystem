from .base import BaseService
from ..repository import UserRepository


class UserService(BaseService):
    repository = UserRepository
