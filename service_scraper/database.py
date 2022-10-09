from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from service_api.settings import APP_SETTINGS

engine = create_engine(APP_SETTINGS.DB_SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class SessionManager:
    def __init__(self):
        self.session: Session = SessionLocal()

    def __enter__(self):
        return self.session

    def __exit__(self, exception_type, exception_value, traceback):
        self.session.close()
