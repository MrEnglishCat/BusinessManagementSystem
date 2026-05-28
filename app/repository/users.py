from .base_repository import BaseRepository
from ..models.users import UserModel


class UserRepository(BaseRepository):

    model = UserModel
