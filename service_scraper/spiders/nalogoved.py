import locale
import logging
from datetime import datetime
from typing import List, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from service_scraper.utils import get_stream_logger

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

logger = get_stream_logger()


class NalogovedScraper:
    base_url = "https://nalogoved.ru"
    base_url_news = "https://nalogoved.ru/news/"

    def _parse_main_page(self, soup: BeautifulSoup) -> Tuple[List[dict], str]:
        links = []
        for row in soup.findAll("div", class_="news-list"):
            link = row.find("a")
            if link is not None:
                news = {}
                news["link"] = urljoin(self.base_url, link.get("href"))
                news["title"] = link.text.strip()
                post_dttm = row.find("span").text.strip()
                news["post_dttm"] = (
                    datetime.strptime(post_dttm, "%d, %B  %Y") if post_dttm else None
                )
                links.append(news)
        next_page = soup.find("div", class_="pager").find("a", class_="next")
        next_page = urljoin(self.base_url_news, next_page.get("href"))
        return links, next_page

    def _get_page_urls(self, page: str) -> Tuple[List[dict], str]:
        try:
            page = requests.get(page)
            assert page.status_code == 200
            soup = BeautifulSoup(page.text, "html.parser")
            links, next_page = self._parse_main_page(soup)
            if not links:
                logger.error(f"No available news for page: {page}")
            return links, next_page
        except Exception as err:
            logger.error(f"Unexcepted err: {err}")

    def _parse_news_page(self, page) -> str:
        try:
            page = requests.get(page)
            assert page.status_code == 200
            soup = BeautifulSoup(page.text, "html.parser")
            return soup.find("div", class_="html").text.strip()
        except Exception as err:
            logging.error(f"Unexcepted err: {err}")

    def _get_news_text(self, links: List[dict]):
        max_post_dttm = links[0]["post_dttm"]
        for link in links:
            link["full_text"] = self._parse_news_page(link["link"])
            if max_post_dttm < link["post_dttm"]:
                max_post_dttm = link["post_dttm"]
        return links, max_post_dttm

    def parse(
        self, start_page: str = None, stop_post_dttm=None, stop_page_num=None
    ) -> List[dict]:
        """

        Parameters
        ----------
        start_page : str, optional
            Страница, с которой начать парсинг
        stop_post_dttm : str, optional
            Последняя дата-время, после которой остановить парсинг
        stop_page_num : str, optional
            Последняя страница, после которой остновать парсинг

        Returns
        -------
        None
        """
        page = start_page or self.base_url_news
        links, next_page = self._get_page_urls(page)
        if links:
            links, max_post_dttm = self._get_news_text(links)
        logger.info(
            "Parse %s %s %s %s",
            page,
            max_post_dttm,
            int(next_page.split("=")[1]),
            stop_page_num,
        )
        if stop_post_dttm and stop_post_dttm >= max_post_dttm:
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
    res = news.parse(start_page="https://nalogoved.ru/news/?page=2", stop_page_num=2)
    logger.debug(f"Result {res[:2]}")
    logger.debug(f"Result len {len(res)}")
