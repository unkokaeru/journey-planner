"""route_planning.py: Functions for route planning."""

from random import randint

from geopy.geocoders import Nominatim

from ..config.constants import Constants
from ..integrations.google_maps import (
    compute_route,
    get_distance_matrix,
    search_nearby_places,
)


def find_longitude_and_latitude(location: str) -> tuple[float, float]:
    """
    Find the longitude and latitude of a location.

    Parameters
    ----------
    location : str
        The location to find the longitude and latitude of.

    Returns
    -------
    tuple[float, float]
        A tuple containing the longitude and latitude of the location.

    Raises
    ------
    ValueError
        If the location is not found.

    Examples
    --------
    >>> get_location_coordinates("New York")
    (40.7128, -74.0060)

    >>> get_location_coordinates("Los Angeles")
    (34.0522, -118.2437)

    Notes
    -----
    This function finds the longitude and latitude of a given location.
    It takes in the location as a string and returns a tuple containing
    the longitude and latitude of the location.
    It uses the Nominatim geocoding service from OpenStreetMap to find
    the location. If the location is not found, it raises a ValueError.
    """
    geolocator = Nominatim(user_agent="geoapiExercises")  # geolocator object
    location_data = geolocator.geocode(location)

    if location_data:
        latitude: float = location_data.latitude
        longitude: float = location_data.longitude
        return latitude, longitude
    else:
        raise ValueError("Location not found.")


def plan_route(start: str, end: str, duration: int, API_KEY: str) -> dict[str, str | int]:
    """
    Plan a route between two locations.

    Parameters
    ----------
    start : str
        The starting location for the journey.
    end : str
        The ending location for the journey.
    duration : int
        The duration of the journey, in seconds.
    API_KEY : str
        The API key for the application.

    Returns
    -------
    dict[str, str | int]
        A dictionary containing the route information.

    Raises
    ------
    ValueError
        If no nearby places are found,
        or if the journey is not possible within the specified duration.

    Notes
    -----
    This function plans a route between two locations using the
    Google Maps API. It takes in the starting location, ending
    location, duration of the journey, and the API key for the
    application. It returns a dictionary containing the route
    information: distance in meters, duration in seconds, and
    an encoded polyline of the route.
    It does this by first searching for nearby points of interest
    within the specified duration of the starting location. It then
    selects a random point of interest to travel to, subtracts the
    time taken to travel to that point from the total duration, and
    repeats the process until the remaining duration is less than
    the time taken to travel to the given ending location.
    """
    # Get initial journey details
    start_to_end_distance_matrix = get_distance_matrix(start, end, API_KEY)
    start_latlong = find_longitude_and_latitude(start_to_end_distance_matrix["start_location"])
    end_latlong = find_longitude_and_latitude(start_to_end_distance_matrix["end_location"])
    remaining_duration = duration
    intermediate_latlongs = []

    # Check if ending location is reachable within the specified duration
    if start_to_end_distance_matrix["duration"] > duration:
        raise ValueError("Ending location not reachable within the specified duration.")

    # Find latlongs of nearby places and plan the route
    while remaining_duration > 0:
        # Search for nearby places within the remaining duration
        nearby_places = search_nearby_places(
            API_KEY,
            start_latlong,
            remaining_duration * Constants.CONVERSION_FACTOR_MINUTES_TO_METERS,
        )

        # Select a random place to travel to
        try:
            selected_place = nearby_places.pop(randint(0, len(nearby_places) - 1))
            selected_latlong = find_longitude_and_latitude(selected_place["formatted_address"])
        except IndexError:
            break  # Ran out of nearby places to search for

        # Compute the route to the selected place and the ending location
        route_to_selection = compute_route(API_KEY, start_latlong, selected_latlong)
        route_to_end = compute_route(API_KEY, selected_latlong, end_latlong)

        if (
            route_to_selection["duration_seconds"] + route_to_end["duration_seconds"]
            <= remaining_duration
        ):
            # Update the remaining duration and the route list
            remaining_duration -= route_to_selection["duration_seconds"]
            intermediate_latlongs.append(selected_latlong)
            start_latlong = selected_latlong

            if len(intermediate_latlongs) == 8:
                break  # Reached the maximum number of places before higher billing on API
        else:
            continue  # Try again with a different place

    if len(intermediate_latlongs) == 0:
        raise ValueError("No nearby places found within the specified duration.")

    # Calculate total route information
    total_route_information = compute_route(
        API_KEY, start_latlong, end_latlong, intermediate_latlongs
    )

    return total_route_information
