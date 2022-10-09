from base import BaseParser
from datetime import datetime, timedelta
from loguru import logger
from pytz import UTC

class BuhgalteriaParser(BaseParser):

    ARTICLES_BLOCK = "div"
    ARTICLES_ATTR = {"class": "articles"}
    ARTICLE_BLOCK = "article"
    DATE_BLOCK = "span"
    DATE_ATTR = {"class": "newsdate"}
    TEXT_BLOCK = "div"
    TEXT_ATTR = {"class": "text"}
    TITLE_BLOCK = "h1"
    URL_BLOCK = "h3"
    
    @staticmethod
    def _parse_date(date: str) -> datetime:
        """Парсим строчку с созданием времени"""
        date = date.strip().split(sep=",")
        try:
            now = datetime.now()
            date = (
                datetime.strptime(date[0], "%d.%m.%Y")
                + timedelta(hours=now.hour, minutes=now.minute, days=now.day)
            )
        except ValueError:
            article_time = date[1].strip().split(sep=":")
            date_res = (
                datetime.now()
                + timedelta(hours=int(article_time[0]), minutes=int(article_time[1]))
            )
            if date[0] == "Вчера":
                date_res -= timedelta(days=2)
            date = date_res

        return date.replace(tzinfo=UTC)

if __name__ == "__main__":
    buhgalteria_parser = BuhgalteriaParser("https://www.buhgalteria.ru/news/?PAGEN_1=")

    last_bd_time = datetime.now(tz=UTC) - timedelta(days=1)
    first_test = buhgalteria_parser.parse(stop_datetime=last_bd_time)
    min_loaded_date = min([article["post_dttm"] for article in first_test])
    status = "✅" if min_loaded_date > last_bd_time else "❌"
    logger.info(f"Тест №1 - остановимся по времени : {status}")

    page_to_parse = 2
    _ = buhgalteria_parser.parse(max_pages=page_to_parse)
    second_test = buhgalteria_parser.page_parsed
    status = "✅" if page_to_parse == second_test else "❌"
    logger.info(f"Тест №2 - остановимся по страницам : {status}")