from datetime import datetime

from streamstats.analysis import (
    analyze,
    final_statistics,
    new_statistics,
    top_source_errors,
)
from streamstats.reader import read_file


def test_count_all_events():
    '''Тест счетчика событий в функции анализа'''
    stat = new_statistics()
    analyze({'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'},stat)
    assert stat['total_events'] == 1

def test_count_levels_events():
    '''Тест счетчика уровней в функции анализа'''
    stat = new_statistics()
    analyze({'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'},stat)
    assert stat['count_levels'] == {'DEBUG': 0, 'INFO': 0, 'WARNING': 1, 'ERROR': 0, 'CRITICAL': 0}

def test_count_source_events():
    '''Тест счетчика различных источников ошибок в функции анализа'''
    stat = new_statistics()
    for input_dates in ({'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'},{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server2', 'message': 'Загрузка данных'},{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'},{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server1', 'message': 'Загрузка данных'}):

        analyze(input_dates,stat)
    assert stat['count_source'] == {'server3': 2, 'server2': 1, 'server1': 1}

def test_first_timestamp_events():
    '''Тест определения самого ранней временной метки в функции анализа'''
    stat = new_statistics()
    for dict in ({'timestamp': datetime(2026, 1, 10, 10, 18, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'},{'timestamp': datetime(2026, 1, 10, 10, 16, 30),
        'level': 'WARNING', 'source': 'server2', 'message': 'Загрузка данных'},{'timestamp': datetime(2026, 1, 10, 10, 15, 30),
        'level': 'WARNING', 'source': 'server3', 'message': 'Загрузка данных'},{'timestamp': datetime(2026, 1, 10, 10, 17, 30),
        'level': 'WARNING', 'source': 'server1', 'message': 'Загрузка данных'}):

        analyze(dict,stat)
    assert stat['first_timestamp'] == datetime(2026, 1, 10, 10, 15, 30)

def test_top_source():
    '''Тест счетчика топ-5 различных источников ошибок ERROR/CRITICAL в функции анализа'''
    assert top_source_errors({'server3': 2, 'server2': 1,'server1': 1}) == [{'source': 'server3', 'count': 2}, {'source': 'server1', 'count': 1}, {'source': 'server2', 'count': 1}]

def test_many_files_analysis(tmp_path):
    '''Тест на статистику сразу нескольких файлов'''
    input_dates1 = tmp_path / "input_dates1.jsonl"
    input_dates1.write_text('{"timestamp":"2026-01-10T09:02:30","level":"INFO","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    input_dates2 = tmp_path / "input_dates2.jsonl"
    input_dates2.write_text('{"timestamp":"2026-01-10T09:02:20","level":"ERROR","source":"server4", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:17","level":"INFO","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    input_dates3 = tmp_path / "input_dates3.jsonl"
    input_dates3.write_text('{"timestamp":"2026-01-10T09:02:28","level":"DEBUG","source":"server1", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:31","level":"CRITICAL","source":"server5","message":"Загрузка данных"}\n',encoding='utf-8')

    statistics = new_statistics()

    for file in (input_dates1, input_dates2, input_dates3):
        for line_number, line in read_file(file,'jsonl'):
            analyze(line,statistics)

    assert final_statistics(statistics) == {"total_events": 6,"count_levels": {"DEBUG": 1,"INFO": 2,"WARNING": 1,"ERROR": 1,
  "CRITICAL": 1},"count_source": {"server1": 1,"server2": 1,"server3": 2,"server4": 1,"server5": 1},"source_errors": [{"source": "server4","count": 1},
  {"source": "server5","count": 1}],"first_timestamp": "2026-01-10T09:02:20","last_timestamp": "2026-01-10T10:15:31",
  "skipped": 0}

def test_many_files_with_invalid(tmp_path):
    '''Тест на статистику сразу нескольких файлов со некорректной строкой'''
    input_dates1 = tmp_path / "input_dates1.jsonl"
    input_dates1.write_text('{"timestamp":"2026-01-10T09:02:30","level":"lalala","source":"server2", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:30","level":"WARNING","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    input_dates2 = tmp_path / "input_dates2.jsonl"
    input_dates2.write_text('{"timestamp":"2026-01-10T09:02:20","level":"ERROR","source":"server4", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:17","level":"INFO","source":"server3","message":"Загрузка данных"}\n',encoding='utf-8')
    input_dates3 = tmp_path / "input_dates3.jsonl"
    input_dates3.write_text('{"timestamp":"2026-01-10T09:02:28","level":"DEBUG","source":"server1", "message":"Высокая загрузка процессора: 85%"}\n'
                           '{"timestamp":"2026-01-10T10:15:31","level":"CRITICAL","source":"server5","message":"Загрузка данных"}\n',encoding='utf-8')

    statistics = new_statistics()
    skipped = [0]

    for file in (input_dates1, input_dates2, input_dates3):
        for line_number, line in read_file(str(file),'jsonl',skip_invalid=True,skipped=skipped):
            analyze(line,statistics)

    assert final_statistics(statistics,skipped=skipped[0]) == {"total_events": 5,"count_levels": {"DEBUG": 1,"INFO": 1,"WARNING": 1,"ERROR": 1,
  "CRITICAL": 1},"count_source": {"server1": 1,"server3": 2,"server4": 1,"server5": 1},"source_errors": [{"source": "server4","count": 1},
  {"source": "server5","count": 1}],"first_timestamp": "2026-01-10T09:02:20","last_timestamp": "2026-01-10T10:15:31",
  "skipped": 1}
