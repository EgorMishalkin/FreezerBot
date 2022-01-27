import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "users.db"


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


def get_user_products(user_id):
    string = ''

    with sqlite3.connect(str(db_path), check_same_thread=False) as conn:
        c = conn.cursor()
        sql = f'SELECT freezer, remain FROM users WHERE user_id = {user_id}'
        c.execute(sql)

        for name, key in c.fetchall():
            if key == 0:
                string += 'продукт ' + name + ' испортился!' + '\n'
            else:
                string += name + ' ' + str(key) + '\n'

    return string


def get_user_ids():

    with sqlite3.connect(str(db_path), check_same_thread=False) as conn:

        c = conn.cursor()

        sql = f'SELECT user_id FROM users'
        c.execute(sql)
        output = c.fetchall()
    output = [val[0] for val in output]
    return output


def update_remains():
    with sqlite3.connect(str(db_path), check_same_thread=False) as conn:

        c = conn.cursor()
        sql = f'UPDATE users SET remain = remain - 1'
        c.execute(sql)


def delete_products():
    with sqlite3.connect(str(db_path), check_same_thread=False) as conn:

        c = conn.cursor()
        sql = f'DELETE FROM users WHERE remain <= 0'
        c.execute(sql)
