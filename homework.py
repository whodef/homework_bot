import os
import time
import logging
from http import HTTPStatus

import telegram
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

SEND_MESSAGE_INFO_LOG = 'Отправлено сообщение: "{}"'

API_ANSWER_ERROR = (
    'Ошибка подключения к API: {error}\n {url}\n {headers}\n {params}')

RESPONSE_ERROR = (
    'Ошибка в респонсе: {error}\n {key}\n {url}\n {headers}\n {params}')

STATUS_CODE_ERROR = (
    'Ошибка при запросе к API: '
    '{status_code}\n {url}\n {headers}\n {params}')

UNKNOWN_STATUS_ERROR = 'Неизвестный статус: {}'

CHANGED_STATUS = 'Изменился статус проверки работы "{}". {}'

NOT_DICT_RESPONSE = 'Ответ API не является словарем'

HOMEWORK_NOT_IN_RESPONSE = 'Отсутствует ключ homework в ответе'

HOMEWORK_IS_NOT_LIST = 'Ответ не является списком'

TOKEN_NOT_FOUND = 'Токен {} не найден!'

TOKEN_ERROR = 'Ошибка в токенах'

ERROR_MESSAGE = 'Сбой в работе программы: {}'

HOMEWORK_NAME_NOT_FOUND = 'Не найден ключ "homework_name"'

SEND_MESSAGE_ERROR = 'Ошибка при отправке сообщения: {}'

VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class ResponseErrorException(Exception):
    """Исключение при отсутствии ответа."""
    pass


class StatusCodeErrorException(Exception):
    """Исключение если код запроса не равен 200."""
    pass


class TokenErrorException(Exception):
    """Исключение при возникновении ошибок в токенах."""
    pass


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""

    bot.send_message(TELEGRAM_CHAT_ID, message)
    logging.info(SEND_MESSAGE_INFO_LOG.format(message))


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""

    params = dict(
        url=ENDPOINT, headers={'Authorization': f'OAuth {PRACTICUM_TOKEN}'},
        params={'from_date': current_timestamp}
    )
    try:
        response = requests.get(**params)
    except RequestException as error:
        raise ConnectionError(
            API_ANSWER_ERROR.format(error=error, **params))

    status_code = response.status_code

    if not status_code == HTTPStatus.OK:
        raise StatusCodeErrorException(
            STATUS_CODE_ERROR.format(status_code=status_code, **params)
        )

    response_json = response.json()

    for key in ('error', 'code'):
        if key in response_json:
            raise ResponseErrorException(
                RESPONSE_ERROR.format(
                    error=response_json[key], key=key, **params
                )
            )
    return response_json


def check_response(response):
    """Проверяет ответ API на корректность."""

    if type(response) is not dict:
        raise TypeError(NOT_DICT_RESPONSE)

    if 'homeworks' not in response:
        raise ValueError(HOMEWORK_NOT_IN_RESPONSE)

    homework = response['homeworks']

    if type(homework) is not list:
        raise TypeError(HOMEWORK_IS_NOT_LIST)

    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""

    status = homework['status']

    if 'homework_name' not in homework:
        raise KeyError(HOMEWORK_NAME_NOT_FOUND)

    if status not in VERDICTS:
        raise ValueError(UNKNOWN_STATUS_ERROR.format(status))

    return CHANGED_STATUS.format(homework['homework_name'], VERDICTS.get(status))


def check_tokens():
    """Проверяет доступность переменных окружения."""

    tokens = all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
    return tokens or logging.critical(TOKEN_NOT_FOUND.format(tokens))


def main():
    """Основная логика работы программы."""

    if not check_tokens():
        raise TokenErrorException(TOKEN_ERROR)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)

            if homeworks:
                send_message(bot, parse_status(homeworks[0]))

            timestamp = response.get('current_date', timestamp)
        except Exception as error:
            message = ERROR_MESSAGE.format(error)
            logging.exception(message)

            try:
                bot.send_message(TELEGRAM_CHAT_ID, message)
            except Exception as error:
                logging.exception(SEND_MESSAGE_ERROR.format(error))

        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(__file__ + '.log', encoding='UTF-8')],
        format=(
            '%(asctime)s, %(levelname)s, %(funcName)s, %(lineno)d, %(message)s'
        ))
    main()
