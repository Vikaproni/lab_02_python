import argparse
import logging
import sys

from streamstats.analysis import analyze, final_statistics, new_statistics
from streamstats.errors import StreamStatsError
from streamstats.reader import read_file
from streamstats.report import writing_report


def main(arguments: list[str]| None = None) -> None:
    '''Чтение командной строки, чтение файлов, анализ и формирование файла с отчетом'''

    #Разбор командной строки
    parser = argparse.ArgumentParser(prog='streamstats', description='Потоковый анализатор файлов')
    subparsers = parser.add_subparsers(dest='command', required=True, help='подкоманды') #создание подкоманд

    analyze_parser = subparsers.add_parser('analyze', help='анализ файлов')
    analyze_parser.add_argument('input',nargs='+', help='входные файлы')
    analyze_parser.add_argument('--format', choices = ['csv','jsonl'], required=True, help='формат файлов')
    analyze_parser.add_argument('--output', default='REPORT.json', help='путь файла с отчетом(по умолчанию: "REPORT.json"')
    analyze_parser.add_argument('--skip-invalid', action='store_true', help='пропуск некорректных строк')
    arguments = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

    #Связывание чтения, анализа, создания отчета; обработка ошибок
    statistics = new_statistics() #создание новой статистики
    skipped = [0]

    try:
        for file_path in arguments.input: #чтение файлов, заполнение статистики
            for line_number, event in read_file(file_path, arguments.format, skip_invalid=arguments.skip_invalid, skipped = skipped):
                analyze(event,statistics)

        result = final_statistics(statistics,skipped=skipped[0])
        writing_report(result,arguments.output) #формирование файла с отчетом


    except StreamStatsError as exc:
        print(f'Ошибка: {exc}', file=sys.stderr)
        sys.exit(2)



if __name__ == '__main__':
    main()