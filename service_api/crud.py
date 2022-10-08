from datetime import datetime
from typing import List, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from service_api.models import NewsEmbModel, NewsModel, NewsRolesMapModel


def get_corpus(
    db: Session, role_id: str, dttm_to: datetime
) -> List[Tuple[NewsModel, NewsEmbModel]]:
    """Поиск актуальных новостей для role_id не старше dttm_to

    Args:
        db (Session): Подключение к базе данных
        role_id (str): Роль для поиска
        dttm_to (datetime): До какой даты отбираем новости (включая)

    Returns:
        List[Tuple[NewsModel, NewsEmbModel]]: Корпусов новостей
    """

    corpus = (
        db.query(NewsModel, NewsEmbModel)
        .select_from(NewsModel)
        .join(
            NewsEmbModel,
            and_(NewsModel.uuid == NewsEmbModel.uuid, NewsModel.post_dttm >= dttm_to),
        )
        .join(
            NewsRolesMapModel,
            and_(
                NewsModel.uuid == NewsRolesMapModel.uuid,
                NewsRolesMapModel.role_id == role_id,
            ),
        )
    )
    return corpus.all()
