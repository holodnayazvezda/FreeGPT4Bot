import sqlite3


def drop_daily_users():
    conn = sqlite3.connect('./data/databases/users.sqlite3')
    c = conn.cursor()
    c.execute('DELETE FROM DAILY_USERS')
    conn.commit()
    c.close()
    conn.close()


def drop_amount_of_requests():
    conn = sqlite3.connect('./data/databases/quantity_of_requests.sqlite3')
    c = conn.cursor()
    table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    for table in table_names:
        c.execute(f"DROP TABLE IF EXISTS {table[0]}")
    conn.commit()
    c.close()
    conn.close()