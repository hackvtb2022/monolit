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


class AuditItScraper:
    base_url = "https://www.audit-it.ru"
    base_url_news = "https://www.audit-it.ru/news/account"
    news_pages_tpl = "https://www.audit-it.ru/news/account/{}/"

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

    def _parse_main_page(self, soup: BeautifulSoup) -> List[dict]:
        links = []
        dates = [
            datetime.strptime(post_dttm.text.strip(), "%d %B %Y")
            for post_dttm in soup.findAll("span", class_="date-news")
        ]
        for post_dt, news_block in zip(
            dates, soup.findAll("ul", class_="type-first info-box")
        ):
            for row in news_block.findAll("li"):
                title = row.find("a").text.strip()
                if (
                    "новости недели" in title
                    or "наиболее важные новости недели" in title.lower()
                ):
                    continue
                news = {
                    "uuid": str(uuid4()),
                    "url": urljoin(self.base_url, row.find("a").get("href").strip()),
                    "title": title,
                    "post_dttm": datetime.combine(
                        post_dt,
                        datetime.strptime(
                            row.find("span", class_="time").text.strip(), "%H:%M"
                        ).time(),
                    ),
                    "processed_dttm": datetime.now(),
                }
                links.append(news)
        return links

    def _get_page_urls(self, page: str) -> List[dict]:
        page_raw = page
        try:
            page = self.session.get(
                page, timeout=self.requests_timeout_sec, headers=self.headers
            )
            assert page.status_code == 200
            soup = BeautifulSoup(page.content, "html.parser")
            links = self._parse_main_page(soup)
            if not links:
                logger.error(f"No available news for page: {page}")
            return links
        except requests.exceptions.ConnectTimeout as err:
            logger.error(f"ConnectTimeout err: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"RequestException err: {err}")
        except Exception as err:
            logger.error(f"Unexcepted err: {err}")
        self.failed_url.append(page)
        return []

    def _parse_news_page(self, page) -> Tuple[Optional[str], Optional[str]]:
        try:
            page = self.session.get(
                page, timeout=self.requests_timeout_sec, headers=self.headers
            )
            assert page.status_code == 200
            soup = BeautifulSoup(page.content, "html.parser")
            content = soup.find("div", class_="block-p-mb30")
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
            logger.error(f"Unexcepted err: {str(err)}")
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
        start_page: int = None,
        stop_post_dttm: datetime = None,
        stop_page_num: int = None,
    ) -> List[dict]:
        """

        Parameters
        ----------
        start_page : int, optional
            Страница, с которой начать парсинг
        stop_post_dttm : datetime, optional
            Последняя дата-время, после которой остановить парсинг
        stop_page_num : int, optional
            Последняя страница, после которой остновать парсинг

        Returns
        -------
        Список из новостей
        """
        page = start_page or 1
        next_page = 0
        total_news_parsed = 0
        links = []
        min_post_dttm = None
        while True:
            links_ = self._get_page_urls(self.news_pages_tpl.format(page))
            total_news_parsed += len(links_)
            links.extend(links_)
            if links:
                sleep(randint(1, 5))
                links, min_post_dttm = self._get_news_text(links)
            next_page += start_page + 1

            logger.info(
                f"current page {page} next_page {next_page} min_post_dttm {min_post_dttm} parse news {len(links)} total parsed {total_news_parsed}"
            )

            if (
                stop_post_dttm and min_post_dttm and stop_post_dttm >= min_post_dttm
            ) or (stop_page_num and next_page >= stop_page_num + 1):
                self._save_batch(links, save_all=True)
                return

            links = self._save_batch(links)
            page = next_page
            sleep(self.sleep_sec + randint(1, 5))


if __name__ == "__main__":
    news = AuditItScraper(
        csv_path=Path("/Users/vgstrelnik/Desktop/projects/hakaton/audit_it.csv"),
        batch_save=10,
        sleep_sec=10,
    )

    news.parse(start_page=1, stop_page_num=500)
    with open(
        "/Users/vgstrelnik/Desktop/projects/hakaton/audit_it_failed.json", "w"
    ) as f:
        json.dump(news.failed_url, f)
