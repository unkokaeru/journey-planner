"""setup_logging.py: Set up the logging configuration."""

import logging
from typing import Literal

from rich.logging import RichHandler

from ..config.constants import Constants


def setup_logging(
    logging_level: Literal[
        "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"
    ] = Constants.LOGGING_LEVEL_DEFAULT,
) -> logging.Logger:
    """
    Setup logging configuration.

    Parameters
    ----------
    logging_level : Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], optional
        The logging level to set, by default Constants.LOGGING_LEVEL_DEFAULT

    Returns
    -------
    logging.Logger
        The logger instance for the application.

    Raises
    ------
    ValueError
        If the logging level is invalid.

    Examples
    --------
    >>> setup_logging()
    <Logger rich (INFO)>
    >>> setup_logging(logging_level="DEBUG")
    <Logger rich (DEBUG)>
    >>> setup_logging(logging_level="INVALID")
    Traceback (most recent call last):
        ...
    ValueError: Invalid logging level: INVALID.
    Valid levels are:CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

    Notes
    -----
    This function sets up the logging configuration for the application.
    """
    valid_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    if logging_level not in valid_levels:
        raise ValueError(
            "Invalid logging level: "
            + logging_level
            + ". \nValid levels are: "
            + ", ".join(valid_levels.keys())
        )

    logging.basicConfig(
        level=valid_levels[logging_level],
        format=Constants.LOGGING_FORMAT,
        datefmt=Constants.LOGGING_DATE_FORMAT,
        handlers=[RichHandler(rich_tracebacks=Constants.LOGGING_TRACEBACKS)],
    )

    return logging.getLogger("rich")
