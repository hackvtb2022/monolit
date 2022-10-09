from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_DB: str
    SPIDER_WAIT_TIMEOUT_SEC: int = 60 * 60 * 1  # каждый час
    SPIDER_PERIOD_DAYS: int = 1

    @property
    def DB_SQLALCHEMY_DATABASE_URL(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        )


APP_SETTINGS = Settings()
print(APP_SETTINGS.json(indent=4))
