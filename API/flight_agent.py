from datetime import datetime

import requests

FLIGHT_API_URL = "http://localhost:8000/search-flights"

CITY_TO_AIRPORT = {
    "delhi": "DEL",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "mumbai": "BOM",
    "jaipur": "JAI",
}

DEFAULT_PASSENGERS = {
    "adults": 1,
    "children": 0,
    "infants": 0,
}


def execute_flight_search(task, intent):
    # ---- Passenger handling (user > default) ----
    passengers = intent.get("passengers", {}) or {}

    adult_count = passengers.get("adults") or DEFAULT_PASSENGERS["adults"]
    child_count = passengers.get("children") or DEFAULT_PASSENGERS["children"]
    infant_count = passengers.get("infants") or DEFAULT_PASSENGERS["infants"]

    # ---- Required intent fields ----
    destination_city = intent.get("destination")
    start_date = intent.get("start_date")
    end_date = intent.get("end_date")

    if not destination_city or not start_date:
        return {"status": "error", "reason": "Missing destination or start_date"}

    origin_code = CITY_TO_AIRPORT.get("delhi")
    destination_code = CITY_TO_AIRPORT.get(destination_city.lower())

    if not destination_code:
        return {
            "status": "error",
            "reason": f"Unknown destination airport for '{destination_city}'",
        }

    departure_time = datetime.fromisoformat(start_date).strftime("%Y-%m-%dT00:00:00")

    # ---- Journey type ----
    journey_type = 1  # One-way
    if end_date:
        journey_type = 2  # Round-trip

    # ---- Build API payload ----
    payload = {
        "AdultCount": adult_count,
        "ChildCount": child_count,
        "InfantCount": infant_count,
        "DirectFlight": False,
        "OneStopFlight": False,
        "JourneyType": journey_type,
        "PreferredAirlines": None,
        "Segments": [
            {
                "Origin": origin_code,
                "Destination": destination_code,
                "FlightCabinClass": 1,  # Economy
                "PreferredDepartureTime": departure_time,
                "PreferredArrivalTime": departure_time,
            }
        ],
    }

    try:
        response = requests.post(FLIGHT_API_URL, json=payload, timeout=10)
        response.raise_for_status()

        return {"status": "success", "results": response.json()}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "reason": str(e)}
