import pytest
from datetime import datetime
from streamstats.reader import read_file

def test_read_csv(tmp_path):
    '''Тест чтения csv-файла с заголовком с использованием временного каталога, чтобы не создавать мусор в проекте'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('timestamp,level,source,message\n'
                           '2026-01-10T09:02:30,INFO,server2,Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30,WARNING,server3,Загрузка данных\n',encoding='utf8')
    assert list(read_file(str(input_dates),'csv')) == [(2,{'timestamp': datetime(2026, 1, 10, 9, 2, 30), 'level': 'INFO', 'source': 'server2',
      'message': 'Высокая загрузка процессора: 85%'}),(3,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_read_csv_other_separator(tmp_path):
    '''Тест чтения csv-файла без заголовка и с разделителем ";" с использованием временного каталога'''
    input_dates = tmp_path / "input_dates.csv"
    input_dates.write_text('2026-01-10T09:02:30;INFO;server2;Высокая загрузка процессора: 85%\n'
                           '2026-01-10T10:15:30;WARNING;server3;Загрузка данных\n',encoding='utf8')
    assert list(read_file(str(input_dates),'csv')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 30), 'level': 'INFO', 'source': 'server2',
      'message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_read_jsonl(tmp_path):
    '''Тест чтения jsonl-файла с использованием временного каталога'''
    input_dates = tmp_path / "input_dates.jsonl"
    input_dates.write_text('{"timestamp":"2026-01-10T09:02:30","level":"INFO","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf8')
    assert list(read_file(str(input_dates),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 30), 'level': 'INFO', 'source': 'server2',
      'message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]

def test_read_many_files_jsonl(tmp_path):
    '''Тест чтения нескольких разных jsonl-файлов с использованием временного каталога'''
    input_dates1 = tmp_path / "input_dates1.jsonl"
    input_dates1.write_text('{"timestamp":"2026-01-10T09:02:30","level":"INFO","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf8')
    input_dates2 = tmp_path / "input_dates2.jsonl"
    input_dates2.write_text('{"timestamp":"2026-01-10T09:02:20","level":"ERROR","source":"server4", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:17","level":"INFO","source":"server3","message":"Загрузка данных"}\n',encoding='utf8')
    input_dates3 = tmp_path / "input_dates3.jsonl"
    input_dates3.write_text('{"timestamp":"2026-01-10T09:02:28","level":"DEBUG","source":"server1", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:31","level":"CRITICAL","source":"server5","message":"Загрузка данных"}\n',encoding='utf8')
    assert list(read_file(str(input_dates1),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 30),
        'level': 'INFO', 'source': 'server2','message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'})]
    assert list(read_file(str(input_dates2),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 20),
        'level': 'ERROR', 'source': 'server4','message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 17),
        'level': 'INFO', 'source': 'server3', 'message': 'Загрузка данных'})]
    assert list(read_file(str(input_dates3),'jsonl')) == [(1,{'timestamp': datetime(2026, 1, 10, 9, 2, 28),
        'level': 'DEBUG', 'source': 'server1', 'message': 'Высокая загрузка процессора: 85%'}),(2,{'timestamp': datetime(2026, 1, 10, 10, 15, 31),
        'level': 'CRITICAL', 'source': 'server5', 'message': 'Загрузка данных'})]

