from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from service_api.api.schemas import NewsSchema, RoleNewsResponseSchema, RolesEnum
from service_api.crud import get_news_score
from service_api.dependencies import get_db

router_health = APIRouter(prefix="")
router_main = APIRouter(prefix="/api/v1")


@router_health.get("/")
@router_health.get("/health")
async def read_root():
    return {"Hello": "Refactor"}


@router_main.get(
    "/news/{role_id}",
    response_model=RoleNewsResponseSchema,
)
async def task_start(role_id: RolesEnum, db: Session = Depends(get_db)):
    role_id = role_id.value.lower().strip()

    news_score = get_news_score(db, role_id)
    if not news_score:
        return RoleNewsResponseSchema(
            status=f"not found", message=f"Not found news for role `{role_id}`"
        )

    resp = RoleNewsResponseSchema(status="ok", role_id=role_id)
    news = []
    for score, news_raw in news_score:
        news.append(
            NewsSchema(url=news_raw.url, title=news_raw.title, score=score.score)
        )
    resp.news = news

    return resp
