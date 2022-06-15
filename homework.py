import time
import logging
from http import HTTPStatus

import telegram
import requests

from requests.exceptions import RequestException

import constants as c
import error_exceptions as e


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(c.TELEGRAM_CHAT_ID, text=message)
    except telegram.error.Conflict as error:
        logging.error(c.SEND_MESSAGE_ERROR.format(error=error))

    return logging.info(c.SEND_MESSAGE_INFO_LOG.format(message))


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = dict(
        url=c.ENDPOINT, headers={'Authorization': f'OAuth {c.PRACTICUM_TOKEN}'},
        params={'from_date': current_timestamp}
    )
    try:
        response = requests.get(**params, timeout=30)
    except RequestException as error:
        raise ConnectionError(
            c.API_ANSWER_ERROR.format(error=error, **params))

    status_code = response.status_code

    if not status_code == HTTPStatus.OK:
        raise e.StatusCodeErrorException(
            c.STATUS_CODE_ERROR.format(status_code=status_code, **params)
        )

    response_json = response.json()

    for key in ('error', 'code'):
        if key in response_json:
            raise e.ResponseErrorException(
                c.RESPONSE_ERROR.format(
                    error=response_json[key], key=key, **params
                )
            )
    return response_json


def check_response(response):
    """Проверяет ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError(c.NOT_DICT_RESPONSE)

    if 'homeworks' not in response:
        raise ValueError(c.HOMEWORK_NOT_IN_RESPONSE)

    homework = response['homeworks']

    if type(homework) is not list:
        raise TypeError(c.HOMEWORK_IS_NOT_LIST)

    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""
    status = homework['status']

    if 'homework_name' not in homework:
        raise KeyError(c.HOMEWORK_NAME_NOT_FOUND)

    if status not in c.VERDICTS:
        raise ValueError(c.UNKNOWN_STATUS_ERROR.format(status))

    return c.CHANGED_STATUS.format(
        homework['homework_name'], c.VERDICTS.get(status))


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = all([c.PRACTICUM_TOKEN, c.TELEGRAM_TOKEN, c.TELEGRAM_CHAT_ID])
    return tokens or logging.critical(c.TOKEN_NOT_FOUND.format(tokens))


def main():
    """Основная логика работы программы."""
    if not check_tokens():
        raise e.TokenErrorException(c.TOKEN_ERROR)

    bot = telegram.Bot(token=c.TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_exception_msg = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)

            if homework:
                send_message(bot, parse_status(homework[0]))

            timestamp = response.get('current_date', timestamp)

        except Exception as error:
            message = c.ERROR_MESSAGE.format(error)
            logging.exception(message)

            if not last_exception_msg == message:
                successfully_sending: bool = bot.send_message(
                    c.TELEGRAM_CHAT_ID, message
                )
                if successfully_sending:
                    last_exception_msg = message

        time.sleep(c.RETRY_TIME)


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
