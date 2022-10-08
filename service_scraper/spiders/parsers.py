from datetime import datetime, timedelta
from typing import Callable, Optional
from uuid import uuid4

import pytz
import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin

utc = pytz.UTC


RU_MONTH_VALUES = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


url_1 = "https://www.buhgalteria.ru/news/?PAGEN_1="
url_2 = "https://nalogoved.ru/news?page="
url_3 = "https://www.audit-it.ru/news/account/"

d = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


# парси каждую новость
def date_parse(date: str) -> datetime:
    date = date.strip().split(sep=",")
    try:
        now = datetime.now()
        date = datetime.strptime(date[0], "%d.%m.%Y") + timedelta(
            hours=now.hour, minutes=now.minute, days=now.day
        )
    except ValueError:
        article_time = date[1].strip().split(sep=":")
        date_res = datetime.now() + timedelta(
            hours=int(article_time[0]),
            minutes=int(article_time[1]),
        )
        if date[0] == "Вчера":
            date_res -= timedelta(days=2)
        date = date_res

    return date


def date_parse_nalogoved(date: str):
    date = date.strip().split(",")
    day = date[0]
    month = date[1].strip().split()[0]
    year = date[1].strip().split()[1]
    month = RU_MONTH_VALUES[month.lower()]
    now = datetime.now()
    date = datetime(
        day=int(day), month=int(month), year=int(year), hour=now.hour, minute=now.minute
    )
    return date


def date_parse_lenta(date: str):
    date = date.strip().split(sep=",")
    tm = date[0].strip().split(sep=":")
    date = date[1].strip().split(sep=" ")
    day = int(date[0])
    month = RU_MONTH_VALUES[date[1]]
    year = int(date[2])
    hour = int(tm[0])
    minute = int(tm[1])

    res = datetime(day=day, month=month, year=year, hour=hour, minute=minute)
    return res


class BaseParser:
    def __init__(
        self,
        header: dict,
        pages_url: str,
        date_parser: Callable,
        articles_block: str = "div",
        articles_attr: Optional[dict] = {"class": "articles"},
        article_block: str = "article",
        article_attr: Optional[dict] = None,
        url_block: str = "h3",
        url_attr: Optional[dict] = None,
        title_block: str = "h1",
        title_attr: Optional[dict] = None,
        date_block: str = "span",
        date_attr: Optional[dict] = {"class": "newsdate"},
        text_block: str = "div",
        text_attr: Optional[dict] = {"class": "text"},
        timeout_sec: int = 60,
        start_page: int = 1,
    ) -> None:

        self.headers = header
        self.pages_url = pages_url
        self.date_parser = date_parser
        self.articles_block = articles_block
        self.articles_attr = articles_attr
        self.article_block = article_block
        self.article_attr = article_attr
        self.url_attr = url_attr
        self.title_block = title_block
        self.title_attr = title_attr
        self.date_block = date_block
        self.date_attr = date_attr
        self.url_block = url_block
        self.session = requests.Session()
        self.timeout_sec = timeout_sec
        self.start_page = start_page
        self.text_block = text_block
        self.text_attr = text_attr

    def parse_website(
        self,
        max_pages,
        stop_datetime: Optional[datetime] = None,
    ):
        stop_datetime = stop_datetime.replace(tzinfo=utc) if stop_datetime else None
        result = list()
        for page in range(self.start_page, max_pages + 1):
            url = self.pages_url + str(page)
            response = self._do_request(url, headers=self.headers)

            # получаем страницу
            tree = BeautifulSoup(response.content, "html.parser")

            # находим блок со всеми новостями
            articles = tree.find(self.articles_block, self.articles_attr)

            # находим каждый блок новости
            articles = articles.find_all(self.article_block, self.article_attr)

            # находим блок урлов для каждой новости
            if not self.url_block:
                articles_urls = [article.a.get("href") for article in articles]
            else:
                articles_urls = [
                    article.find(self.url_block, self.url_attr).a.get("href")
                    for article in articles
                ]

            # парсим каждую новость
            for article_url in articles_urls:
                news_url = urljoin(self.pages_url, article_url)
                response = self._do_request(news_url, headers=self.headers)
                tree = BeautifulSoup(response.content, "html.parser")

                post_date = self.date_parser(
                    tree.find(self.date_block, self.date_attr).text
                ).replace(tzinfo=utc)
                # ограничение по временным рамкам парсинга
                if stop_datetime and post_date < stop_datetime:
                    break

                proc_date = datetime.now().replace(tzinfo=utc)
                title = tree.find(self.title_block, self.title_attr).text
                print(title)

                content = tree.find(self.text_block, self.text_attr)
                full_text = content.text
                full_text = " ".join(full_text.split())
                full_text = full_text.replace("\n", " ")
                full_text = full_text.replace("\t", " ")
                full_text = full_text.replace(";", " ")
                full_text = full_text.strip()

                news = {
                    "uuid": str(uuid4()),
                    "url": news_url,
                    "title": title,
                    "full_text": full_text,
                    "post_dttm": post_date,
                    "processed_dttm": proc_date,
                }
                result.append(news)

        return result

    def _do_request(self, url, headers):
        retries = 0
        while retries < 5:
            try:
                response = self.session.get(url, headers=headers)
            except Exception:
                self.sleep()
                retries += 1
            else:
                return response
        raise Exception("WTF, can't connect")


if __name__ == "__main__":
    url = "https://www.buhgalteria.ru/news/?PAGEN_1="

    # parser_bugalteria = BaseParser(
    #     header=d,
    #     pages_url=url,
    #     date_parser=date_parse,
    #     articles_block="div",
    #     articles_attr={"class": "articles"},
    #     article_block="article",
    #     article_attr=None,
    #     url_block="h3",
    #     url_attr=None,
    #     title_block="h1",
    #     title_attr=None,
    #     text_block="div",
    #     text_attr={"class": "text"},
    #     date_block="span",
    #     date_attr={"class": "newsdate"},
    # )

    # print(parser_bugalteria.parse_website(max_pages=5))

    # parser_nalogoved = BaseParser(
    #     header=d,
    #     pages_url=url_2,
    #     date_parser=date_parse_nalogoved,
    #     articles_block="div",
    #     articles_attr={"class": "pubs-list"},
    #     article_block="div",
    #     article_attr={"class": "news-list"},
    #     url_block=None,
    #     url_attr=None,
    #     title_block="h1",
    #     title_attr=None,
    #     text_block="div",
    #     text_attr={"class": "html"},
    #     date_block="div",
    #     date_attr={"class": "date"},
    # )

    # print(
    #     parser_nalogoved.parse_website(
    #         max_pages=5, stop_datetime=datetime.now() - timedelta(days=2)
    #     )
    # )

    parser_lenta_business = BaseParser(
        header=d,
        pages_url="https://lenta.ru/rubrics/economics/markets/",
        date_parser=date_parse_lenta,
        articles_block="div",
        articles_attr={"class": "rubric-page"},
        article_block="li",
        article_attr={"class": "rubric-page__item _news"},
        url_block=None,
        url_attr=None,
        title_block="span",
        title_attr={"class": "topic-body__title"},
        date_block="time",
        date_attr={"class": "topic-header__time"},
        text_block="div",
        text_attr={"class": "topic-body__content"},
    )

    print(parser_lenta_business.parse_website(max_pages=2))
