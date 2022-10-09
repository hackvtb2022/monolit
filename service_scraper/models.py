from sqlalchemy import ARRAY, TIMESTAMP, Column, Float, String
from sqlalchemy.ext.mutable import MutableList

from service_api.database import Base


class NewsModel(Base):
    """Таблица новостей"""

    __tablename__ = "news_tmp1"

    uuid = Column(String)
    full_text = Column(String)
    title = Column(String)
    post_dttm = Column(TIMESTAMP)
    url = Column(String, primary_key=True)
    text_links = Column(String)
    processed_dttm = Column(TIMESTAMP)


class NewsEmbModel(Base):
    """Таблица эмбедингов новостей"""

    __tablename__ = "news_emb_tmp1"

    uuid = Column(String, primary_key=True)
    embedding_full_text = Column(MutableList.as_mutable(ARRAY(Float)))
    embedding_title = Column(MutableList.as_mutable(ARRAY(Float)))


class NewsRolesMapModel(Base):
    """Таблица соответствия роли и новости"""

    __tablename__ = "news_roles_map_tmp1"

    uuid = Column(String, primary_key=True)
    role_id = Column(String, primary_key=True)
