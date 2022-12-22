import os
import logging
import time
import requests

import telegram

from exceptions import (
    StatusCodeIsNot200,
    RequiredVariablesAbsent,
)
from http import HTTPStatus
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    return False


def send_message(bot: telegram.bot.Bot, message: str):
    """Отправляет сообщение в телеграмм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(f'Сообщение удачно отправлено: {message}!')
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp: int):
    """Получает ответ API."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise StatusCodeIsNot200(
                homework_statuses.status_code,
                HTTPStatus.OK
            )
        else:
            return homework_statuses.json()
    except Exception as error:
        logging.error(f'Ошибка при запросе к API: {error}')
        raise Exception(f'Ошибка при запросе к API: {error}')


def check_response(response: dict):
    """Проверяет ответ API на соответствие документации."""
    response_keys = ['homeworks', 'current_date']
    try:
        if (isinstance(response, dict) is False
                or isinstance(response['homeworks'], list) is False):
            raise TypeError
        for key in response_keys:
            if key not in response.keys():
                raise KeyError
        if len(response['homeworks']) == 0:
            raise TypeError
        return True
    except TypeError as error:
        logging.error(
            f'Ответ API не соответствует документации: {error}'
        )
        raise TypeError(f'Ответ API не соответствует документации: {error}')
    except KeyError as error:
        logging.error(
            f'Отсутствие ожидаемых ключей в ответе API: {error}'
        )
        raise KeyError(f'Отсутствие ожидаемых ключей в ответе API: {error}')
    except Exception as error:
        logging.error(f'Ответ api не соответствует документации: {error}')
        raise Exception(f'Ответ api не соответствует документации: {error}')


def parse_status(homework: dict):
    """Извлекает из информации о домашней работе статус этой работы."""
    try:
        if homework['status'] in HOMEWORK_VERDICTS.keys():
            if 'homework_name' in homework.keys():
                homework_name = homework['homework_name']
            else:
                raise KeyError
            return (
                f'Изменился статус проверки работы '
                f'"{homework_name}". '
                f'{HOMEWORK_VERDICTS[homework["status"]]}'
            )
        else:
            raise TypeError
    except TypeError as error:
        logging.error(f'Получен недокументированный статус домашки: {error}')
        raise TypeError('Получен недокументированный статус домашки: {error}')
    except KeyError as error:
        logging.error(
            f'В ответе API домашки нет ключа '
            f'`homework_name`: {error}'
        )
        raise KeyError(
            f'В ответе API домашки нет ключа '
            f'`homework_name`: {error}'
        )
    except Exception as error:
        logging.error(error)
        raise Exception(error)


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        timestamp = 0
        previous_status = ''
        while True:
            try:
                response = get_api_answer(timestamp)
                if check_response(response) is True:
                    status = parse_status(response['homeworks'][0])
                    if status != previous_status:
                        send_message(bot, status)
                        previous_status = str(status)
            except StatusCodeIsNot200 as error:
                logging.error(error)
                raise StatusCodeIsNot200(error)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                logging.error(message)
            time.sleep(RETRY_PERIOD)
    else:
        logging.critical('Отсутствуют обязательные переменные окружения!')
        raise RequiredVariablesAbsent(
            'Отсутствуют обязательные переменные окружения!'
        )


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename='mylog.log',
        filemode='a'
    )
    main()
