import logging
import os
import time
import sys
from http import HTTPStatus
from json import JSONDecodeError
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    JSONformatExceprion,
    APINotAvailableException,
    APINotStatusCode200,
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - '
    '%(name)s - '
    '%(levelname)s - '
    '%(funcName)s - '
    '%(lineno)d - '
    '%(message)s '
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяем наличия данных в переменных в окружении."""
    tokens = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    empty_tokens = [token for token in tokens if not globals().get(token)]
    if empty_tokens:
        logging.critical(f'Отсутствуют переменные или токены {empty_tokens}')
        sys.exit(1)


def get_api_answer(timestamp: int) -> str:
    """Получаем данные из API сервиса Яндекс.Домашка."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
        if response.status_code != HTTPStatus.OK:
            raise APINotStatusCode200('Статус код НЕ 200 ОК')
        return response.json()
    except requests.RequestException as error:
        raise APINotAvailableException(f'Эндпоинт не доступен. Ошибка {error}')
    except JSONDecodeError:
        raise JSONformatExceprion('Не корректный формат JSON')


def check_response(response: dict):
    """Проверка наличия данных в JSON."""
    if not isinstance(response, dict):
        raise TypeError('Ответ не содержит словарь')
    if 'homeworks' not in response:
        raise TypeError('Отсутствует ключ homeworks')
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            'Значение для ключа homeworks не корретного типа, '
            'должен быть список'
        )
    if 'current_date' not in response:
        logging.warning('Ключ current_date отсутствует')
    elif not isinstance(response.get('current_date'), int):
        logging.warning('current_date должно быть числом')


def parse_status(homework: dict) -> str:
    """Парсим название и статус проекта из JSON."""
    if 'status' not in homework:
        raise KeyError('Ключ status отсутствует в словаре')
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name отсутствует в словаре')
    if not homework['homework_name']:
        raise ValueError('Отсутствует значение ключа homework_name')
    if homework['status'] not in HOMEWORK_VERDICTS:
        raise ValueError('Значение ключа status не совпадает с шаблоном')
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Функция отправки сообщения о статусе проверки прокта."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        logging.error('Отправка сообщеней в телеграмм бот недоступна')
    else:
        logging.debug('Сообщение о статусе домашней работы отправлено')


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    message_with_verdict = ''
    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            timestamp = response.get('current_date', timestamp)
            if response['homeworks']:
                new_message = parse_status(response['homeworks'][0])
                if new_message != message_with_verdict:
                    message_with_verdict = new_message
                    send_message(bot, message_with_verdict)
                else:
                    logging.debug('Новых сообщений нет')
        except Exception as error:
            new_message = f'Сбой в работе программы: {error}'
            if new_message != last_message:
                last_message = new_message
                send_message(bot, new_message)
                logging.error(new_message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
