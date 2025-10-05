import os
import logging
from logging.handlers import RotatingFileHandler

def get_logger(name: str = "default"):
    """
    Returns a configured logger with rotation and console output.
    Log level and log directory can be customized via environment variables.
    """
    # Read config from environment
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_dir = os.getenv("LOG_PATH", "/app/var/logs")
    log_file = os.path.join(log_dir, "agent_post.log")

    # Make sure log dir exists
    os.makedirs(log_dir, exist_ok=True)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    )

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=50 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler (for Docker logs)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Create or get existing logger
    logger = logging.getLogger(name)
    # Prevent duplicate handlers if called multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(log_level)
        logger.propagate = False

    return logger
