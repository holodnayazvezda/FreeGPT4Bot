import sqlite3


def register_user(id_of_user: int) -> None:
    conn = sqlite3.connect('./bot_data/databases/users.sqlite3')
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS DAILY_USERS (id INTEGER)')
    # если в таблице DAILY_USERS в колонке id нет id_of_user, то записать его туда
    if not c.execute(f'SELECT id FROM DAILY_USERS WHERE id=?', (id_of_user,)).fetchall():
        c.execute(f'INSERT INTO DAILY_USERS (id) VALUES (?)', (id_of_user,))
    c.execute(f'CREATE TABLE IF NOT EXISTS USERS (id INTEGER)')
    # если в таблице USERS в колонке id нет id_of_user, то записать его туда
    if not c.execute(f'SELECT id FROM USERS WHERE id=?', (id_of_user,)).fetchall():
        c.execute(f'INSERT INTO USERS (id) VALUES (?)', (id_of_user,))
    conn.commit()
    c.close()
    conn.close()


async def is_new_user(user_id: int) -> bool:
    conn = sqlite3.connect('./bot_data/databases/users.sqlite3')
    c = conn.cursor()
    res = c.execute(f'SELECT COUNT(id) FROM users WHERE id = {user_id}').fetchone()[0]
    c.close()
    conn.close()
    return res == 0
