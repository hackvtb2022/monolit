from app.database import Base
from sqlalchemy import ARRAY, TIMESTAMP, Column, Float, String


class NewsModel(Base):
    __tablename__ = "news"

    uuid = Column(String, primary_key=True)
    full_text = Column(String)
    title = Column(String)
    post_dttm = Column(TIMESTAMP)
    url = Column(String, unique=True)
    role_ids = ARRAY(String)
    embedding_full_text = ARRAY(Float)
    embedding_title = ARRAY(Float)
    processed_dttm = Column(TIMESTAMP)


class NewsScoreModel(Base):
    __tablename__ = "news_score"

    uuid = Column(String, primary_key=True)
    role_id = Column(String, primary_key=True)
    score = Column(Float)
    processed_dttm = Column(TIMESTAMP, primary_key=True)
