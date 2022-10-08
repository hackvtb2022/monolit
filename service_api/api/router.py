from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service_aggregator import run_pipeline
from service_api.api.schemas import (
    NewsClusterSchema,
    NewsSchema,
    PeriodEnum,
    RoleNewsResponseSchema,
)
from service_api.containers import Container
from service_api.crud import get_corpus
from service_api.dependencies import get_db
from service_api.models import NewsEmbModel, NewsModel
from service_insights.models import PipelineItemResponse, PipelineRequest
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


@router_main.get(
    "/trands/{role_id}",
    response_model=RoleNewsResponseSchema,
)
@inject
async def task_start(
    role_id: str,
    period: PeriodEnum = PeriodEnum.month,
    k_trands: int = 3,
    k_trand_news: Optional[int] = None,
    insights: Pipeline = Depends(Provide[Container.insights]),
    db: Session = Depends(get_db),
):
    if period == PeriodEnum.month:
        last_dttm = (datetime.now() - timedelta(weeks=4)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif period == PeriodEnum.week:
        last_dttm = (datetime.now() - timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif period == PeriodEnum.day:
        last_dttm = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown period type {period}",
        )
    if k_trands < 1 or k_trands > 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"k_trands should be in range: 1 <= k_trands <= 20",
        )
    if k_trand_news and k_trand_news < 1 or k_trand_news > 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"k_trand_news should be in range: 1 <= k_trand_news <= 20",
        )

    role_id = role_id.strip()
    corpus = get_corpus(db, role_id, last_dttm)
    if not corpus:
        return RoleNewsResponseSchema(
            status=f"not found", message=f"Not found news for role `{role_id}`"
        )

    corpus = prepare_corpus(corpus)
    clustered_corpus = run_pipeline(
        corpus=corpus,
        clusters=k_trands,
        cluster_top_news=k_trand_news,
        embedding_col="embedding_full_text",
        date_col="post_dttm",
    )
    for trand in clustered_corpus:
        trand_news = trand["news"]
        for news in trand_news:
            insights_request = PipelineRequest(text=news["full_text"])
            news["insights"] = insights.run(insights_request)

    return RoleNewsResponseSchema.parse_obj(
        {"status": "ok", "role_id": role_id, "trands": clustered_corpus}
    )
