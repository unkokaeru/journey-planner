"""google_maps.py: Integration with the Google Maps API."""

import json
from typing import Any, Literal

import requests

from ..logs.setup_logging import setup_logging

maps_integration_logger = setup_logging()


def get_distance_matrix(
    api_key: str,
    start_location: str,
    end_location: str,
    units: Literal["metric", "imperial"] = "metric",
) -> dict[str, Any]:
    """
    Retrieve the distance/duration between two locations using the Google Maps Distance Matrix API.

    Parameters
    ----------
    api_key : str
        Your Google Maps API key.
    start_location : str
        The starting location for the distance matrix request.
    end_location : str
        The ending location for the distance matrix request.
    units : Literal['metric', 'imperial'], optional
        The units to use for the distance and duration values, by default 'metric'.

    Returns
    -------
    dict of str to str or int
        A dictionary containing the distance and duration between the two locations.

    Raises
    ------
    ValueError
        If the API request fails or if the locations are not found.

    Notes
    -----
    The Google Maps Distance Matrix API requires an API key with the appropriate permissions.

    Example
    -------
    >>> api_key = 'your_api_key_here'
    >>> start_location = 'London'
    >>> end_location = 'Bury St Edmunds'
    >>> get_distance_matrix(api_key, start_location, end_location)
    {
        'start_location': 'London, UK',
        'end_location': 'Bury St Edmunds, Bury Saint Edmunds, UK',
        'distance_text': '133 km',
        'distance_value': 133313,
        'duration_text': '1 hour 47 mins',
        'duration_value': 6398
    }
    """
    url: str = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"destinations={end_location}&origins={start_location}&units={units}&key={api_key}"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"API request failed with status code {response.status_code}")

    data = response.json()

    if data["status"] != "OK":
        raise ValueError(f"API response status is not OK: {data['status']}")

    origin_addresses = data["origin_addresses"]
    destination_addresses = data["destination_addresses"]
    elements = data["rows"][0]["elements"][0]

    if elements["status"] != "OK":
        raise ValueError(f"Element status is not OK: {elements['status']}")

    result = {
        "start_location": origin_addresses[0],
        "end_location": destination_addresses[0],
        "distance_text": elements["distance"]["text"],
        "distance_value": elements["distance"]["value"],
        "duration_text": elements["duration"]["text"],
        "duration_value": elements["duration"]["value"],
    }

    return result


def search_nearby_places(
    api_key: str,
    latlong: tuple[float, float],
    radius: int,
    types_list: list[str] = ["tourist_attraction"],
) -> list[dict[str, Any]]:
    """
    Search for nearby places using the Google Places API.

    Parameters
    ----------
    api_key : str
        Your Google Maps API key.
    latlong : tuple of float
        The latitude and longitude of the search location.
    radius : int
        The radius of the search area in metres.
    types_list : list of str, optional
        A list of place types to include in the search. Default is ['tourist_attraction'].

    Returns
    -------
    list of dict of str to Any
        A list of dictionaries containing information about the nearby places.

    Raises
    ------
    ValueError
        If the API request fails or if the response contains an error.

    Notes
    -----
    The Google Places API requires an API key with the appropriate permissions.

    Example
    -------
    >>> api_key = 'your_api_key_here'
    >>> latitude = 52.2635809
    >>> longitude = 0.6916481
    >>> radius = 10000
    >>> search_nearby_places(api_key, (latitude, longitude), radius)
    [
        {
            'formatted_address': 'West Midland Safari and Leisure Park, Bewdley DY12 1LF, UK',
            'rating': 4.5,
            'user_rating_count': 2,
            'display_name': 'Twilight Cave'
        },
        ...
    ]
    """
    url = "https://places.googleapis.com/v1/places:searchNearby"
    field_mask = "places.displayName,places.formattedAddress,places.rating,places.userRatingCount"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": field_mask,
    }
    payload = {
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latlong[0], "longitude": latlong[1]},
                "radius": radius,
            }
        },
        "rankPreference": "DISTANCE",
        "includedTypes": types_list,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError(f"API request failed with status code {response.status_code}")

    data = response.json()

    if "places" not in data:
        raise ValueError(f"API response error: {data}")

    places = []
    for place in data["places"]:
        place_info = {
            "formatted_address": place.get("formattedAddress"),
            "rating": place.get("rating"),
            "user_rating_count": place.get("userRatingCount"),
            "display_name": place["displayName"]["text"] if "displayName" in place else None,
        }
        places.append(place_info)

    return places


