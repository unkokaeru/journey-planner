"""constants.py: Constants for the application."""

from typing import Literal


class Constants:
    """
    Constants for the application.

    Notes
    -----
    This class contains constants used throughout the application.
    By storing constants in a single location, it is easier to
    manage and update them. Constants should be defined as class
    attributes and should be named in uppercase with underscores
    separating words.
    """

    # Logging constants
    POSSIBLE_LOGGING_LEVELS = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
    LOGGING_LEVEL_DEFAULT: POSSIBLE_LOGGING_LEVELS = "WARNING"
    LOGGING_FORMAT = "%(message)s"
    LOGGING_DATE_FORMAT = "[%X]"
    LOGGING_TRACEBACKS = True

    # Computation constants
    CONVERSION_FACTOR_MINUTES_TO_METERS: int = 750  # meters per minute (just under 30mph)
