import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Custom logging handler that intercepts
     log records and emits them using the 'logger' object.

    This handler is designed to work with the
    'logger' object from the 'loguru' library.

    Note:
        The 'emit' method of this handler
        is expected to be overridden in subclasses.

    Args:
        logging.Handler: The base logging handler class.

    Attributes:
        N/A

    Methods:
        emit(record: logging.LogRecord) -> None:
            Emit the log record using the 'logger' object.

    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """
        Emit the log record using the 'logger' object.

        Args:
            record (logging.LogRecord):
             The log record to emit.

        Returns:
            None

        """
        logger_opt = logger.opt(depth=7, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())