def compute_route(
    api_key: str,
    origin_latlong: tuple[float, float],
    destination_latlong: tuple[float, float],
    intermediate_latlongs: list[tuple[float, float]] = [],
    travel_mode: str = "DRIVE",
    routing_preference: str = "TRAFFIC_AWARE",
    compute_alternative_routes: bool = False,
    avoid_tolls: bool = False,
    avoid_highways: bool = False,
    avoid_ferries: bool = False,
    units: Literal["IMPERIAL", "METRIC"] = "METRIC",
) -> dict[str, Any]:
    """
    Compute a route between two locations using the Google Routes API.

    Parameters
    ----------
    api_key : str
        Your Google Maps API key.
    origin_latlong : tuple of float
        The latitude and longitude of the origin location.
    destination_latlong : tuple of float
        The latitude and longitude of the destination location.
    intermediate_latlongs : list of tuple of float, optional
        A list of intermediate locations to visit along the route. Default is [].
    travel_mode : str, optional
        Mode of travel (e.g., 'DRIVE', 'WALK'). Default is 'DRIVE'.
    routing_preference : str, optional
        Routing preference (e.g., 'TRAFFIC_AWARE'). Default is 'TRAFFIC_AWARE'.
    compute_alternative_routes : bool, optional
        Whether to compute alternative routes. Default is False.
    avoid_tolls : bool, optional
        Whether to avoid tolls. Default is False.
    avoid_highways : bool, optional
        Whether to avoid highways. Default is False.
    avoid_ferries : bool, optional
        Whether to avoid ferries. Default is False.
    language_code : str, optional
        Language code for the response. Default is 'en-US'.
    units : Literal['IMPERIAL', 'METRIC'], optional
        Units for the response. Default is 'METRIC'.

    Returns
    -------
    dict of str to int or str
        A dictionary containing the route distance, duration, and encoded polyline.

    Raises
    ------
    ValueError
        If the API request fails or if the response contains an error.

    Notes
    -----
    The Google Routes API requires an API key with the appropriate permissions.

    Example
    -------
    >>> api_key = 'your_api_key_here'
    >>> origin_lat = 37.419734
    >>> origin_lng = -122.0827784
    >>> destination_lat = 37.417670
    >>> destination_lng = -122.079595
    >>> compute_route(api_key, (origin_lat, origin_lng), (destination_lat, destination_lng))
    {
        'distance_meters': 772,
        'duration_seconds': 165,
        'encoded_polyline': 'ipkcFfichVnP@j@BLoFVwM{E?'
    }
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline",
    }  # Might also need to include 'routes.legs' in the field mask
    payload = {
        "origin": {
            "location": {"latLng": {"latitude": origin_latlong[0], "longitude": origin_latlong[1]}}
        },
        "destination": {
            "location": {
                "latLng": {"latitude": destination_latlong[0], "longitude": destination_latlong[1]}
            }
        },
        "intermediates": (
            [
                {"location": {"latLng": {"latitude": latlong[0], "longitude": latlong[1]}}}
                for latlong in intermediate_latlongs
            ]
            if intermediate_latlongs != []
            else []
        ),
        "travelMode": travel_mode,
        "routingPreference": routing_preference,
        "computeAlternativeRoutes": compute_alternative_routes,
        "routeModifiers": {
            "avoidTolls": avoid_tolls,
            "avoidHighways": avoid_highways,
            "avoidFerries": avoid_ferries,
        },
        "languageCode": "en-GB",
        "units": units,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        if response.status_code == 403:
            raise ValueError(
                "API request failed with status code 403: Forbidden. "
                "This could be due to an invalid API key, lack of permissions, "
                "or exceeding the quota."
            )
        else:
            raise ValueError(
                f"API request failed with status code {response.status_code}: {response.text}"
            )

    data = response.json()

    if "routes" not in data or not data["routes"]:
        raise ValueError(f"API response error: {data}")

    route: dict = data["routes"][0]
    route_info = {
        "distance_meters": route.get("distanceMeters"),
        "duration_seconds": int(route.get("duration", "0").replace("s", "")),
        "encoded_polyline": route.get("polyline", {}).get("encodedPolyline"),
    }

    return route_info
