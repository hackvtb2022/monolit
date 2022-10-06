import psycopg2
from app.settings import APP_SETTINGS
from psycopg2 import Error


def get_db():
    return psycopg2.connect(**APP_SETTINGS.DB_PG_URL)
