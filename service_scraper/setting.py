import locale

from pydantic import BaseSettings

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


class Settings(BaseSettings):
    REQUESTS_TIMEOUT_SEC: int = 60
    SLEEP_SEC: int = 3
    BATCH_SAVE: int = 100
    HEADERS: dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }


APP_SETTINGS = Settings()
print(APP_SETTINGS.json(indent=4))
