import logging
import os
from logging.handlers import RotatingFileHandler

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _create_rotating_handler(filename: str, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, filename),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return handler


def setup_loggers() -> None:
    # --- Error logger ---
    error_logger = logging.getLogger("app.error")
    error_logger.setLevel(logging.ERROR)
    error_logger.addHandler(_create_rotating_handler("error.log", logging.ERROR))
    error_logger.propagate = False

    # --- Warning logger ---
    warning_logger = logging.getLogger("app.warning")
    warning_logger.setLevel(logging.WARNING)
    warning_logger.addHandler(_create_rotating_handler("warning.log", logging.WARNING))
    warning_logger.propagate = False

    # --- DB logger ---
    db_logger = logging.getLogger("sqlalchemy.engine")
    db_logger.setLevel(logging.INFO)
    db_logger.addHandler(_create_rotating_handler("database.log", logging.INFO))
    db_logger.propagate = False

    # --- Request logger (HTTP) ---
    request_logger = logging.getLogger("app.request")
    request_logger.setLevel(logging.INFO)
    request_logger.addHandler(_create_rotating_handler("request.log", logging.INFO))
    request_logger.propagate = False
