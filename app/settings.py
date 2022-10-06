from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_DB: str

    @property
    def DB_PG_URL(self):
        return {
            "dbname": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD.get_secret_value(),
            "host": self.POSTGRES_HOST,
        }

    @property
    def DB_SQLALCHEMY_DATABASE_URL(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        )


APP_SETTINGS = Settings()
print(APP_SETTINGS.json(indent=4))
