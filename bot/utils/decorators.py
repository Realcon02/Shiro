from functools import wraps


def template_decorator():  # 1-й уровень - параметры декоратора
    def decorator(func):  # 2-й уровень - функция
        @wraps(func)  # Сохраняет метаданные оригинальной функции
        async def wrapper(*args, **kwargs):  # 3-й уровень - аргументы вызова
            ...
            result = await func(*args, **kwargs)
            ...
            return result

        return wrapper

    return decorator
