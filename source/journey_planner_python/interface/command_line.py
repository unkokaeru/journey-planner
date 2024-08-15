"""command_line.py: Command line interface for the application."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from typing import Any

from ..logs.setup_logging import setup_logging

interface_logger = setup_logging()


def command_line_interface() -> dict[str, Any]:
    """
    Command line interface for the application.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the arguments passed to the application

    Notes
    -----
    Takes arguments from the command line and returns them as a dictionary.
    """
    interface_logger.debug("Command line interface started.")

    argparser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter
    )  # Automatically generates help messages

    argparser.add_argument(
        "--api_key",
        "-a",
        action="store",
        type=str,
        required=True,
        help="API key for the application.",
    )  # API key for the application

    argparser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        # type=bool, # This is not needed as the action is store_true
        required=False,
        help="Show debug messages.",
    )  # Debug mode

    argparser.add_argument(
        "--start",
        "-s",
        action="store",
        type=str,
        required=True,
        help="Starting location for the journey.",
    )  # Starting location

    argparser.add_argument(
        "--end",
        "-e",
        action="store",
        type=str,
        required=False,
        help=(
            "Ending location for the journey, "
            "if not provided, the journey will be a return journey."
        ),
    )  # Ending location

    argparser.add_argument(
        "--length",
        "-l",
        action="store",
        type=int,
        required=False,
        help="Length of the journey in minutes.",
    )  # Length of the journey

    parsed_args = argparser.parse_args()

    interface_logger.debug("Command line interface finished.")

    return vars(parsed_args)
