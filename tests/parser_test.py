import pytest

from streamstats.errors import IncorrectEventError
from streamstats.parsers import parser_csv, parser_json


def test_normal_line_csv():
    '''Тест корректной строки, приходящей из csv-файла'''
    assert parser_csv('2026-01-10T09:11:02,CRITICAL,server1,Диск заполнен на 99%') == {'timestamp':'2026-01-10T09:11:02',
                    'level':'CRITICAL','source':'server1','message':'Диск заполнен на 99%'}

def test_comma_in_message_csv():
    '''Тест корректной строки, приходящей из csv-файла, с запятой в "message" '''
    assert parser_csv('2026-01-10T09:10:45,ERROR,server2,Таймаут, соединение с базой данных') == {'timestamp':'2026-01-10T09:10:45',
                    'level':'ERROR','source':'server2','message':'Таймаут, соединение с базой данных'}

def test_normal_line_jsonl():
    '''Тест корректной строки, приходящей из jsonl-файла (вывод должен совпадать с выводом первого теста)'''
    assert (parser_json('{"timestamp": "2026-01-10T09:11:02", "level": "CRITICAL", "source": "server1", "message": "Диск заполнен на 99%"}')
            == {'timestamp':'2026-01-10T09:11:02','level':'CRITICAL','source':'server1','message':'Диск заполнен на 99%'})

def test_other_separator():
    '''Тест строки из csv-файла с разделителем ";" '''
    assert parser_csv('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%',separator=';') == {'timestamp':'2026-01-10T09:11:02',
                    'level':'CRITICAL','source':'server1','message':'Диск заполнен на 99%'}

def test_unicode_escape_in_json():
    '''Тест строки из jsonl-файла с unicode-escape-последовательностью'''

    assert parser_json('{"timestamp":"2026-01-10T09:05","level":"INFO","source":"server1","message":"\\u0417\\u0430\\u043f\\u0440\\u043e\\u0441"}') == {'timestamp':'2026-01-10T09:05',
                    'level':'INFO','source':'server1','message':'Запрос'}

def test_unicode_escape_in_csv():
    '''Тест строки из csv-файла с unicode-escape-последовательностью'''
    assert parser_csv('2026-01-10T09:11:02,CRITICAL,server1,Запрос на /api/users обработан за 12 мс') == {'timestamp':'2026-01-10T09:11:02',
                    'level':'CRITICAL','source':'server1','message':'Запрос на /api/users обработан за 12 мс'}

def test_missing_field_csv():
    '''Тест строки из csv-файла с отсутствием данных для поля "message" '''
    with pytest.raises(IncorrectEventError, match = 'Не хватает данных'):
        parser_csv('2026-01-10T09:11:02,CRITICAL,server1')

def test_empty_line_csv():
    '''Тест пустой строки из csv-файла'''
    with pytest.raises(IncorrectEventError, match = 'Пустая строка'):
        parser_csv('')

def test_not_jsonl():
    '''Тест строки из jsonl-файла, у которой отсутствует "{" '''
    with pytest.raises(IncorrectEventError, match = 'Ожидался JSON-объект'):
        parser_json('"timestamp": "2026-01-10T09:05", "level": "DEBUG", "source": "server3", "message": "Запрос на /api/users обработан за 12 мс"}')

def test_empty_line_jsonl():
    '''Тест пустой строки из jsonl-файла'''
    with pytest.raises(IncorrectEventError, match = 'Пустая строка'):
        parser_json('')

def test_expect_key_jsonl():
    '''Тест строки из jsonl-файла, у которой есть ключ, который начинается не с " '''
    with pytest.raises(IncorrectEventError, match = 'Ожидался ключ'):
        parser_json('{"timestamp": "2026-01-10T09:05", level": "DEBUG", "source": "server3", "message": "Запрос на /api/users обработан за 12 мс"}')

def test_shielding_in_key_jsonl():
    '''Тест строки из jsonl-файла, у которой есть некорректный ключ'''
    with pytest.raises(IncorrectEventError, match = 'Некорректно введен ключ'):
        parser_json('{"\\timestamp": "2026-01-10T09:05", "level": "DEBUG", "source": "server3", "message": "Запрос на /api/users обработан за 12 мс"}')

def test_missing_colon_jsonl():
    '''Тест строки из jsonl-файла, у которой нет ":" между ключом и значением'''
    with pytest.raises(IncorrectEventError, match = 'Ожидалось двоеточие'):
        parser_json('{"timestamp" "2026-01-10T09:05", "level": "DEBUG", "source": "server3", "message": "Запрос на /api/users обработан за 12 мс"}')

def test_unsupported_format_dates_jsonl():
    '''Тест строки из jsonl-файла, у которой неправильный формат значения (не строка)'''
    with pytest.raises(IncorrectEventError, match = 'Неподдерживаемый формат данных'):
        parser_json('{"timestamp": 123, "level": "DEBUG", "source": "server3", "message": "Запрос на /api/users обработан за 12 мс"}')

def test_uncorrectable_unicode_escape_jsonl():
    '''Тест строки из jsonl-файла, у которой в unicode-escape-последовательности символы не 0-9, a-z, A-Z'''
    with pytest.raises(IncorrectEventError, match = 'Некорректные сиволы в unicode-escape-последовательности'):
        parser_json('{"timestamp": "2026-01-10T09:05", "level": "DEBUG", "source": "server3", "message": "\\u0щ17\\u0а30"}')