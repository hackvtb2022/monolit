import locale
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger
from pytz import UTC

from service_scraper.spiders.base import BaseParser


class LentaParser(BaseParser):
    ARTICLES_BLOCK = "div"
    ARTICLES_ATTR = {"class": "rubric-page"}
    ARTICLE_BLOCK = "li"
    ARTICLE_ATTR = {"class": "rubric-page__item _news"}
    DATE_BLOCK = "time"
    DATE_ATTR = {"class": "topic-header__time"}
    TEXT_BLOCK = "div"
    TEXT_ATTR = {"class": "topic-body__content"}
    TITLE_BLOCK = "span"
    TITLE_ATTR = {"class": "topic-body__title"}

    @staticmethod
    def _parse_date(date) -> datetime:
        """Парсим строчку с созданием времени"""
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
        return datetime.strptime(date, "%H:%M, %d %B %Y").replace(tzinfo=UTC)

    def parse(
        self,
        max_pages: int = None,
        start_page: int = 1,
        stop_datetime: Optional[datetime] = None,
    ):
        """Точка запуска парсера"""
        stop_datetime = stop_datetime.replace(tzinfo=UTC) if stop_datetime else None
        assert (
            stop_datetime is not None or max_pages is not None
        ), "Нужно задать ограничения на парсинг"

        result = []
        previous_min_dt = None
        self.page_parsed = 0
        page_number = start_page
        while True:
            logger.info(f"Scraping page №{page_number} ...")
            data, is_breaked = self._parse_page(page_number, stop_datetime)
            if is_breaked:
                # мы дошли до новости, которая по времени уже есть в БД
                result.extend(data)
                break

            min_published_dt = min(data).post_dttm
            if previous_min_dt and previous_min_dt < min_published_dt:
                # Мы увеличиваем пэйджи, но с какого-то номера нам всегда выдают 1-ый
                break
            result.extend(data)
            page_number += 1
            self.page_parsed += 1
            previous_min_dt = min_published_dt

            if max_pages and page_number == start_page + max_pages:
                # Мы прошли максимальное число страниц
                break
        return list(map(asdict, result))


if __name__ == "__main__":
    lenta_parser = LentaParser("https://lenta.ru/rubrics/economics/investments/")

    last_bd_time = datetime.now() - timedelta(days=3)
    first_test = lenta_parser.parse(stop_datetime=last_bd_time)
    min_loaded_date = min([article["post_dttm"] for article in first_test])
    status = "✅" if min_loaded_date > last_bd_time else "❌"
    logger.info(f"Тест №1 - остановимся по времени : {status}")

    page_to_parse = 2
    _ = lenta_parser.parse(max_pages=page_to_parse)
    second_test = lenta_parser.page_parsed
    status = "✅" if page_to_parse == second_test else "❌"
    logger.info(f"Тест №2 - остановимся по страницам : {status}")

    last_bd_time = datetime(2021, 10, 4, tzinfo=UTC)
    _ = lenta_parser.parse(stop_datetime=last_bd_time)
    third_test = lenta_parser.page_parsed
    status = "✅" if third_test < 10 else "❌"
    logger.info(f"Тест №3 - остановились - закончился feed : {status}")
