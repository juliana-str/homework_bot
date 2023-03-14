import logging
import os
import time
from http import HTTPStatus

import requests
import telegram

from dotenv import load_dotenv

from exeptions import GetAPIError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
RETRY_PERIOD = 600


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка корректности указанных токенов."""
    if not PRACTICUM_TOKEN:
        logger.critical('Отсутствуют необходимый токен: PRACTICUM_TOKEN!')
        raise SystemExit('Нет необходимых токенов.')
    if not TELEGRAM_TOKEN:
        logger.critical('Отсутствуют необходимый токен: TELEGRAM_TOKEN!')
        raise SystemExit('Нет необходимых токенов.')
    if not TELEGRAM_CHAT_ID:
        logger.critical('Отсутствуют необходимый токен: TELEGRAM_CHAT_ID!')
        raise SystemExit('Нет необходимых токенов.')
    return True


def send_message(bot, message):
    """Отправка сообщения в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено.')
    except telegram.error.TelegramError:
        logger.error('Сообщение не отправлено!', exc_info=True)


def get_api_answer(timestamp):
    """Получение ответа от API."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(f'Нет ответа, код ошибки: {response.status_code}.')
    except requests.RequestException:
        raise GetAPIError(
            f'Нет ответа на запрос! Параметры запроса: '
            f'{ENDPOINT}, {HEADERS}, {timestamp}.'
            f'{response.status_code}'
        )
    return response.json()


def check_response(response):
    """Проверка ответа."""
    if not (isinstance(response, dict)
            and isinstance(response.get('homeworks'), list)):
        raise TypeError('Неверный формат данных.')
    if 'homeworks' not in response:
        raise KeyError('Нет такого ключа.')
    return True


def parse_status(homework):
    """Обновление статуса проверки работы."""
    if 'homework_name' not in homework:
        raise KeyError("В API домашки нет ключа 'homework_name'.")
    if 'status' not in homework:
        raise KeyError("В API домашки нет ключа 'status'.")
    if homework.get('status') not in HOMEWORK_VERDICTS:
        raise KeyError('Недокументированный статус домашней работы.')

    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    homework_name = homework.get('homework_name')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = {'from_date': int(time.time())}
    check_tokens()
    previous_answer = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homework = response.get('homeworks')
            if len(homework) != 0:
                answer = parse_status(homework[0])
                logger.debug(answer)

                if previous_answer != answer:
                    send_message(bot, answer)
                    previous_answer = answer
                timestamp['from_date'] = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}.'
            send_message(bot, message)
            logger.error(f'Сбой в работе программы: {error}.', exc_info=True)

        time.sleep(RETRY_PERIOD)


logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    main()
