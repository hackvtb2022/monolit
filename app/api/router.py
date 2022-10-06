from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import NewsSchema, RoleNewsResponseSchema, RolesEnum
from app.dependencies import get_db
from app.models import NewsModel

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

    res = db.query(NewsModel).filter(NewsModel.title == "xxx").all()
    print("res", res)

    return RoleNewsResponseSchema(
        role_id=role_id, news=[NewsSchema(url="url", title="title")]
    )
