import csv
import json
from datetime import datetime
from pathlib import Path
from random import randint
from time import sleep
from typing import List, Optional, Tuple
from urllib.parse import urljoin
from uuid import uuid4

import requests
from bs4 import BeautifulSoup

from service_scraper.setting import APP_SETTINGS
from service_scraper.utils import get_stream_logger

logger = get_stream_logger(logger_name=__name__)


class BuhgalteriaScraper:
    base_url = "https://www.buhgalteria.ru"
    base_url_news = "https://www.buhgalteria.ru/news/"
    available_categories = {
        "учет и отчетность",
        "налоги",
        "спецрежимы",
        "организация бизнеса",
        "проверки",
        "вэд",
        "взносы",
        "нормативные акты",
        "ответственность",
    }

    def __init__(
        self,
        csv_path: Path,
        batch_save: int = APP_SETTINGS.BATCH_SAVE,
        requests_timeout_sec: int = APP_SETTINGS.REQUESTS_TIMEOUT_SEC,
        sleep_sec: int = APP_SETTINGS.SLEEP_SEC,
        headers: Optional[dict] = None,
    ) -> None:
        self.csv_path = csv_path
        self.batch_save = batch_save
        self.requests_timeout_sec = requests_timeout_sec
        self.sleep_sec = sleep_sec
        self.headers = headers or APP_SETTINGS.HEADERS
        self.failed_url = []
        self.session = requests.Session()

    def _parse_main_page(self, soup: BeautifulSoup) -> Tuple[List[dict], str]:
        links = []
        for row in soup.findAll("article"):
            category = row.find("span", class_="category")
            if category is None:
                continue
            category = category.find("a")
            if category is None:
                continue
            category = category.text.strip().lower()
            if category in self.available_categories:
                news = {
                    "uuid": str(uuid4()),
                    "post_category": category,
                    "url": urljoin(
                        self.base_url, row.find("h3").find("a").get("href").strip()
                    ),
                    "title": row.find("h3").find("a").text.strip(),
                    "post_dttm": datetime.strptime(
                        row.find("span", class_="published").text.strip(), "%d.%m.%Y"
                    ),
                    "processed_dttm": datetime.now(),
                }
                links.append(news)
        next_page = soup.find("li", class_="bx-pag-next").find("a").get("href")
        next_page = urljoin(self.base_url, next_page)
        return links, next_page

    def _get_page_urls(self, page: str) -> Tuple[List[dict], Optional[str]]:
        try:
            page = self.session.get(
                page, timeout=self.requests_timeout_sec, headers=self.headers
            )
            assert page.status_code == 200
            soup = BeautifulSoup(page.content, "html.parser")
            links, next_page = self._parse_main_page(soup)
            if not links:
                logger.error(f"No available news for page: {page}")
            return links, next_page
        except requests.exceptions.ConnectTimeout as err:
            logger.error(f"ConnectTimeout err: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"RequestException err: {err}")
        except Exception as err:
            logger.error(f"Unexcepted err: {err}")
        self.failed_url.append(page)
        return [], None

    def _parse_news_page(self, page) -> Tuple[Optional[str], Optional[str]]:
        try:
            page = self.session.get(
                page, timeout=self.requests_timeout_sec, headers=self.headers
            )
            assert page.status_code == 200
            soup = BeautifulSoup(page.content, "html.parser")
            content = soup.find("div", class_="text")
            links = ",".join(
                [link.get("href") for link in content.findAll("a") if link.get("href")]
            )
            full_text = content.text
            full_text = " ".join(full_text.split())
            full_text = full_text.replace("\n", " ")
            full_text = full_text.replace("\t", " ")
            full_text = full_text.replace(";", " ")
            full_text = full_text.strip()
            return full_text, links
        except requests.exceptions.Timeout as err:
            logger.error(f"Timeout err: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"RequestException err: {err}")
        except Exception as err:
            logger.error(f"Unexcepted err: {err}")
        self.failed_url.append(page)
        return None, None

    def _get_news_text(self, links: List[dict]) -> Tuple[List[dict], datetime]:
        min_post_dttm = links[0]["post_dttm"]
        for link in links:
            link["full_text"], link["text_links"] = self._parse_news_page(link["url"])
            if min_post_dttm > link["post_dttm"]:
                min_post_dttm = link["post_dttm"]
        return links, min_post_dttm

    def _save_batch(self, links: List[dict], save_all: bool = False):
        if self.batch_save <= len(links) or save_all:
            logger.info(f"Save batch {len(links)}")
            if links:
                with open(self.csv_path, mode="a", encoding="utf8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=links[0].keys(), delimiter=";"
                    )
                    writer.writerows(links)
            return []
        return links

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
        page = start_page or self.base_url_news
        total_news_parsed = 0
        links = []
        while True:
            links_, next_page = self._get_page_urls(page)
            total_news_parsed += len(links_)
            links.extend(links_)
            if links:
                links, min_post_dttm = self._get_news_text(links)
            if next_page is None:
                logger.error(f"None next_page for page {page}")
                self._save_batch(links, save_all=True)
                return

            logger.info(
                f"current page {page} next_page {next_page} min_post_dttm {min_post_dttm} parse news {len(links)} total parsed {total_news_parsed}"
            )

            if (stop_post_dttm and stop_post_dttm >= min_post_dttm) or (
                stop_page_num
                and next_page
                and int(next_page.split("=")[-1]) >= stop_page_num + 1
            ):
                self._save_batch(links, save_all=True)
                return

            links = self._save_batch(links)
            page = next_page
            sleep(self.sleep_sec + randint(1, 5))


if __name__ == "__main__":
    news = BuhgalteriaScraper(
        csv_path=Path("/Users/vgstrelnik/Desktop/projects/hakaton/buhgalteria.csv"),
        batch_save=100,
    )

    # post_dttm 2022-03-25 00:00:00 parse news 88 total parsed 1870
    # [2022-10-08 03:42:36,995] [INFO    ] [__main__]: current page https://www.buhgalteria.ru/news/?id=5443&PAGEN_1=198 next_page https://www.buhgalteria.ru/news/?id=5443&PAGEN_1=199 min_post_dttm 2022-03-24 00:00:00 parse news 99 total parsed 1881
    # последний запуск остановилось на 188
    news.parse(
        start_page="https://www.buhgalteria.ru/news/?PAGEN_1=188", stop_page_num=750
    )
    with open(
        "/Users/vgstrelnik/Desktop/projects/hakaton/buhgalteria_failed.json", "w"
    ) as f:
        json.dump(news.failed_url, f)
