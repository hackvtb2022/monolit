from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from service_aggregator import run_pipeline
from service_api.api.schemas import (
    NewsClusterSchema,
    PeriodEnum,
    RoleNewsResponseSchema,
)
from service_api.containers import Container
from service_api.crud import get_corpus
from service_api.dependencies import get_db
from service_api.models import NewsEmbModel, NewsModel
from service_insights.models import PipelineRequest
from service_insights.pipeline import Pipeline

router_health = APIRouter(prefix="")
router_main = APIRouter(prefix="/api/v1")

CORPUS_COLS = [
    "url",
    "title",
    "post_dttm",
    "full_text",
    "embedding_full_text",
    "embedding_title",
]


@router_health.get("/")
@router_health.get("/health")
async def read_root():
    return {"Hello": "Refactor"}


def prepare_corpus(
    corpus: List[Tuple[NewsModel, NewsEmbModel]], cols: List[str] = None
) -> pd.DataFrame:
    """Преобразование корпуса тексто из orm моделей в pandas DF

    Args:
        corpus (List[Tuple[NewsModel, NewsEmbModel]]): корпус текстов из БД
        cols (List[str]): Столбцы, с которыми вернем DF

    Returns:
        pd.DataFrame: Корпусов новостей
    """
    cols = cols or CORPUS_COLS
    corpus_sel_col = []
    for news, news_emb in corpus:
        corpus_sel_col.append(
            {
                "url": news.url,
                "title": news.title,
                "post_dttm": news.post_dttm,
                "full_text": news.full_text,
                "embedding_full_text": news_emb.embedding_full_text,
                "embedding_title": news_emb.embedding_title,
            }
        )
    return pd.DataFrame(corpus_sel_col, columns=cols)


def get_last_dttm(period: PeriodEnum) -> datetime:
    if period == PeriodEnum.quarter:
        return (datetime.now() - timedelta(weeks=4 * 3)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif period == PeriodEnum.month:
        return (datetime.now() - timedelta(weeks=4)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif period == PeriodEnum.week:
        return (datetime.now() - timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif period == PeriodEnum.day:
        return (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown period type {period}",
        )


@router_main.get(
    "/trands/{role_id}",
    response_model=RoleNewsResponseSchema,
)
@inject
async def get_trands(
    role_id: str,
    period: PeriodEnum = PeriodEnum.month,
    num_trands: Optional[int] = Query(default=3, title="Кол-во трендов", gt=0, le=20),
    num_trand_news: Optional[int] = Query(
        default=3,
        title="Кол-во новостей в тренде. Если не указано, вернет все доступные",
        gt=0,
        le=20,
    ),
    num_trand_news_insights: Optional[int] = Query(
        default=10,
        title="Кол-во инсайдов из новости тренда. Если не указано, вернет все.",
        gt=0,
        le=20,
    ),
    insights: Pipeline = Depends(Provide[Container.insights]),
    db: Session = Depends(get_db),
):
    """Выгрузка актуальный новостей.

    Возможно конфигурировать:
    - role_id - роль, для которой выгружаются новости
    - period - период, за который выгружаются новости: 'quarter', 'month', 'week', 'day'
    - num_trands - кол-во трендов
    - num_trand_news - кол-во новостей в тренде
        Если не передан, выгруажем все доступные новости тренда
    - num_trand_news_insights - кол-во инсайтов в новости тренда
        сли не передан, выгруажем все доступные инсайты новости тренда
    """

    last_dttm = get_last_dttm(period)
    role_id = role_id.strip()
    corpus = get_corpus(db, role_id, last_dttm)
    if not corpus:
        return RoleNewsResponseSchema(
            status=f"not found", message=f"Not found news for role `{role_id}`"
        )

    corpus = prepare_corpus(corpus)
    clustered_corpus = run_pipeline(
        corpus=corpus,
        clusters=num_trands,
        cluster_top_news=num_trand_news,
        embedding_col="embedding_full_text",
        date_col="post_dttm",
    )
    for trand in clustered_corpus:
        trand_news = trand["news"]
        for news in trand_news:
            insights_request = PipelineRequest(text=news["full_text"])
            insights_vals = insights.run(insights_request)
            insights_vals.items = sorted(insights_vals.items, key=lambda x: -x.score)
            if num_trand_news_insights:
                insights_vals.items = insights_vals.items[:num_trand_news_insights]
            news["insights"] = insights_vals

    return RoleNewsResponseSchema.parse_obj(
        {
            "status": "ok",
            "role_id": role_id,
            "period": period,
            "trands": clustered_corpus,
        }
    )
