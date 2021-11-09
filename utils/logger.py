import sys
import logging
import traceback
from typing import Callable, Dict
from typing_extensions import Literal
from .color import Color, colored, colored_with_padding

color_map = {
    logging.DEBUG: [Color.BG_BLUE],
    logging.INFO: [Color.BG_GREEN],
    logging.WARN: [Color.FG_BRIGHT_BLACK, Color.BG_YELLOW],
    logging.ERROR: [Color.BG_RED]
}


Style = Dict[
    Literal[
        'name',
        'levelno',
        'levelname',
        'pathname',
        'filename',
        'module',
        'lineno',
        'funcName',
        'created',
        'asctime',
        'msecs',
        'relativeCreated',
        'thread',
        'threadName',
        'process',
        'message',
    ],
    Callable[[str, logging.LogRecord], str],
]


class StyledFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: str = None,
        datefmt: str = None,
        style: Style = None,
    ):
        super().__init__(fmt, datefmt=datefmt)
        self.fmt = fmt
        self.style: Style = {
            'name': lambda template, record: template,
            'levelno': lambda template, record: template,
            'levelname': lambda template, record: template,
            'pathname': lambda template, record: template,
            'filename': lambda template, record: template,
            'module': lambda template, record: template,
            'lineno': lambda template, record: template,
            'funcName': lambda template, record: template,
            'created': lambda template, record: template,
            'asctime': lambda template, record: template,
            'msecs': lambda template, record: template,
            'relativeCreated': lambda template, record: template,
            'thread': lambda template, record: template,
            'threadName': lambda template, record: template,
            'process': lambda template, record: template,
            'message': lambda template, record: template,
            **(style or {}),
        }

    def format(self, record: logging.LogRecord) -> str:
        format_orig = self._style._fmt

        self._style._fmt = self.fmt \
            .replace('%(name)s', self.style['name']('%(name)s', record)) \
            .replace('%(levelno)s', self.style['levelno']('%(levelno)s', record)) \
            .replace('%(levelname)s', self.style['levelname']('%(levelname)s', record)) \
            .replace('%(pathname)s', self.style['pathname']('%(pathname)s', record)) \
            .replace('%(filename)s', self.style['filename']('%(filename)s', record)) \
            .replace('%(lineno)d', self.style['lineno']('%(lineno)d', record)) \
            .replace('%(funcName)s', self.style['funcName']('%(funcName)s', record)) \
            .replace('%(created)f', self.style['created']('%(created)f', record)) \
            .replace('%(asctime)s', self.style['asctime']('%(asctime)s', record)) \
            .replace('%(msecs)d', self.style['msecs']('%(msecs)d', record)) \
            .replace('%(relativeCreated)d', self.style['relativeCreated']('%(relativeCreated)d', record)) \
            .replace('%(thread)d', self.style['thread']('%(thread)d', record)) \
            .replace('%(threadName)d', self.style['threadName']('%(threadName)d', record)) \
            .replace('%(process)d', self.style['process']('%(process)d', record)) \
            .replace('%(message)s', self.style['message']('%(message)s', record))

        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


def brief_path(verbose_path):
    stripped = verbose_path
    for env_var in sys.path:
        stripped = verbose_path.replace(env_var, '')
        if stripped != verbose_path:
            return stripped.lstrip('/\\')
    return stripped


def create_level_filter(level):
    def filter(record: logging.LogRecord):
        return record.levelname == level
    return filter


class Logger:
    """
    - `name` name of logger
    - `color` style of the `name` part
    - `level` the minimum level of the recorded log
    - `filename` if specified, log will be written into the file
    - `silent` no output at terminal if `True`
    - `fmt` format of the stream handler, see https://docs.python.org/3/library/logging.html#logging.Formatter
    - `filefmt` format of the file handler, see https://docs.python.org/3/library/logging.html#logging.Formatter
    - `datefmt` date format, see https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime
    """
    default_level = 'INFO'

    def __init__(self,
        name = __file__,
        color = [Color.FG_BLACK, Color.BG_WHITE],
        level = default_level,
        filename = None,
        silent = False,
        fmt = '%(asctime)s %(name)s %(levelname)s %(message)s',
        filefmt = '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',  
    ):
        self.name = name
        self.color = color
        self.fmt = fmt
        self.filefmt = filefmt
        self.datefmt = datefmt
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if isinstance(filename, str):
            self.add_handler(filename, level=level)
        elif isinstance(filename, dict):
            for level, name in filename.items():
                self.add_handler(filename=name, level_filter=create_level_filter(level))
        if not silent:
            self.add_handler(level=level)

    def __call__(self, message=''):
        self.info(message)

    def add_handler(self, filename=None, level=default_level, level_filter=None):
        if isinstance(filename, str) and filename:
            handler = logging.FileHandler(filename, encoding='utf-8')
            handler.setFormatter(logging.Formatter(self.filefmt, datefmt=self.datefmt))
        else:
            handler = logging.StreamHandler()
            handler.setFormatter(StyledFormatter(
                fmt = self.fmt,
                datefmt = self.datefmt,
                style = {
                    'asctime': lambda asctime, record: colored(asctime, Color.BRIGHT),
                    'levelname': lambda levelname, record: colored_with_padding(levelname, *color_map[record.levelno]),
                    'name': lambda name, record: colored_with_padding(name, self.color),
                },
            ))

        handler.setLevel(level)
        if level_filter:
            handler.addFilter(level_filter)
        self.logger.addHandler(handler)

    def error(self, message='', exc_info=None):
        """
        - `message` error message
        - `exc_info` tuple returned by sys.exc_info()
        """
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            additional = f'[{message}] ' if message else ''
            self.logger.error(additional + ' => '.join([f'"{brief_path(fs.filename)}", {fs.lineno}: "{fs.line}"' for fs in traceback.extract_tb(exc_traceback)]) + f' [{exc_type.__name__}: {exc_value}]')
        else:
            self.logger.error(message)

    def info(self, *message):
        self.logger.info(' '.join(message))

    def warning(self, *message):
        self.logger.warning(' '.join(message))

    def debug(self, *message):
        self.logger.debug(' '.join(message))
