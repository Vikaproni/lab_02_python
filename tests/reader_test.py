from datetime import datetime

import pytest

from streamstats.errors import IncorrectEventError, IncorrectTimestampError
from streamstats.reader import read_file


def test_read_csv(tmp_path):
    '''Тест чтения csv-файла с заголовком с использованием временного каталога, чтобы не создавать мусор в проекте'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('timestamp,level,source,message\n'
                           '2026-01-10T09:02:30,INFO,server2,Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30,WARNING,server3,Загрузка данных\n',encoding='utf-8')
    assert list(read_file(str(input_dates),'csv')) == [(2,{'timestamp': datetime(2026, 1, 10, 9, 2, 30), 'level': 'INFO', 'source': 'server2',
      'message': 'Высокая загрузка процессора: 85%'}),(3,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_read_csv_other_separator(tmp_path):
    '''Тест чтения csv-файла без заголовка и с разделителем ";" с использованием временного каталога'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('2026-01-10T09:02:30;INFO;server2;Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30;WARNING;server3;Загрузка данных\n',encoding='utf-8')
    assert list(read_file(str(input_dates),'csv')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 30), 'level': 'INFO', 'source': 'server2',
      'message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_read_jsonl(tmp_path):
    '''Тест чтения jsonl-файла с использованием временного каталога'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('{"timestamp":"2026-01-10T09:02:30","level":"INFO","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    assert list(read_file(str(input_dates),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 30), 'level': 'INFO', 'source': 'server2',
      'message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_read_many_files_jsonl(tmp_path):
    '''Тест чтения нескольких разных jsonl-файлов с использованием временного каталога, проверяет, что read_file е зависит от конкретного файла, каждый вызов независим'''
    input_dates1 = tmp_path / "input_dates1.jsonl"
    input_dates1.write_text('{"timestamp":"2026-01-10T09:02:30","level":"INFO","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    input_dates2 = tmp_path / "input_dates2.jsonl"
    input_dates2.write_text('{"timestamp":"2026-01-10T09:02:20","level":"ERROR","source":"server4", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:17","level":"INFO","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    input_dates3 = tmp_path / "input_dates3.jsonl"
    input_dates3.write_text('{"timestamp":"2026-01-10T09:02:28","level":"DEBUG","source":"server1", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:31","level":"CRITICAL","source":"server5","message":"Загрузка данных"}\n',encoding='utf-8')
    assert list(read_file(str(input_dates1),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 30),
        'level': 'INFO', 'source': 'server2','message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]
    assert list(read_file(str(input_dates2),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 20),
        'level': 'ERROR', 'source': 'server4','message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 17),
        'level': 'INFO', 'source': 'server3', 'message': 'Загрузка данных'})]
    assert list(read_file(str(input_dates3),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 28),
        'level': 'DEBUG', 'source': 'server1', 'message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 31),
        'level': 'CRITICAL', 'source': 'server5', 'message': 'Загрузка данных'})]

def test_empty_csv(tmp_path):
    '''Проверка чтения пустого csv-файла, должен вернуть пустой список'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('',encoding='utf-8')
    assert list(read_file(str(input_dates),'csv')) == []

def test_empty_jsonl(tmp_path):
    '''Проверка чтения пустого json-файла, должен вернуть пустой список'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('',encoding='utf-8')
    assert list(read_file(str(input_dates),'jsonl')) == []

def test_invalid_skip_csv(tmp_path):
    '''Проверка чтения csv-файла в режиме skip_invalid с неправильным событием'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('timestamp,level,source,message\n'
                           '2026-01-10T09:02:30,lalala,server2,Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30,WARNING,server3,Загрузка данных\n',encoding='utf8')
    assert list(read_file(str(input_dates),'csv',skip_invalid=True)) == [(3,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_invalid_skip_jsonl(tmp_path):
    '''Проверка чтения jsonl-файла в режиме skip_invalid с неправильным событием'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('{"timestamp":"2026-01-10T09:02:30","level":"lalala","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    skipped = [0]

    assert list(read_file(str(input_dates),'jsonl',skip_invalid=True,skipped=skipped)) == [(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]
    assert skipped[0] == 1

def test_unicode_jsonl(tmp_path):
    '''Проверка чтения jsonl-файла c unicode-escape-последовательностью'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('{"timestamp": "2026-01-10T09:00:01", "level": "INFO", "source": "server1", "message": "\\u0417\\u0430\\u043f\\u0440\\u043e\\u0441"}',encoding='utf-8')
    assert list(read_file(str(input_dates),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 0, 1),
        'level': 'INFO', 'source': 'server1', 'message': 'Запрос'})]

def test_error_seven_jsonl(tmp_path):
    '''Проверка чтения jsonl-файла c шибкой в 7й строке, должен вывести поле, в котором ошибка, номер строки, тип ошибки'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('{"timestamp": "2026-01-10T09:00:01", "level": "INFO", "source": "server1", "message": "Загрузка данных"}\n'
                           '{"timestamp": "2026-01-10T09:00:01", "level": "INFO", "source": "server1", "message": "Загрузка данных"}\n'
                           '\n''\n''\n''\n'
                           '{"timestamp": "2026-01-10T09:00:01", "level": "дфдфдф", "source": "server1", "message": "Загрузка данных"}\n',encoding='utf-8')
    with pytest.raises(IncorrectEventError,match=': строка 7:'):
        list(read_file(str(input_dates),'jsonl'))

def test_invalid_no_skip_csv(tmp_path):
    '''Проверка чтения csv-файла без skip_invalid с неправильным событием'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('timestamp,level,source,message\n'
                           '2026-01-10T09:02:30,lalala,server2,Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30,WARNING,server3,Загрузка данных\n',encoding='utf-8')
    with pytest.raises(IncorrectEventError):
        list(read_file(str(input_dates),'csv'))

def test_invalid_no_skip_jsonl(tmp_path):
    '''Проверка чтения jsonl-файла без skip_invalid с неправильным событием'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('{"timestamp":"123","level":"lalala","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    with pytest.raises(IncorrectEventError):
        list(read_file(str(input_dates),'jsonl'))

def test_invalid_time_no_skip_csv(tmp_path):
    '''Проверка чтения csv-файла без skip_invalid с неправильным форматом времени'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('timestamp,level,source,message\n'
                           '11.02.11,INFO,server2,Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30,WARNING,server3,Загрузка данных\n',encoding='utf-8')
    with pytest.raises(IncorrectTimestampError):
        list(read_file(str(input_dates),'csv'))