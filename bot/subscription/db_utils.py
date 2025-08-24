import psycopg2
from functools import wraps
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()
db_params = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}


"""
Без @wraps(func) функции под декоратором потеряют свои метаданные (свои имя и документацию)
"""


# Определение декоратора с параметрами
def with_db_connection(db_params):     # ✅ Первый уровень - параметры
    """
    Декоратор для автоматического подключения к БД PostgreSQL.
    """
    def decorator(func):               # ✅ Второй уровень - функция
        @wraps(func)                   # Сохраняет метаданные оригинальной функции
        def wrapper(*args, **kwargs):  # ✅ Третий уровень - аргументы вызова
            try:
                with psycopg2.connect(**db_params) as conn:
                    # Передаем соединение как первый аргумент функции
                    return func(conn, *args, **kwargs)
            except psycopg2.Error as e:
                print(f"Database error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator


def with_db_transaction(db_params):
    """
    Декоратор с управлением транзакциями (автокоммит/роллбэк) PostgreSQL.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with psycopg2.connect(**db_params) as conn:
                try:
                    result = func(conn, *args, **kwargs)
                    conn.commit()    # ✅ Явный коммит
                    return result
                except Exception as e:
                    conn.rollback()  # ✅ Явный откат
                    print(f"Transaction failed in {func.__name__}: {e}")
                    raise
        return wrapper
    return decorator


@with_db_transaction(db_params)
def create_sub(conn: psycopg2.extensions.connection,
               target_type: str,
               target_id: int,
               newest_id_chapter: int):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO
            subscriptions(target_type, target_id, newest_id_chapter, created_at)
            VALUES (%s, %s, %s, %s)""",
            (target_type, target_id, newest_id_chapter, datetime.now())
        )


@with_db_connection(db_params)
def check_sub_exists(conn: psycopg2.extensions.connection,
                     target_type: str,
                     target_id: int):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM subscriptions WHERE target_type = %s AND target_id = %s)",
            (target_type, target_id)
        )
        return cursor.fetchone()[0]
