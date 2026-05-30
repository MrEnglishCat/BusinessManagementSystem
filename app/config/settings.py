from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    MODE: str

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    @property
    def DB_URL(self):

        if self.MODE == "DEBUG":
            return "sqlite:///test.db"

        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_DB_URL(self):

        if self.MODE == "DEBUG":
            return "sqlite:///test.db"

        return f"postgresql+psycopg2://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
