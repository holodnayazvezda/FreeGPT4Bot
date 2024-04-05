import sqlite3


async def increase_the_number_of_requests_for_the_user(database_name: str, table_name: str, user_id: int) -> None:
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER, amount_of_requests INTEGER)')
    if c.execute(f'SELECT * FROM {table_name} WHERE id=?', (user_id,)).fetchone():
        c.execute(f'UPDATE {table_name} SET amount_of_requests=amount_of_requests+1 WHERE id=?', (user_id,))
    else:
        c.execute(f'INSERT INTO {table_name} (id, amount_of_requests) VALUES (?, ?)', (user_id, 1))
    conn.commit()
    c.close()
    conn.close()


async def get_amount_of_requests_for_user(database_name: str, table_name: str, user_id: int) -> int:
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER, amount_of_requests INTEGER)')
    amount_of_requests = c.execute(f'SELECT amount_of_requests FROM {table_name} WHERE id=?', (user_id,)).fetchone()
    conn.commit()
    c.close()
    conn.close()
    if amount_of_requests is not None:
        return amount_of_requests[0]
    return 0


async def get_available_amount_of_requests_to_chat_gpt(model: str) -> int:
    # мб потом подысправить под реферальную систему, но пока так
    if 'gpt-4' in model or 'gpt-3.5' in model:
        return 30
    else:
        return 30
