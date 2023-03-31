class APINotAvailableException(Exception):
    """API не доступен."""


class APINotStatusCode200(Exception):
    """Статус код ответа отличный от 200 ОК."""


class JSONformatExceprion(Exception):
    """Эксепшен не корректного JSON."""


class ExceptionWithOutMessage(Exception):
    """Ексепшен для ошибок без передачи в телеграм"""


class CurrentDateError(ExceptionWithOutMessage):
    """Эксепшен ошибки ключа current_date"""


class CurrentDateTypeError(ExceptionWithOutMessage):
    """Эксепшен ошибки типа значение ключа current_date"""
