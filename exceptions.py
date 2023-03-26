class NetworkException(Exception):
    """Эксепшен дисконекта."""

    pass


class JSONformatExceprion(Exception):
    """Эксепшен не корректного JSON."""

    pass


class NotSendMessageException(Exception):
    """Отправка сообщеней в телеграмм бот недоступна."""

    pass


class TokensNotAvailableException(Exception):
    """Отправка сообщеней в телеграмм бот недоступна."""

    pass
