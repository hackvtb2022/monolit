from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import NewsModel, NewsScoreModel


def get_news_score(db: Session, role_id: str) -> List[Tuple[NewsScoreModel, NewsModel]]:
    """Поиск актуальных новостей для role_id

    Parameters
    ----------
    db : Session
        Подключение к базе данных
    role_id : str
        Роль

    Returns
    -------
    Актуальные новости
    """

    max_dttm = db.query(func.max(NewsScoreModel.processed_dttm))
    news_score = (
        db.query(NewsScoreModel, NewsModel)
        .filter(
            NewsScoreModel.processed_dttm == max_dttm, NewsScoreModel.role_id == role_id
        )
        .join(NewsModel, NewsScoreModel.uuid == NewsModel.uuid)
        .all()
    )
    return news_score
