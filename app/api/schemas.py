from enum import Enum
from typing import List

from pydantic import BaseModel


class RolesEnum(str, Enum):
    role_id_1 = "сантехник"
    role_id_2 = "прогер"


class NewsSchema(BaseModel):
    url: str
    title: str


class RoleNewsResponseSchema(BaseModel):
    role_id: RolesEnum
    news: List[NewsSchema]
