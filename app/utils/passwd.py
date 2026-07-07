from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


def get_password_hash(password: str):
    ph = PasswordHasher()
    return ph.hash(password=password)


def verify_password(hash_password: str, password: str):
    ph = PasswordHasher()
    try:
        ph.verify(hash_password, password)
        return True
    except VerifyMismatchError:
        return False
