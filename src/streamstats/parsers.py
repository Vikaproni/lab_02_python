"""Приведение строк к общему виду"""
from streamstats.errors import IncorrectEventError

START, EXPECT_KEY, EXPECT_VALUE, AFTER_KEY, IN_KEY, IN_STRING, IN_ESCAPE, AFTER_VALUE, DONE = range(9) #состояния внутри строки
escapes = {'"': '"', '\\': '\\', '/': '/', 'n': '\n', 't': '\t'} #escape-символы
fields = ('timestamp','level','source','message') #допустимые поля

def parser_csv(line:str, columns: tuple[str, ...]|None = None, separator: str = ',') -> dict:
    '''Приведение строк из csv-файла к общему виду, те преобразование обычных строк в словарь
     с ключами ('timestamp','level','source','message')'''
    line = line.strip() #удаление ненужных пробелов и '\n'
    #Определение пустой строки
    if not line:
        raise IncorrectEventError('Пустая строка')

    line = [parts.strip() for parts in line.split(separator, 3)] #разбиение строки по заданному разделителю
    # и убирание ненужных пробелов

    #Создание словаря с полями и исходными данными
    if columns is None:
        if len(line) < 4:
            raise IncorrectEventError('Не хватает данных')

        result = dict(zip(fields, line))

    else:
        if len(line) < len(columns): #если количество данных не соответствует количеству полей
            raise IncorrectEventError('Недостаточно полей')
        result = dict(zip(columns, line))

        #проверка на наличие всех необходимых полей
        missing = [field for field in fields if field not in result]
        if missing:
            raise IncorrectEventError(f'Отсутствует необходимое поле: {", ".join(missing)}')

    return result


def parser_json(line:str) -> dict:
    '''Приведение строк из jsonl-файла к общему виду, те преобразование json в словарь
     с ключами ('timestamp','level','source','message')'''
    line = line.strip()
    if not line:
        raise IncorrectEventError('Пустая строка')

    if line[0] != '{':
        raise IncorrectEventError('Ожидался JSON-объект')

    result = {}
    state = START #определение, где находится символ
    key = ''
    value = ''
    position = 1

    while position <  len(line):
        char = line[position]
        #в начале строки
        if state == START:
            if char == ' ':
                pass
            elif char == '"':
                key = ''
                state = IN_KEY
            elif char == '}': #пустой объект
                state = DONE
            else:
                raise IncorrectEventError('Ожидался ключ')

        #еще не в ключе
        elif state == EXPECT_KEY:
            if char == '"':
                key = ''
                state = IN_KEY
            elif char == ' ':
                pass
            else:
                raise IncorrectEventError('Ожидался ключ')

        #в ключе
        elif state == IN_KEY:
            if char == '\\': #в ключе не может быть экранирования, там должно быть конкретное название поля
                raise IncorrectEventError('Некорректно введен ключ')
            elif char == '"':
                state = AFTER_KEY
            else:
                key+=char

        #после прочтения ключа
        elif state == AFTER_KEY:
            if char == ':':
                state = EXPECT_VALUE
            elif char == ' ':
                pass
            else:
                raise IncorrectEventError('Ожидалось двоеточие')

        #после прочтения ключа и ":"
        elif state == EXPECT_VALUE:
            if char == '"':
                value = ''
                state = IN_STRING
            elif char == ' ':
                pass
            else:
                raise IncorrectEventError('Неподдерживаемый формат данных')

        #в значении
        elif state == IN_STRING:
            if char == '\\':
                state = IN_ESCAPE
            elif char == '"':
                result[key] = value #добавление значения к ключу
                key = ''
                value = ''
                state = AFTER_VALUE
            else:
                value+=char

        #сразу после значения
        elif state == AFTER_VALUE:
            if char == ' ':
                pass
            elif char == ',':
                state = EXPECT_KEY
            elif char == '}':
                state = DONE
            else:
                raise IncorrectEventError('Неверный json формат')

        #если есть экранирование
        elif state == IN_ESCAPE:
            if char == 'u':
                if position + 5 <= len(line): #проверка, что unicode-escape-последовательность полная
                    unicode_char = line[position+1:position+5] #срез с unicode-escape-последовательностью
                    try:
                        unicode_char = int(unicode_char, 16) #преобразование unicode-escape-последовательность
                    except ValueError:
                        raise IncorrectEventError('Некорректные сиволы в unicode-escape-последовательности')
                    unicode_char = chr(unicode_char)
                    value += unicode_char
                    position += 4
                    state = IN_STRING
                else:
                    raise IncorrectEventError('Неполная unicode-последовательность')

            else: #если другие escape-символы
                decoded = escapes.get(char)
                if decoded is None:
                    raise IncorrectEventError('Неизвестные символы')
                value+=decoded
                state = IN_STRING

        #в конце json-объекта
        elif state == DONE:
            if char != ' ': #если после закрывающей } есть какие-либо еще лишние символы, обрабатываем как ошибку,
                # тк это нарушение формата json-объекта
                raise IncorrectEventError('Символы после закрывающей скобки')
        else:
            raise IncorrectEventError('Ошибка')

        position += 1

    #если отсутствует закрывающая кавычка
    if state == IN_STRING:
        raise IncorrectEventError('Незакрытая строка')
    #если отсутствует "}"
    if state != DONE:
        raise IncorrectEventError('Незакрытый JSON-объект')

    return result

