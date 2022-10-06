from psycopg2 import Error

from app.utils.db import get_db
from app.utils.log import get_stream_logger

logger = get_stream_logger()

QUERY = """SELECT * from news"""


def get_hello():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(QUERY)
        res = cursor.fetchall()
        logger.debug(f"select from news: {res}")
    except (Exception, Error) as error:
        logger.debug(f"PG error: {error}")
    finally:
        if conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    get_hello()
