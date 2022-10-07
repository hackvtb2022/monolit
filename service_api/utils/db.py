import psycopg2
from psycopg2 import Error

from service_api.settings import APP_SETTINGS


def get_db():
    return psycopg2.connect(**APP_SETTINGS.DB_PG_URL)
