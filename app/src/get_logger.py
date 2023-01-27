import logging
import sys

from pythonjsonlogger import jsonlogger

_message_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
_date_format = '%I:%M:%S'


class _StackDriverJsonFormatter(jsonlogger.JsonFormatter):  # type: ignore
    def __init__(  # type: ignore
        self, *args, fmt: str = _message_format, style: str = '%', datefmt: str = _date_format, **kwargs
    ) -> None:
        jsonlogger.JsonFormatter.__init__(self, *args, fmt=fmt, style=style, datefmt=datefmt, **kwargs)

    def process_log_record(self, log_record):  # type: ignore
        log_record['severity'] = log_record['levelname']
        del log_record['levelname']
        return super().process_log_record(log_record)


class _MaxLevelFilter(logging.Filter):
    def __init__(self, highest_log_level: int) -> None:
        super().__init__()
        self._highest_log_level = highest_log_level

    def filter(self, record):  # type: ignore
        return record.levelno <= self._highest_log_level


def _get_formatter() -> _StackDriverJsonFormatter:
    formatter = _StackDriverJsonFormatter()
    return formatter


def _get_info_handler() -> logging.StreamHandler:  # type: ignore
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(_MaxLevelFilter(logging.WARNING))
    info_handler.setFormatter(_get_formatter())
    return info_handler


def _get_error_handler() -> logging.StreamHandler:  # type: ignore
    error_handler = logging.StreamHandler(sys.stderr)
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
    logger.addHandler(_get_error_handler())
    logger.propagate = False
    _loggers[name] = logger
    return logger
