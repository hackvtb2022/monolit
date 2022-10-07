import locale
import logging
from datetime import datetime
from random import randint
from time import sleep
from typing import List, Optional, Tuple
from urllib.parse import urljoin
from uuid import uuid4

import requests
from bs4 import BeautifulSoup

from service_scraper.utils import get_stream_logger

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

logger = get_stream_logger(logger_name=__name__)

REQUESTS_TIMEOUT_SEC = 60
SLEEP_SEC = 5


class NalogovedScraper:
    base_url = "https://nalogoved.ru"
    base_url_news = "https://nalogoved.ru/news/"

    def __init__(
        self,
        requests_timeout_sec: int = REQUESTS_TIMEOUT_SEC,
        sleep_sec: int = SLEEP_SEC,
    ) -> None:
        self.session = requests.Session()
        self.requests_timeout_sec = requests_timeout_sec
        self.sleep_sec = sleep_sec
        self.failed_url = []

    def _parse_main_page(self, soup: BeautifulSoup) -> Tuple[List[dict], str]:
        links = []
        for row in soup.findAll("div", class_="news-list"):
            link = row.find("a")
            if link is not None:
                post_dttm = row.find("span").text.strip()
                news = {
                    "uuid": str(uuid4()),
                    "url": urljoin(self.base_url, link.get("href")),
                    "title": link.text.strip(),
                    "post_dttm": datetime.strptime(post_dttm, "%d, %B  %Y")
                    if post_dttm
                    else None,
                    "processed_dttm": datetime.now(),
                }
                links.append(news)
        next_page = soup.find("div", class_="pager").find("a", class_="next")
        next_page = urljoin(self.base_url_news, next_page.get("href"))
        return links, next_page

    def _get_page_urls(self, page: str) -> Tuple[List[dict], Optional[str]]:
        try:
            page = self.session.get(page, timeout=self.requests_timeout_sec)
            assert page.status_code == 200
            soup = BeautifulSoup(page.text, "html.parser")
            links, next_page = self._parse_main_page(soup)
            if not links:
                logger.error(f"No available news for page: {page}")
            return links, next_page
        except requests.exceptions.Timeout as err:
            logger.error(f"Timeout err: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"RequestException err: {err}")
        except Exception as err:
            logger.error(f"Unexcepted err: {err}")
        self.failed_url.append(page)
        return [], None

    def _parse_news_page(self, page) -> Optional[str]:
        try:
            page = self.session.get(page, timeout=self.requests_timeout_sec)
            assert page.status_code == 200
            soup = BeautifulSoup(page.text, "html.parser")
            return soup.find("div", class_="html").text.strip()
        except requests.exceptions.Timeout as err:
            logger.error(f"Timeout err: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"RequestException err: {err}")
        except Exception as err:
            logger.error(f"Unexcepted err: {err}")
        self.failed_url.append(page)
        return None

    def _get_news_text(self, links: List[dict]) -> Tuple[List[dict], datetime]:
        min_post_dttm = links[0]["post_dttm"]
        for link in links:
            link["full_text"] = self._parse_news_page(link["url"])
            if min_post_dttm > link["post_dttm"]:
                min_post_dttm = link["post_dttm"]
        return links, min_post_dttm

    def parse(
        self,
        start_page: str = None,
        stop_post_dttm: datetime = None,
        stop_page_num: str = None,
    ) -> List[dict]:
        """

        Parameters
        ----------
        start_page : str, optional
            Страница, с которой начать парсинг
        stop_post_dttm : datetime, optional
            Последняя дата-время, после которой остановить парсинг
        stop_page_num : str, optional
            Последняя страница, после которой остновать парсинг

        Returns
        -------
        Список из новостей
        """
        sleep(self.sleep_sec + randint(1, 5))
        page = start_page or self.base_url_news
        links, next_page = self._get_page_urls(page)
        if links:
            links, min_post_dttm = self._get_news_text(links)
        if next_page is None:
            logger.error(f"None next_page for page {page}")
            return links

        logger.info(
            f"page {page} next_page {next_page} min_post_dttm {min_post_dttm} parse news {len(links)}"
        )

        if stop_post_dttm and stop_post_dttm >= min_post_dttm:
            return links
        if (
            stop_page_num
            and next_page
            and int(next_page.split("=")[1]) >= stop_page_num + 1
        ):
            return links
        links.extend(
            self.parse(
                start_page=next_page,
                stop_post_dttm=stop_post_dttm,
                stop_page_num=stop_page_num,
            )
        )
        return links


if __name__ == "__main__":
    news = NalogovedScraper()
    # res = news.parse(start_page="https://nalogoved.ru/news/?page=1", stop_page_num=1)
    # logger.debug(f"Result {res[:2]}")
    # logger.debug(f"Result len {len(res)}")

    res = news.parse(
        start_page="https://nalogoved.ru/news/?page=1",
        stop_post_dttm=datetime.strptime("2022-09-26", "%Y-%m-%d"),
    )
    logger.debug(f"Result {res[:2]}")
    logger.debug(f"Result len {len(res)}")
