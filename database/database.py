import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "users.db"


# функция подключния к бд
# def ensure_connection(func):
#     def inner(*args, **kwargs):
#         global conn
#         with sqlite3.connect(str(db_path), check_same_thread=False) as conn:
#             kwargs['conn'] = conn
#             res = func(*args, **kwargs)
#         return res
#
#     return inner


# создание бд
# @ensure_connection
def init_db(force: bool = False):
    with sqlite3.connect(str(db_path), check_same_thread=False) as conn:
        c = conn.cursor()
        if force:
            c.execute('DROP TABLE IF EXISTS users')

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER NOT NULL,
                freezer     TEXT,
                remain INTEGER)
        ''')
        conn.commit()
