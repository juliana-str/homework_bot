import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram

from telegram.ext import Updater
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
    tokens = [PRACTICUM_TOKEN,
              TELEGRAM_TOKEN,
              TELEGRAM_CHAT_ID
              ]
    for token in tokens:
        if not isinstance(token, str):
            logger.critical('Отсутствуют необходимые токены!')
            raise SystemExit('Нет необходимых токенов.')
    return len(tokens) == 3


def send_message(bot, message):
    """Отправка сообщения в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(message)
    except Exception as error:
        logging.error(error)


def get_api_answer(timestamp):
    """Получение ответа от API."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
    except requests.RequestException as error:
        logging.error(error)

    if response.status_code != HTTPStatus.OK:
        logging.error('Нет ответа на запрос.')
        raise ConnectionError

    response = response.json()
    if not isinstance(response, dict):
        logging.error('Неверный формат данных.')
        raise TypeError
    return response


def check_response(response):
    """Проверка ответа."""
    if not response or len(response)==0:
        logging.error('Ответа нет.')
        raise ValueError
    if not isinstance(response, dict):
        logging.error('Неверный формат данных.')
        raise TypeError
    if 'homeworks' not in response:
        logging.error('Нет такого ключа.')
        raise KeyError
    if not isinstance(response.get('homeworks'), list):
        logging.error('Неверный формат данных.')
        raise TypeError
    return response.get('homeworks')


def parse_status(homework):
    """Обновление статуса проверки работы."""
    if 'status' not in homework:
        raise KeyError
    if 'homework_name' not in homework:
        raise KeyError
    if homework.get('status') not in HOMEWORK_VERDICTS:
        raise KeyError
    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    homework_name = homework.get('homework_name')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = {'from_date': int(time.time() - 5184000)}
    if not check_tokens():
        logger.critical('Отсутствуют необходимые токены!')
        sys.stdin.close()
    previous_answer = ''
    response = get_api_answer(timestamp)
    homeworks = check_response(response)

    while True:
        if homeworks is None:
            logger.critical('Отсутствуют данные!')
            break
        for homework in homeworks:
            answer = parse_status(homework)
            if HOMEWORK_VERDICTS.get('approved') not in answer:
                previous_answer = answer
            try:
                answer = parse_status(homework)
                if previous_answer != answer:
                    send_message(bot, answer)
                    previous_answer = answer
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)

        timestamp['from_date'] = response.get('current_date')
        time.sleep(RETRY_PERIOD)
        updater = Updater(token=TELEGRAM_TOKEN)
        updater.start_polling()
        updater.idle()

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


if __name__ == '__main__':
    main()
