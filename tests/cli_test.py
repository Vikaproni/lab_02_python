import json

import pytest

from streamstats.__main__ import main


def test_cli_analyze_csv(tmp_path):
    '''Проверка корректного csv_файла '''
    input_dates = tmp_path / 'input_dates.csv'
    input_dates.write_text('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%\n'
                           '2026-01-10T09:11:12;ERROR;server1;Диск заполнен на 99%\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates),'--format','csv','--output',str(output_dates)])
    result = json.loads(output_dates.read_text(encoding='utf-8'))

    assert result == {'total_events': 2,
                      'count_levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 1, 'CRITICAL': 1},
                      'count_source': {'server1': 2},
                      'source_errors': [{'source': 'server1', 'count': 2}],
                      'first_timestamp': '2026-01-10T09:11:02', 'last_timestamp': '2026-01-10T09:11:12', 'skipped': 0}

def test_cli_analyze_jsonl(tmp_path):
    '''Проверка корректного jsonl-файла, отчеты с прошлым тестом одинаковы, тк данные в файлах jsonl и csv одинаковы'''
    input_dates = tmp_path / 'input_dates.jsonl'
    input_dates.write_text('{"timestamp":"2026-01-10T09:11:02","level":"CRITICAL","source":"server1","message":"Диск заполнен на 99%"}\n'
                           '{"timestamp":"2026-01-10T09:11:12","level":"ERROR","source":"server1","message":"Диск заполнен на 99%"}\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates),'--format','jsonl','--output',str(output_dates)])
    result = json.loads(output_dates.read_text(encoding='utf-8'))

    assert result == {'total_events': 2,
                      'count_levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 1, 'CRITICAL': 1},
                      'count_source': {'server1': 2},
                      'source_errors': [{'source': 'server1', 'count': 2}],
                      'first_timestamp': '2026-01-10T09:11:02', 'last_timestamp': '2026-01-10T09:11:12', 'skipped': 0}

def test_many_cli_analyze(tmp_path):
    '''Проверка нескольких корректных файлов '''
    input_dates1 = tmp_path / 'input_dates1.csv'
    input_dates1.write_text('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%\n', encoding='utf-8')
    input_dates2 = tmp_path / 'input_dates2.csv'
    input_dates2.write_text('2026-01-10T09:11:10;CRITICAL;server2;Диск заполнен на 99%\n', encoding='utf-8')
    input_dates3 = tmp_path / 'input_dates3.csv'
    input_dates3.write_text('2026-01-10T09:11:12;INFO;server2;Диск заполнен на 99%\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates1), str(input_dates2), str(input_dates3),'--format','csv','--output',str(output_dates)])
    result = json.loads(output_dates.read_text(encoding='utf-8'))

    assert result == {'total_events': 3, 'count_levels': {'DEBUG': 0, 'INFO': 1, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 2},
     'count_source': {'server1': 1, 'server2': 2},
     'source_errors': [{'source': 'server1', 'count': 1}, {'source': 'server2', 'count': 1}],
     'first_timestamp': '2026-01-10T09:11:02', 'last_timestamp': '2026-01-10T09:11:12', 'skipped': 0}

def test_many_cli_with_skip_invalid(tmp_path):
    '''Проверка нескольких файлов, среди которых есть некорректное событие, в режиме skip_invalid'''
    input_dates1 = tmp_path / 'input_dates1.csv'
    input_dates1.write_text('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%\n', encoding='utf-8')
    input_dates2 = tmp_path / 'input_dates2.csv'
    input_dates2.write_text('123;CRITICAL;server2;Диск заполнен на 99%\n', encoding='utf-8')
    input_dates3 = tmp_path / 'input_dates3.csv'
    input_dates3.write_text('2026-01-10T09:11:12;INFO;server2;Диск заполнен на 99%\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates1), str(input_dates2), str(input_dates3),'--format','csv','--output',str(output_dates), '--skip-invalid'])
    result = json.loads(output_dates.read_text(encoding='utf-8'))

    assert result == {'total_events': 2, 'count_levels': {'DEBUG': 0, 'INFO': 1, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 1},
     'count_source': {'server1': 1, 'server2': 1},
     'source_errors': [{'source': 'server1', 'count': 1}],
     'first_timestamp': '2026-01-10T09:11:02', 'last_timestamp': '2026-01-10T09:11:12', 'skipped': 1}

def test_unicode(tmp_path):
    '''Тестирование файла с  unicode-escape-последовательностью и представления данных в отчете(кириллица в отчете)'''
    input_dates = tmp_path / 'input_dates.jsonl'
    input_dates.write_text('{"timestamp":"2026-01-10T09:05","level":"INFO","source":"\\u0073\\u0065\\u0072\\u0076\\u0065\\u0072\\u0031","message":"Данные загружаются"}\n'
                           '{"timestamp":"2026-01-10T09:05","level":"INFO","source":"server2","message":"Получение данных"}\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates),'--format','jsonl','--output',str(output_dates)])
    result = json.loads(output_dates.read_text(encoding='utf-8'))

    assert 'server1' in result['count_source']
    assert '\\u0073\\u0065\\u0072\\u0076\\u0065\\u0072\\u0031' not in result['count_source']

def test_many_cli_no_skip_invalid(tmp_path):
    '''Проверка нескольких файлов, среди которых есть некорректное событие, в режиме по умолчанию'''
    input_dates1 = tmp_path / 'input_dates1.csv'
    input_dates1.write_text('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%\n', encoding='utf-8')
    input_dates2 = tmp_path / 'input_dates2.csv'
    input_dates2.write_text('123;CRITICAL;server2;Диск заполнен на 99%\n', encoding='utf-8')
    input_dates3 = tmp_path / 'input_dates3.csv'
    input_dates3.write_text('2026-01-10T09:11:12;INFO;server2;Диск заполнен на 99%\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'

    with pytest.raises(SystemExit) as exc_info:
        main(['analyze', str(input_dates1), str(input_dates2), str(input_dates3), '--format', 'csv', '--output',
              str(output_dates)])
    assert exc_info.value.code == 2

def test_unsupported_format(tmp_path):
    '''Проверка недопустимого формата'''
    input_dates1 = tmp_path / 'input_dates1.txt'
    input_dates1.write_text('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'

    with pytest.raises(SystemExit) as exc_info:
        main(['analyze', str(input_dates1), '--format', 'txt', '--output',
              str(output_dates)])
    assert exc_info.value.code == 2


def test_empty_file(tmp_path):
    '''Проверка пустого файла, должен вывестись нулевой отчет'''
    input_dates1 = tmp_path / 'input_dates1.csv'
    input_dates1.write_text('', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates1),'--format','jsonl','--output',str(output_dates)])
    result = json.loads(output_dates.read_text(encoding='utf-8'))

    assert result == {'total_events': 0,'count_levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
        'count_source': {},'source_errors': [],'first_timestamp': None,'last_timestamp': None,'skipped': 0}

def test_seven_line_error(tmp_path):
    '''Проверка сломанной седьмой строки бв режиме по умолчанию'''
    input_dates1 = tmp_path / 'input_dates1.jsonl'
    input_dates1.write_text('{"timestamp":"2026-01-10T09:11:02","level":"CRITICAL","source":"server1","message":"Диск заполнен на 99%"}\n'
                            '\n''\n''\n''\n''\n'
                           '{"timestamp":"123","level":"ERROR","source":"server1","message":"Диск заполнен на 99%"}\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'

    with pytest.raises(SystemExit) as exc_info:
        main(['analyze', str(input_dates1), '--format', 'jsonl', '--output', str(output_dates)])
    assert exc_info.value.code == 2


