'''Чтение файла'''
import logging
from typing import Any, Generator

from streamstats.errors import (
    IncorrectEventError,
    IncorrectTimestampError,
    UnsupportedFormatError,
)
from streamstats.models import validation
from streamstats.parsers import parser_csv, parser_json

logger = logging.getLogger(__name__) #присваивание логгера модуля name

fields = ('timestamp','level','source','message') #необходимые поля

def read_file(file_path:str,file_format:str,skip_invalid:bool=False,skipped:list|None=None) -> Generator[
    tuple[int, dict[str, Any]], Any, None]:

    #счетчик пропущенных некорректных строк
    if skipped is None:
        skipped = [0]

    with open(file_path, encoding='utf-8-sig') as file:
        #чтение заголовка
        if file_format == 'csv':
            headline = file.readline()

            if headline:
                separator = ';' if headline.count(';') >= 3 else ',' #определяем разделитель
                first_parts = tuple(name.strip() for name in headline.rstrip().split(separator)) #формируем кортеж с заданными заголовками

                #проверка заголовков на корректность
                if all(field in first_parts for field in fields):
                    columns = first_parts #название колонок
                    first_line = None
                    start = 2

                #если первая сторка - не заголовок, а событие
                else:
                    columns, start = None, 2
                    first_line = headline

            #если пустая строка
            else:
                columns, first_line, start = None, None, 0 #пропускаем пустую строку

        elif file_format == 'jsonl':
            columns, first_line, start = None, None, 1

        else:
            raise UnsupportedFormatError('Неподдерживаемый формат файлов')

        #если первая строка не заголовок, а событие
        if first_line is not None:
            try:
                line = parser_csv(first_line,columns,separator) #парсим первую строку отдельно
                yield 1, validation(line) #возвращает проверенный словарь и приостанавливается
            except (IncorrectTimestampError, IncorrectEventError) as exc:
                # если в режиме skip_invalid увеличиваем счетчик пропущенных строк
                if skip_invalid:
                    skipped[0]+=1
                    logger.warning(f'{file_path}: строка 1: {exc}') #записываем warning в лог
                #если не в режиме skip_invalid кидаем ошибку
                else:
                    raise type(exc)(f'{file_path}: строка 1: {exc}') from exc

        #проходимся по остальным строкам, нумеруем их и парсерим
        for line_number, other_line in enumerate(file, start):
            other_line = other_line.rstrip('\n')

            #пропуск пустых строк
            if not other_line.strip():
                continue

            #парсинг строк
            try:
                if file_format == 'csv':
                    line = parser_csv(other_line,columns,separator)
                else:
                    line = parser_json(other_line)
                yield line_number, validation(line) #возвращает проверенный словарь и приостанавливается
            except (IncorrectTimestampError, IncorrectEventError) as exc:
                #если в режиме skip_invalid увеличиваем счетчик пропущенных строк
                if skip_invalid:
                    skipped[0] += 1
                    logger.warning(f'{file_path}: строка {line_number}: {exc}') #записываем warning в лог
                #если не в режиме skip_invalid кидаем ошибку
                else:
                    raise type(exc)(f'{file_path}: строка {line_number}: {exc}') from exc



