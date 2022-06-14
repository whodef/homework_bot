class ResponseErrorException(Exception):
    """Исключение при отсутствии ответа."""


class StatusCodeErrorException(Exception):
    """Исключение если код запроса не равен 200."""


class TokenErrorException(Exception):
    """Исключение при возникновении ошибок в токенах."""
