import pytest

from streamstats.models import validation
from streamstats.errors import IncorrectEventError, IncorrectTimestampError

def test_correct_dict():
    '''Проверка корректной строки'''
    assert validation({'timestamp':'2026-01-10T09:10:45',
                    'level':'ERROR','source':'server2','message':'Таймаут, соединение с базой данных'})

def test_correct_dict_2():
    '''Проверка корректной строки №2'''
    assert validation({'timestamp':'2026-01-10T09:11:02','level':'CRITICAL','source':'server1',
                       'message':'Запрос на /api/users обработан за 12 мс'})

def test_correct_dict_3():
    '''Проверка корректной строки'''
    assert validation({'timestamp':'2026-01-10T09:10:45',
                    'level':'error','source':'server2','message':'Таймаут, соединение с базой данных'})

def test_empty_value():
    '''Проверка словаря с пустым значением '''
    with pytest.raises(IncorrectEventError, match = 'Пустое значение или отсутствие поля'):
        validation({'timestamp':'2026-01-10T09:11:02','level':'','source':'server1',
                       'message':'Запрос на /api/users обработан за 12 мс'})

def test_empty_key():
    '''Проверка словаря с пустым значением '''
    with pytest.raises(IncorrectEventError, match = 'Пустое значение или отсутствие поля'):
        validation({'':'2026-01-10T09:11:02','level':'','source':'server1',
                       'message':'Запрос на /api/users обработан за 12 мс'})

def test_uncorrectable_value():
    '''Проверка словаря со значенеием, не являющимся строкой '''
    with pytest.raises(IncorrectEventError, match = 'Неверный формат данных'):
        validation({'timestamp':'2026-01-10T09:11:02','level':'CRITICAL','source':345,
                       'message':'Запрос на /api/users обработан за 12 мс'})

def test_uncorrectable_value_bool():
    '''Проверка словаря со значенеием, не являющимся строкой '''
    with pytest.raises(IncorrectEventError, match = 'Неверный формат данных'):
        validation({'timestamp':'2026-01-10T09:11:02','level':'CRITICAL','source': True,
                       'message':'Запрос на /api/users обработан за 12 мс'})

def test_uncorrectable_value_in_level():
    '''Недопустимое значение "level" '''
    with pytest.raises(IncorrectEventError, match = 'level: Неверно введено значение поля'):
        validation({'timestamp':'2026-01-10T09:11:02','level':'lalalala','source':'server1',
                       'message':'Запрос на /api/users обработан за 12 мс'})

def test_uncorrectable_value_in_timestamp():
    '''Недопустимое значение "timestamp" '''
    with pytest.raises(IncorrectTimestampError, match = 'timestamp: Некорректный формат времени'):
        validation({'timestamp':'11.22.33','level':'INFO','source':'server1',
                       'message':'Запрос на /api/users обработан за 12 мс'})