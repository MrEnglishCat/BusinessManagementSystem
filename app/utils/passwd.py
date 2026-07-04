from argon2 import PasswordHasher


def get_password_hash(password: str):
    ph = PasswordHasher()
    return ph.hash(password=password)
