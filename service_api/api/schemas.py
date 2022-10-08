from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PeriodEnum(str, Enum):
    month = "month"
    week = "week"
    day = "day"


class InsigtsItemResponse(BaseModel):
    start: int
    end: int


class InsigtsItemTextResponse(BaseModel):
    text: str


class InsigtsResponse(BaseModel):
    items: List[InsigtsItemResponse]
    items_text: List[InsigtsItemTextResponse]


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
