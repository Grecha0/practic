import psycopg2
from values import dbname, user, password, host, port

conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
cursor = conn.cursor()

# Инициализация базы данных и создание таблицы, если её ещё нет
def record_token(access_token):
    cursor.execute('INSERT INTO tokens (token) VALUES (%s)', (access_token,))
    conn.commit()

# Обновление токена в базе данных
def update_token(access_token):
    cursor.execute('''
        UPDATE tokens
        SET token = %s
        WHERE id = 1
    ''', (access_token,))
    conn.commit()

# Получение текущего токена из базы данных
def get_token():
    cursor.execute("""CREATE TABLE IF NOT EXISTS tokens(id INTEGER PRIMARY KEY, token TEXT)""")
    cursor.execute('SELECT COUNT(*) FROM tokens WHERE id = %s', (1,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Если записи с таким id нет, выполняем вставку
        cursor.execute('INSERT INTO tokens VALUES (%s, %s)', (1, 1))
        conn.commit()
    conn.commit()
    cursor.execute('SELECT token FROM tokens WHERE id = 1')
    row = cursor.fetchone()
    return row[0]


def get_vacancy_info(name, salary_from, salary_to, currency, city, metro_station, id, user_id_vac):

    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vacancies (
        vacancy_name TEXT,
        salary_from TEXT,
        salary_to TEXT,
        currency TEXT,
        city TEXT,
        metro TEXT,
        id TEXT,
        user_id_vac BIGINT
    )
""")
    conn.commit()

    cur.execute("""
            INSERT INTO vacancies (vacancy_name, salary_from, salary_to, currency, city, metro, id, user_id_vac)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, salary_from, salary_to, currency, city, metro_station, id, user_id_vac))

    # Commit the changes and close the connection
    conn.commit()