# 1. Исправить ошибки
# 2. Доделать логирование и эксепшены
# 3. Добавить аннотацию типов

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
    NotSendMessageException,
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
    filename='logs.log',
    encoding="UTF-8",
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)


def check_tokens():
    """Проверяем наличия данных в переменных в окружении."""
    if not PRACTICUM_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.critical('Отсутствуют переменные или токены')
        raise TokensNotAvailableException(
            'Токены или данные в переменных не доступны'
        )


def get_api_answer(timestamp):
    """Получаем данные из API сервиса Яндекс.Домашка."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
    except Exception as error:
        logging.error('Эндпоинт не доступен')
        raise NetworkException(f'Эндпоинт не доступен. Ошибка {error}')
    if response.status_code != HTTPStatus.OK:
        logging.error('Статус код НЕ 200 ОК')
        raise requests.HTTPError('Статус код НЕ 200 ОК')
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        ).json()
    except Exception:
        logging.error('Не корректный формат JSON')
        raise JSONformatExceprion('Не корректный формат JSON')
    return response


def check_response(response):
    """Проверка наличия данных в JSON."""
    if not isinstance(response, dict):
        logging.error('Ответ не содержит словарь')
        raise TypeError('Ответ не содержит словарь')
    elif not isinstance(response.get('homeworks'), list):
        logging.error('Ответ не содержит списка homeworks')
        raise TypeError('Ответ не содержит списка homeworks')
    elif not response.get('current_date'):
        logging.error('Отсутствует дата')
        raise Exception('Отсутствует дата')


def parse_status(homework):
    """Парсим название и статус проекта из JSON."""
    if 'lesson_name' not in homework:
        raise KeyError('Ключ lesson_name отсутствует в словаре')
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
        logging.error('Сообщение о статусе домашней работы НЕ отвлено')
        raise NotSendMessageException(
            'Отправка сообщеней в телеграмм бот недоступна'
        )


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
            # Проверяем наличие ревью
            if not response['homeworks']:
                # send_message(bot, 'нет сообщений')
                time.sleep(RETRY_PERIOD)
                continue
            new_message = parse_status(response['homeworks'][0])
            # Проверяем наличие нового результата ревью
            if new_message != message_with_verdict:
                message_with_verdict = new_message
                send_message(bot, message_with_verdict)

        except Exception as error:
            # message = f'Сбой в работе программы: {error}'
            print(f'Сбой в работе программы: {error}')
        time.sleep(RETRY_PERIOD)

    # """Основная логика работы бота."""
    # check_tokens()
    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = 1549962000  # int(time.time())
    # message_with_verdict = ''
    # while True:
    #     try:
    #         response = get_api_answer(timestamp)
    #         check_response(response)
    #         # Проверяем наличие ревью
    #         new_message = parse_status(response['homeworks'][0])
    #         print(response)
    #         send_message(bot, new_message)

    #     except Exception as error:
    #         # message = f'Сбой в работе программы: {error}'
    #         print(f'Сбой в работе программы: {error}')
    #     time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
