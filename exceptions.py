class APINotAvailableException(Exception):
    """API не доступен."""


class APINotStatusCode200(Exception):
    """Статус код ответа отличный от 200 ОК."""


class JSONformatExceprion(Exception):
    """Эксепшен не корректного JSON."""
