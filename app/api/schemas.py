from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class RolesEnum(str, Enum):
    role_id_1 = "сантехник"
    role_id_2 = "прогер"


class NewsSchema(BaseModel):
    url: str
    title: str
    score: float


class RoleNewsResponseSchema(BaseModel):
    status: str
    message: Optional[str]
    role_id: Optional[RolesEnum]
    news: Optional[List[NewsSchema]]
