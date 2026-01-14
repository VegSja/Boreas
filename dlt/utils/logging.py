"""Logging configuration for the dlt pipeline."""
import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Set up a structured logger for the pipeline.
    
    Args:
        name: Logger name (typically __name__)
        level: Log level override (defaults to ERROR)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Avoid duplicate handlers
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    log_level = level or 'ERROR'
    logger.setLevel(getattr(logging, log_level.upper()))
    
    return logger