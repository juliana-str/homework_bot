import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram

from dotenv import load_dotenv


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


def send_message(bot, message):  # без логгирования не проходят тесты
    """Отправка сообщения в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено.')
    except Exception:
        logging.error('Сообщение не отправлено!')
        raise Exception('Сообщение не отправлено!')


def get_api_answer(timestamp):
    """Получение ответа от API."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError
    except requests.RequestException:
        raise Exception('Нет ответа на запрос!')
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
        if not get_api_answer(timestamp):
            logging.error('Нет ответа на запрос.')
        response = get_api_answer(timestamp)
        if not check_response(response):
            logging.error('Неверный формат данных.')
        homework = response.get('homeworks')
        if homework is None:
            logging.error('Отсутствуют данные!')
        try:
            answer = parse_status(homework[0])
            logging.debug(f'Статус проверки работы {answer}.')
            if HOMEWORK_VERDICTS.get('approved') not in answer:
                previous_answer = answer
            if previous_answer != answer:
                send_message(bot, answer)
                previous_answer = answer
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}.')

        timestamp['from_date'] = response.get('current_date')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
