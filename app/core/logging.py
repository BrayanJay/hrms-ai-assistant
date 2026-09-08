import logging
import json
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timezone, timedelta

SL_TZ = timezone(timedelta(hours=5, minutes=30))


STANDARD_ATTRS = frozenset(logging.LogRecord(
    "", 0, "", 0, "", (), None
).__dict__.keys()) | {"message", "asctime"}

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.fromtimestamp(record.created, tz=SL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["traceback"] = traceback.format_exception(*record.exc_info)
        for key, value in record.__dict__.items():
            if key not in STANDARD_ATTRS:
                log[key] = value
        return json.dumps(log, default=str)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = JSONFormatter()

        # stdout — for docker logs
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        # file — persists across restarts
        Path("logs").mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            "logs/app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5               # keep last 5 files
        )
        file_handler.setFormatter(formatter)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
    return logger
