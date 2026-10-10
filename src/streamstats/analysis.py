'''Анализ файлов, составление финальной статистики для отчета'''
from datetime import datetime


def new_statistics() -> dict:
    '''Создание новой статистики'''
    return {
        'total_events': 0,
        'count_levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
        'count_source': {},
        'source_errors': {},
        'first_timestamp': None,
        'last_timestamp': None
    }

def analyze(provided_line: dict, statistics:dict) -> None:
    '''Анализ строк, подсчет всех необходимых характеристик'''
    statistics['total_events'] += 1 #подсчет всех событий
    statistics['count_levels'][provided_line['level']]+=1 #подсчет событий каждого уровня
    statistics['count_source'][provided_line['source']] = (statistics['count_source'].get(provided_line['source'],0)) + 1 #подсчет
    # событий каждого источника

    if provided_line['level'] in ('ERROR', 'CRITICAL'): #подсчет источников, которые выводили ERROR/CRITICAL
        source = provided_line['source']
        statistics['source_errors'][source] = (statistics['source_errors'].get(source,0)) + 1

    #Определение самой ранней и самой поздней временной метки
    timestamp = provided_line['timestamp']
    if statistics['first_timestamp'] is None or timestamp < statistics['first_timestamp']:
        statistics['first_timestamp'] = timestamp
    if statistics['last_timestamp'] is None or timestamp > statistics['last_timestamp']:
        statistics['last_timestamp'] = timestamp

def top_source_errors(source_errors:dict, top_n:int = 5) -> list:
    '''Нахождение топ - n источников ошибок ERROR/CRITICAL'''
    source_errors = sorted(source_errors.items(), key=lambda x: x[0]) #сортировка источников по значению
    source_errors = sorted(source_errors, key=lambda x:x[-1], reverse=True) #сортировка источников по номеру
    return [{'source': source, 'count': count} for source, count in source_errors[:top_n]]

def final_statistics(statistics:dict,skipped:int=0, top_n:int=5) -> dict:
    '''Формирование конечной статистики, котороя будет записана в отчете'''
    return {
    'total_events': statistics['total_events'],
    'count_levels': statistics['count_levels'],
    'count_source': statistics['count_source'],
    'source_errors': top_source_errors(statistics['source_errors'],top_n),
    'first_timestamp': datetime.isoformat(statistics['first_timestamp']) if statistics['first_timestamp'] is not None else None,
    'last_timestamp': datetime.isoformat(statistics['last_timestamp']) if statistics['last_timestamp'] is not None else None,
    'skipped': skipped
    }
