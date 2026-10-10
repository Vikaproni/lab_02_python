import pytest
import json
from streamstats.__main__ import main


def test_cli_analyze(tmp_path):
    '''Проверка корректного файла '''
    input_dates = tmp_path / 'input_dates.csv'
    input_dates.write_text('2026-01-10T09:11:02;CRITICAL;server1;Диск заполнен на 99%\n', encoding='utf-8')
    output_dates = tmp_path / 'REPORT.json'
    main(['analyze',str(input_dates),'--format','csv','--output',str(output_dates)])
    assert output_dates.exists()

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
