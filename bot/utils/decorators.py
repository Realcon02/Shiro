from functools import wraps


def template_decorator():                    # 1-й уровень - параметры декоратора
    def decorator(func):                     # 2-й уровень - функция
        @wraps(func)                         # Сохраняет метаданные оригинальной функции
        async def wrapper(*args, **kwargs):  # 3-й уровень - аргументы вызова
            ...
            result = await func(*args, **kwargs)
            ...
            return result
        return wrapper
    return decorator


# def with_db_connection():
#     """
#     Декоратор для автоматического подключения к БД PostgreSQL.
#     """
#     def decorator(func):                     # 2-й уровень - функция
#         @wraps(func)                         # Сохраняет метаданные оригинальной функции
#         async def wrapper(self, *args, **kwargs):  # 3-й уровень - аргументы вызова
#             async with self.pool.acquire() as conn:
#                 return await func(conn, *args, **kwargs)
#         return wrapper
#     return decorator
#
#
# def with_db_transaction():
#     """
#     Декоратор с управлением транзакциями (автокоммит/роллбэк) PostgreSQL.
#     """
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(self, *args, **kwargs):
#             async with self.pool.acquire() as conn:
#                 async with conn.transaction():
#                     return await func(conn, *args, **kwargs)
#         return wrapper
#     return decorator