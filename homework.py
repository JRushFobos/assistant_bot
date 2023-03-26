# 1. Исправить ошибки
# 2. Доделать логирование и эксепшены +
# 3. Добавить аннотацию типов +

import os
import logging
import requests
import telegram
import time
import sys
from http import HTTPStatus

from dotenv import load_dotenv

from exceptions import (
    JSONformatExceprion,
    NetworkException,
    TokensNotAvailableException,
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

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    encoding="UTF-8",
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)


def check_tokens() -> bool:
    """Проверяем наличия данных в переменных в окружении."""
    if not PRACTICUM_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.critical('Отсутствуют переменные или токены')
        raise TokensNotAvailableException(
            'Токены или данные в переменных не доступны'
        )


def get_api_answer(timestamp: int) -> str:
    """Получаем данные из API сервиса Яндекс.Домашка."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
    except Exception as error:
        raise NetworkException(f'Эндпоинт не доступен. Ошибка {error}')
    if response.status_code != HTTPStatus.OK:
        raise requests.HTTPError('Статус код НЕ 200 ОК')
    try:
        response = response.json()
    except Exception:
        raise JSONformatExceprion('Не корректный формат JSON')
    return response


def check_response(response: dict) -> bool:
    """Проверка наличия данных в JSON."""
    if not isinstance(response, dict):
        raise TypeError('Ответ не содержит словарь')
    elif not isinstance(response.get('homeworks'), list):
        raise TypeError('Ответ не содержит списка homeworks')
    elif not response.get('current_date'):
        raise Exception('Отсутствует дата')


def parse_status(homework: dict) -> str:
    """Парсим название и статус проекта из JSON."""
    if 'status' not in homework:
        raise KeyError('Ключ status отсутствует в словаре')
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name отсутствует в словаре')
    if homework['status'] not in HOMEWORK_VERDICTS:
        raise KeyError('Значение ключа status не совпадает с шаблоном')
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    if not homework_name:
        raise Exception('Отсутствует название домашней работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Функция отправки сообщения о статусе проверки прокта."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение о статусе домашней работы отправлено')
    except Exception:
        logging.error('Отправка сообщеней в телеграмм бот недоступна')


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    message_with_verdict = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            print(response)
            if response['homeworks']:
                new_message = parse_status(response['homeworks'][0])
                if new_message != message_with_verdict:
                    message_with_verdict = new_message
                    send_message(bot, message_with_verdict)
            else:
                logging.debug('Новых сообщений нет')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            print(f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
