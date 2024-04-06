import sqlite3


async def get_amount_of_users() -> dict:
    conn = sqlite3.connect('./data/databases/users.sqlite3')
    c = conn.cursor()
    try:
        total_amount_of_users = c.execute('SELECT COUNT(id) FROM USERS').fetchone()[0]
    except IndexError:
        total_amount_of_users = 1
    try:
        daily_amount_of_users = c.execute('SELECT COUNT(id) FROM DAILY_USERS').fetchone()[0]
    except IndexError:
        daily_amount_of_users = 1
    c.close()
    conn.close()
    return {"total": total_amount_of_users, "daily": daily_amount_of_users}
