from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PeriodEnum(str, Enum):
    """Период для выгрузки новостей"""

    month = "month"
    week = "week"
    day = "day"


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"


class InsigtsItemResponse(BaseModel):
    start: int
    end: int
    start: int
    end: int
    sentiment: Sentiment
    score: float
    text: str


class InsigtsResponse(BaseModel):
    items: List[InsigtsItemResponse]


class NewsSchema(BaseModel):
    title: str
    post_dttm: datetime
    url: str
    full_text: str
    insights: InsigtsResponse


class NewsClusterSchema(BaseModel):
    trand_id: int
    trand_title: str
    news: List[NewsSchema]


class RoleNewsResponseSchema(BaseModel):
    status: str
    message: Optional[str]
    role_id: Optional[str]
    trands: Optional[List[NewsClusterSchema]]
