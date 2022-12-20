from homework import HOMEWORK_VERDICTS

my_homework = {
    'homework_name': 'HW'
}


def parse_status(homework):
    try:
        verdict = HOMEWORK_VERDICTS[homework['status']]
        homework_name = homework['homework_name']
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        print(1)
        raise KeyError('Исключение')

parse_status(my_homework)
