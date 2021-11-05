import logging
import traceback


class Logger:
    def __init__(self, name=__file__, filename=None, silent=False, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if filename != None:
            self._add_handler(filename)
        if not silent:
            self._add_handler()

    def _add_handler(self, filename=''):
        if type(filename) is str and filename != '':
            handler = logging.FileHandler(filename, encoding='utf-8')
        else:
            handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def error(self, exc_info=None, message=''):
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            additional = '[%s]' % message if message else ''
            self.logger.error(' => '.join(['"%s", %d: %s' % (fs.filename, fs.lineno, fs.line)
                              for fs in traceback.extract_tb(exc_traceback)]) + ' [%s: %s] ' % (exc_type.__name__, exc_value) + additional)
        else:
            self.logger.error(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)
