# logger.py
import os
import logging
from logging.handlers import RotatingFileHandler
from config import load_config

def setup_logging():
    config = load_config()
    log_file = config["SCRIPT_LOG_FILE"]
    max_log_files = config.get("MAX_LOG_FILES", 5)
    os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler (logs everything)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,
        backupCount=max_log_files,
        encoding='utf-8'
    )
    file_formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (suppresses 403/400 errors and module/file logging)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(lambda record: not (
        record.getMessage().startswith("Indexing module:") or
        record.getMessage().startswith("Found file:") or
        record.getMessage().startswith("Found linked file:") or
        "403 Client Error" in record.getMessage() or
        "400 Client Error" in record.getMessage()
    ))
    logger.addHandler(console_handler)

    return logger
