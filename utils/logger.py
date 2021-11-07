import sys
import logging
import traceback
from .color import Color, colored, colored_with_padding

color_map = {
    logging.DEBUG: [Color.BG_BLUE],
    logging.INFO: [Color.BG_GREEN],
    logging.WARN: [Color.FG_BRIGHT_BLACK, Color.BG_YELLOW],
    logging.ERROR: [Color.BG_RED]
}


class StyledFormatter(logging.Formatter):
    def __init__(
        self,
        fmt = '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        style = None,
    ):
        super().__init__(fmt, datefmt=datefmt)
        self.style = {
            'asctime': lambda asctime: asctime,
            'levelname': lambda levelname: levelname,
            'name': lambda name: name,
            **(style or {}),
        }

    def format(self, record: logging.LogRecord) -> str:
        format_orig = self._style._fmt

        self._style._fmt = f'%(asctime)s %(levelname)s %(name)s %(message)s' \
            .replace('%(asctime)s', self.style['asctime']('%(asctime)s')) \
            .replace('%(levelname)s', self.style['levelname']('%(levelname)s', record.levelno)) \
            .replace('%(name)s', self.style['name']('%(name)s'))

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
    :name name of logger

    :filename if specified, log will be written into the file

    :silent no output at terminal if `True`
    """
    default_level = 'DEBUG'

    def __init__(self,
        name = __file__,
        level = default_level,
        filename = None,
        silent = False,
        fmt = '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        filefmt = '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
    ):
        """
        name: name of logger

        filename: if specified, log will be written into the file

        silent: no output at terminal if `True`
        """
        self.fmt = fmt
        self.filefmt = filefmt
        self.datefmt = datefmt
        self.logger = logging.getLogger(name)
        self.logger.setLevel('DEBUG')

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
                    'asctime': lambda asctime: colored(asctime, Color.BRIGHT),
                    'levelname': lambda levelname, level: colored_with_padding(levelname, *color_map[level]),
                    'name': lambda name: colored_with_padding(name, Color.BG_BLUE),
                },
            ))
        if level_filter:
            handler.addFilter(level_filter)
        else:
            handler.setLevel(level)
        self.logger.addHandler(handler)

    def error(self, message='', exc_info=None):
        """
        message: error message
        exc_info: tuple returned by sys.exc_info()
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
