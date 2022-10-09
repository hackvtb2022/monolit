import time
import traceback
from datetime import datetime, timedelta
from typing import List

from loguru import logger

from service_aggregator.embedder import get_embeddings_text
from service_scraper.database import SessionManager
from service_scraper.models import NewsEmbModel, NewsModel, NewsRolesMapModel
from service_scraper.settings import APP_SETTINGS
from service_scraper.spiders import (
    BuhgalteriaParser,
    ExpertParser,
    LentaParser,
    NalogovedParser,
)
from service_scraper.upsert import upsert

ROLE_SOURCES = {
    # "бухгалтер": [
    #     # NalogovedParser("https://nalogoved.ru/news?page="),
    #     BuhgalteriaParser("https://www.buhgalteria.ru/news/?PAGEN_1="),
    # ],
    "ген_директор": [
        ExpertParser("https://expert.ru/ekonomika/"),
        # LentaParser("https://lenta.ru/rubrics/economics/investments/"),
    ]
}


def get_last_post_dttm(period_days: int) -> datetime:
    return (datetime.now() - timedelta(days=period_days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def put_news(news: List[dict]):
    news_models = []
    news_roles_models = []
    news_emd_models = []
    processed_dttm = datetime.now().replace(tzinfo=None)
    for row in news:
        news_models.append(
            dict(
                uuid=row["uuid"],
                full_text=row["full_text"],
                title=row["title"],
                post_dttm=row["post_dttm"],
                url=row["url"],
                text_links=row.get("text_links"),
                processed_dttm=processed_dttm,
            )
        )
        news_roles_models.append(dict(uuid=row["uuid"], role_id=row["role_id"]))
        news_emd_models.append(
            dict(
                uuid=row["uuid"],
                embedding_full_text=row["embedding_full_text"],
                embedding_title=row["embedding_title"],
            )
        )
    with SessionManager() as db:
        logger.info("put NewsModel")
        upsert(
            db,
            NewsModel,
            news_models,
            as_of_date_col="processed_dttm",
        )
        logger.info("put NewsRolesMapModel")
        # db.bulk_save_objects(news_roles_models)
        upsert(
            db,
            NewsRolesMapModel,
            news_roles_models,
        )
        logger.info("put NewsEmbModel")
        # db.bulk_save_objects(news_emd_models)
        upsert(
            db,
            NewsEmbModel,
            news_emd_models,
        )


def add_emb(role_id: str, news: List[dict]) -> List[dict]:
    for row in news:
        row["role_id"] = role_id
        row["embedding_full_text"] = get_embeddings_text([row["full_text"]])[0]
        row["embedding_title"] = get_embeddings_text([row["title"]])[0]
    return news


def run_spider():
    while True:
        last_post_dttm = get_last_post_dttm(APP_SETTINGS.SPIDER_PERIOD_DAYS)
        for role_id in ROLE_SOURCES:
            for parser in ROLE_SOURCES[role_id]:
                logger.info(f"Start {role_id} {parser.pages_url}")
                try:
                    news = parser.parse(stop_datetime=last_post_dttm)
                    if news:
                        news = add_emb(role_id, news)
                        put_news(news)
                        logger.info(f"Done {role_id} {parser.pages_url}")
                    else:
                        logger.error(f"No news for {role_id} {parser.pages_url}")
                except Exception as err:
                    trace = traceback.format_exc()
                    logger.error(f"Unexpected exception {err} trace {trace}")
        logger.info("sleep")
        time.sleep(APP_SETTINGS.SPIDER_WAIT_TIMEOUT_SEC)


if __name__ == "__main__":
    run_spider()
