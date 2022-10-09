import time
from datetime import datetime, timedelta
from typing import List

from service_aggregator.embedder import get_embeddings_text
from service_scraper.database import SessionManager
from service_scraper.models import NewsEmbModel, NewsModel, NewsRolesMapModel
from service_scraper.settings import APP_SETTINGS
from service_scraper.spiders.parsers import parser_lenta_business
from service_scraper.upsert import upsert
from service_scraper.utils import get_stream_logger

logger = get_stream_logger(logger_name=__name__)


def get_last_post_dttm() -> datetime:
    return (datetime.now() - timedelta(days=1)).replace(
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
                text_links=row["text_links"],
                processed_dttm=processed_dttm,
            )
        )
        news_roles_models.append(
            NewsRolesMapModel(uuid=row["uuid"], role_id=row["role_id"])
        )
        news_emd_models.append(
            NewsEmbModel(
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
            no_update_cols=[],
        )
        logger.info("put NewsRolesMapModel")
        db.bulk_save_objects(news_roles_models)
        logger.info("put NewsEmbModel")
        db.bulk_save_objects(news_emd_models)


def add_emb(role_id: str, news: List[dict]) -> List[dict]:
    for row in news:
        row["role_id"] = role_id
        row["embedding_full_text"] = get_embeddings_text([row["full_text"]])[0]
        row["embedding_title"] = get_embeddings_text([row["title"]])[0]
    return news


def get_news(parser, last_post_dttm) -> List[dict]:
    return parser.parse_website(max_pages=2, stop_datetime=last_post_dttm)


def run_spider():
    role_id = "ген_директор"
    parser = parser_lenta_business
    while True:
        try:
            last_post_dttm = get_last_post_dttm()
            logger.info("get_news")
            news = get_news(parser, last_post_dttm)
            if news:
                logger.info("add_emb")
                news = add_emb(role_id, news)
                logger.info("put_news")
                put_news(news)
        except Exception as err:
            logger.info(f"Unexcepted error: {err}")
        logger.info("sleep")
        time.sleep(APP_SETTINGS.SPIDER_WAIT_TIMEOUT_SEC)


if __name__ == "__main__":
    run_spider()
