import locale
from datetime import datetime, timedelta

from loguru import logger
from pytz import UTC

from service_scraper.spiders.base import BaseParser


class ExpertParser(BaseParser):

    ARTICLES_BLOCK = "div"
    ARTICLES_ATTR = {"class": "modular-grid"}
    ARTICLE_BLOCK = "article"
    DATE_BLOCK = "span"
    DATE_ATTR = {"class": "description"}
    TEXT_BLOCK = "div"
    TEXT_ATTR = {"class": "content-text"}
    TITLE_BLOCK = "h1"
    URL_BLOCK = "h2"

    @staticmethod
    def _parse_date(date: str) -> datetime:
        """Парсим строчку с созданием времени"""
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
        return datetime.strptime(date, "%d %B %Y, %H:%M").replace(tzinfo=UTC)


if __name__ == "__main__":
    expert_parser = ExpertParser("https://expert.ru/ekonomika/")
    last_bd_time = datetime.now(tz=UTC) - timedelta(days=3)
    first_test = expert_parser.parse(stop_datetime=last_bd_time)
    min_loaded_date = min([article["post_dttm"] for article in first_test])
    status = "✅" if min_loaded_date > last_bd_time else "❌"
    logger.info(f"Тест №1 - остановимся по времени : {status}")

    page_to_parse = 2
    _ = expert_parser.parse(max_pages=page_to_parse)
    second_test = expert_parser.page_parsed
    status = "✅" if page_to_parse == second_test else "❌"
    logger.info(f"Тест №2 - остановимся по страницам : {status}")
