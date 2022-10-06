from sqlalchemy import ARRAY, TIMESTAMP, Boolean, Column, Integer, String

from app.database import Base


class NewsModel(Base):
    __tablename__ = "news"

    uuid = Column(String, primary_key=True)
    full_text = Column(String)
    title = Column(String)
    post_dttm = Column(TIMESTAMP)
    url = Column(String, unique=True)
    role_ids = ARRAY(String)
    embedding_full_text = ARRAY(Integer)
    embedding_title = ARRAY(Integer)
    processed_dttm = Column(TIMESTAMP)
