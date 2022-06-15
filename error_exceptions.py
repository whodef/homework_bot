class BaseErrorException(Exception):
    """Базовый класс, оптимизирующий все исключения."""


class ResponseErrorException(BaseErrorException):
    """Исключение при отсутствии ответа."""


class StatusCodeErrorException(BaseErrorException):
    """Исключение если код запроса не равен 200."""


class TokenErrorException(BaseErrorException):
    """Исключение при возникновении ошибок в токенах."""
