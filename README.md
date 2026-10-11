## Консольный потоковый анализатор файлов
Пакет `streamstats` читает события из CSV- и JSONL-файлов, считает статистику и формирует JSON-отчёт. Файлы читаются построчно — целиком в память не загружаются. Код запускается через `python -m streamstats`.

Возможности

- объединение статистики нескольких файлов в один отчёт
- поддержка CSV с заголовком и без
- поддержка JSONL
- валидация обязательных полей: `timestamp`, `level`, `source`, `message`
- проверка `level` на допустимые значения: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- подсчёт общего числа событий, событий каждого уровня и каждого источника
- top-5 источников ошибок уровня `ERROR`/`CRITICAL`
- определение самой ранней и самой поздней временной метки
- два режима обработки: с пропуском некорректных событий и без

Обработка ошибок:

- режим по умолчанию — остановиться на первой некорректной строке, вывести `файл:строка`, завершить CLI с кодом `2`
- режим `--skip-invalid` — пропустить повреждённую строку, записать `WARNING` в лог, увеличить счётчик пропущенных строк в отчёте
- неверный JSON в строке 7 сообщает строку 7
- неверная дата сообщает поле и строку
- неизвестный формат файлов — ошибка
- пустой файл создаёт нулевой отчёт без падения

Все ошибки наследуются от общего класса `StreamStatsError`, поэтому командная строка перехватывает их и печатает сообщение в `stderr` с кодом завершения `2`. При успехе код завершения — `0`.

Основные функции

- `read_file` — генератор: открывает файл, читает шапку CSV, построчно читает данные, парсит и валидирует

- `parser_csv` — разбирает CSV-строку в `dict`
- `parser_json` — разбирает JSONL-строку в `dict`

- `validation` — проверяет обязательные поля, тип значений, возвращает словарь с `datetime` в `timestamp`

- `new_statistics` — создаёт пустой `stats` со счётчиками
- `analyze` — формирует статистику
- `top_source_errors` — возвращает top-5 источников ошибок `ERROR`/`CRITICAL`
- `final_statistics` — собирает словарь для JSON-отчёта

- `writing_report` — записывает отчёт в JSON-файл

Структура проекта
```
lab_02/
├── src/
│   └── streamstats/
│       ├── __init__.py
│       ├── __main__.py      # командная строка
│       ├── reader.py        # read_file
│       ├── parsers.py       # parser_csv, parser_json
│       ├── models.py        # validation
│       ├── analysis.py      # analyze, final_statistics
│       ├── report.py        # writing_report
│       └── errors.py        # исключения проекта
├── tests/
│   ├── conftest.py
│   ├── parser_test.py
│   ├── reader_test.py
│   ├── models_test.py
│   ├── analysis_test.py
│   ├── report_test.py
│   └── cli_test.py
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```
Запуск

bash  
cd src  
python -m streamstats analyze "data.csv" --format csv --output report.json  
python -m streamstats analyze "data.jsonl" --format jsonl --output report.json
python -m streamstats analyze "data.jsonl" --format jsonl --skip-invalid --output report.json  
python -m streamstats analyze file1.jsonl file2.jsonl --format jsonl --output report.json  
python -m streamstats --help

Тестирование

Проект использует pytest. Запуск тестов из корня проекта (там, где pyproject.toml):

bash  
python -m pytest -v

Дополнительная проверка стиля кода:

bash  
ruff check .

Технологии

Python 3.12.2  
pytest 9.1.1  
ruff 0.16.8

Автор

Пронина Виктория  
Группа: М8О – 101БВ – 26