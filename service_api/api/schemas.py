from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class RolesEnum(str, Enum):
    """Роли для выгрузки новостей"""

    accountant = "бухгалтер"
    general_manager = "ген_директор"


class PeriodEnum(str, Enum):
    """Период для выгрузки новостей"""

    quarter = "quarter"
    month = "month"
    week = "week"
    day = "day"


class Sentiment(str, Enum):
    """Значения сентимента"""

    positive = "positive"
    negative = "negative"


class InsigtsItemResponse(BaseModel):
    """Структура инсайта"""

    start: int
    end: int
    start: int
    end: int
    sentiment: Sentiment
    score: float
    text: str


class InsigtsResponse(BaseModel):
    """Структура инсайтов"""

    items: List[InsigtsItemResponse]


class NewsSchema(BaseModel):
    """Структура новости"""

    title: str
    post_dttm: datetime
    url: str
    full_text: str
    insights: InsigtsResponse


class NewsTrandsSchema(BaseModel):
    """Структура тренда"""

    trand_id: int
    trand_title: str
    news: List[NewsSchema]


class RoleNewsResponseSchema(BaseModel):
    """Структура ответа API по запросу трендов"""

    status: str
    message: Optional[str]
    role_id: Optional[str]
    period: Optional[PeriodEnum]
    trands: Optional[List[NewsTrandsSchema]]
