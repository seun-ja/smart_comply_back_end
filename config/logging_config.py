import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging():
    """
    Configures the application logging to use JSON format for production-ready structured logging.
    """
    # Define the format for our JSON logger
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s", timestamp=True
    )

    # Root logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File handler (optional, but good for production)
    # file_handler = RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=30)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    # Ensure that logs are propagated to the root logger
    logging.getLogger().addHandler(stream_handler)
    logging.getLogger().setLevel(logging.INFO)

    return logger
