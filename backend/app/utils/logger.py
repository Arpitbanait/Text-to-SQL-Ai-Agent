import logging
import sys
from app.config import settings


def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup and configure logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


logger = setup_logger()
