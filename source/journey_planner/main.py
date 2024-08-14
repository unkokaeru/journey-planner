"""main.py: Called when the package is run as a script."""

from .computation.route_planning import plan_route
from .interface.command_line import command_line_interface
from .logs.setup_logging import setup_logging

main_logger = setup_logging()


def main() -> None:
    """
    Main function for the application.

    Notes
    -----
    This function is the entry point for the application.
    """
    main_logger.debug("Application started.")

    user_arguments = command_line_interface()
    route_details = plan_route(
        user_arguments["start"],
        user_arguments["end"],
        user_arguments["duration"] * 60,  # Convert minutes to seconds
        user_arguments["API_KEY"],
    )

    print(
        f"Distance: {route_details['distance_meters']} meters,\n"
        f"Duration: {route_details['duration_seconds']} seconds,\n"
        f"Encoded Polyline: {route_details['encoded_polyline']}"
    )


if __name__ == "__main__":
    main()
