class NetworkException(Exception):
    """Эксепшен дисконекта."""

    pass


class JSONformatExceprion(Exception):
    """Эксепшен не корректного JSON."""

    pass


class TokensNotAvailableException(Exception):
    """Отправка сообщеней в телеграмм бот недоступна."""

    pass
