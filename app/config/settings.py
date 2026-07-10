from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    MODE: str

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    BMS_DB_NAME: str
    ADMIN_DB_NAME: str

    SECRET_KEY: str
    SECRET: str

    GENERATE_USERS_COUNT: int
    GENERATE_TEAMS_COUNT: int
    GENERATE_TASKS_COUNT: int
    GENERATE_COMMENTS_PER_TASK_MIN: int
    GENERATE_COMMENTS_PER_TASK_MAX: int
    GENERATE_MEETINGS_COUNT: int
    GENERATE_EVALUATIONS_COUNT: int

    @property
    def BMS_DB_URL(self):

        if self.MODE == "DEBUG":
            return "sqlite:///test.db"

        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.BMS_DB_NAME}"

    @property
    def ADMIN_DB_URL(self):

        if self.MODE == "DEBUG":
            return "sqlite:///test.db"

        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.ADMIN_DB_NAME}"

    @property
    def SYNC_DB_URL(self):

        if self.MODE == "DEBUG":
            return "sqlite:///test.db"

        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.BMS_DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


import secrets

print(secrets.token_urlsafe(64))
