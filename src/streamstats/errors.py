'''Исключения пакета'''

class StreamStatsError(Exception):
    pass

class UnsupportedFormatError(StreamStatsError):
    'Неподдерживаемый формат'

class IncorrectEventError(StreamStatsError):
    'Неверное событие'

class IncorrectTimestampError(StreamStatsError):
    'Неверная временная метка'

class CLIConfigurationError(StreamStatsError):
    'Ошибка конфигурации CLI'