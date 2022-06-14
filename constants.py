import os

from dotenv import load_dotenv

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
