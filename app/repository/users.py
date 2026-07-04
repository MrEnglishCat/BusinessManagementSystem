from .base_repository import BaseRepository
from ..models import UserModel


class UserRepository(BaseRepository):
    model = UserModel
