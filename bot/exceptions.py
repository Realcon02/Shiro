class UploaderError(Exception):
    """Базовый класс для ошибок DiscordUploader"""

class UploaderChannelNotFound(UploaderError):
    """Канал для загрузки не найден или имеет неверный тип"""

class UploaderPermissionError(UploaderError):
    """Недостаточно прав для отправки файла в канал"""
