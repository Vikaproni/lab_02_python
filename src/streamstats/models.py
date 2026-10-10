'''Валидация строк'''
from datetime import datetime

from streamstats.errors import IncorrectEventError, IncorrectTimestampError

fields = ('timestamp','level','source','message') #допустимые названия полей
permitted_value_level = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') #допустимые уровни событий

def validation(provided_line:dict) -> dict:

    #Нахождение пустых значений в словаре
    for field in fields:
        if not provided_line.get(field):
            raise IncorrectEventError(f'{field}: Пустое значение или отсутствие поля')

    #Нахождение некорректно введенных данных
    for name in fields:
        if not isinstance(provided_line[name], str): #проверка, является ли значение строкой
            raise IncorrectEventError(f'{name}: Неверный формат данных')

    provided_line['level'] = provided_line['level'].upper() #приведение к нормализованному виду значений level
    #Нахождение недопустимого значения поля evel
    if provided_line['level'] not in permitted_value_level:
        raise IncorrectEventError('level: Неверно введено значение поля')

    #Определение корректности формата введенного значения времени
    try:
        provided_line['timestamp'] = datetime.fromisoformat(provided_line['timestamp'])
    except ValueError as exc:
        raise IncorrectTimestampError('timestamp: Некорректный формат времени') from exc

    return provided_line

