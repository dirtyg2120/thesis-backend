import logging

from app.models.log_record import LogRecord


class LogDBHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        LogRecord(
            level=record.levelname, message=record.message, created_by=record.name
        ).save()
