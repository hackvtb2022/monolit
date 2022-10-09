import locale
from datetime import datetime, timedelta

from base import BaseParser
from loguru import logger
from pytz import UTC


class NalogovedParser(BaseParser):

    ARTICLES_BLOCK = "div"
    ARTICLES_ATTR = {"class": "pubs-list"}
    ARTICLE_BLOCK = "div"
    ARTICLE_ATTR = {"class": "news-list"}
    DATE_BLOCK = "div"
    DATE_ATTR = {"class": "date"}
    TEXT_BLOCK = "div"
    TEXT_ATTR = {"class": "html"}
    TITLE_BLOCK = "h1"

    @staticmethod
    def _parse_date(date: str) -> datetime:
        """Парсим строчку с созданием времени"""
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
        return datetime.strptime(date, "%d, %B %Y").replace(tzinfo=UTC)


if __name__ == "__main__":
    nalogoved_parser = NalogovedParser("https://nalogoved.ru/news?page=")

    last_bd_time = datetime.now(tz=UTC) - timedelta(days=3)
    first_test = nalogoved_parser.parse(stop_datetime=last_bd_time)
    min_loaded_date = min([article["post_dttm"] for article in first_test])
    status = "✅" if min_loaded_date > last_bd_time else "❌"
    logger.info(f"Тест №1 - остановимся по времени : {status}")

    page_to_parse = 2
    _ = nalogoved_parser.parse(max_pages=page_to_parse)
    second_test = nalogoved_parser.page_parsed
    status = "✅" if page_to_parse == second_test else "❌"
    logger.info(f"Тест №2 - остановимся по страницам : {status}")
