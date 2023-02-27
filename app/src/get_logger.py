import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from pythonjsonlogger import jsonlogger

_message_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
_date_format = '%I:%M:%S'


class _StackDriverJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(
        self, *args: str, fmt: str = _message_format, style: str = '%', datefmt: str = _date_format, **kwargs: str
    ) -> None:
        jsonlogger.JsonFormatter.__init__(self, *args, fmt=fmt, style=style, datefmt=datefmt, **kwargs)  # type: ignore

    def process_log_record(self, log_record):  # type: ignore
        log_record['severity'] = log_record['levelname']
        del log_record['levelname']
        return super().process_log_record(log_record)  # type: ignore


class _MaxLevelFilter(logging.Filter):
    def __init__(self, highest_log_level: int) -> None:
        super().__init__()
        self._highest_log_level = highest_log_level

    def filter(self, record):  # type: ignore
        return record.levelno <= self._highest_log_level


def _get_formatter() -> _StackDriverJsonFormatter:
    formatter = _StackDriverJsonFormatter()
    return formatter


def _get_info_handler(file: bool = False) -> logging.StreamHandler | TimedRotatingFileHandler:  # type:ignore
    if file:
        info_handler = TimedRotatingFileHandler('logs/app.log', when='midnight', backupCount=7)
    else:
        info_handler = logging.StreamHandler(sys.stdout)  # type:ignore
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(_MaxLevelFilter(logging.WARNING))
    info_handler.setFormatter(_get_formatter())
    return info_handler


def _get_error_handler(file: bool = False) -> logging.StreamHandler | TimedRotatingFileHandler:  # type:ignore
    if file:
        error_handler = TimedRotatingFileHandler('./logs/app.log', when='midnight', backupCount=7)
    else:
        error_handler = logging.StreamHandler(sys.stdout)  # type:ignore
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(_get_formatter())
    return error_handler


_loggers: dict[str, logging.Logger] = {}


def getLogger(name: str) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(_get_info_handler())
    logger.addHandler(_get_info_handler(file=True))
    logger.addHandler(_get_error_handler())
    logger.addHandler(_get_error_handler(file=True))
    logger.propagate = False
    _loggers[name] = logger
    return logger
