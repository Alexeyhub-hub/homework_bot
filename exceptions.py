
class CustomErrors(Exception):
    pass


class StatusCodeIsNot200(CustomErrors):
    """Вызывается, когда API домашки возвращает код, отличный от 200"""
    def __init__(self, status, expected_status):
        self.status = status
        self.expected_status = expected_status

    def __str__(self):
        return f'Код ответа из API {self.status} не равен {self.expected_status}!'


class RequiredVariablesAbsent(CustomErrors):
    """Вызывается, когда отсутствуют обязательные переменные окружения"""
    def __str__(self):
        return f'Отсутствуют обязательные переменные окружения!'






