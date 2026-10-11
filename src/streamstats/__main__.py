import argparse
import logging
import sys

from streamstats.analysis import analyze, final_statistics, new_statistics
from streamstats.errors import StreamStatsError
from streamstats.reader import read_file
from streamstats.report import writing_report


def main(arguments: list[str]| None = None) -> None:
    '''Чтение командной строки, разбор аргументов,связывание чтения файлов, анализв и формирования файла с отчетом'''

    raw_arguments = sys.argv[1:] if arguments is None else arguments #если параметры команды
    # переданы явно, то они принимаются сразу, иначе берем sys.argv

    #Разбор командной строки
    parser = argparse.ArgumentParser(prog='streamstats', description='Потоковый анализатор файлов')
    subparsers = parser.add_subparsers(dest='command', required=True, help='подкоманды') #создание подкоманд

    analyze_parser = subparsers.add_parser('analyze', help='анализ файлов')
    analyze_parser.add_argument('input',nargs='+', help='входной(ые) файл(ы)')
    analyze_parser.add_argument('--format', choices = ['csv','jsonl'], required=True, help='формат файлов')
    analyze_parser.add_argument('--output', required=True, help='путь файла с отчетом')
    analyze_parser.add_argument('--skip-invalid', action='store_true', help='пропуск некорректных строк')
    parsed = parser.parse_args(raw_arguments)

    logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

    #Связывание чтения, анализа, создания отчета; обработка ошибок
    statistics = new_statistics() #создание новой статистики
    skipped = [0]

    try:
        for file_path in parsed.input: #чтение файлов, заполнение статистики
            for line_number, event in read_file(file_path, parsed.format, skip_invalid=parsed.skip_invalid, skipped = skipped):
                analyze(event,statistics)

        result = final_statistics(statistics,skipped=skipped[0])
        writing_report(result,parsed.output) #формирование файла с отчетом


    except StreamStatsError as exc:
        print(f'Ошибка: {exc}', file=sys.stderr)
        sys.exit(2)

    except (FileNotFoundError,PermissionError) as exc:
        print(f'Ошибка: {exc}', file=sys.stderr)
        sys.exit(2)



if __name__ == '__main__':
    main()