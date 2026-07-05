import sys
from loguru import logger
from config import config

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=config.log_level
)

# Add file handler
logger.add(
    config.log_file_path,
    rotation="10 MB",     # Rotate when file reaches 10MB
    retention="1 week",   # Keep logs for a week
    compression="zip",    # Zip old logs
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"         # Always log debug to file for troubleshooting
)

# Exception logging is handled automatically by logger.exception() or logger.catch decorator
