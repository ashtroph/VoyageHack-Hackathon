# hotel_agent.py

import requests
from defaults import SYSTEM_DEFAULTS
from hotel_resolver import resolve_hotel_codes

HOTEL_API_URL = "http://localhost:8080/hotel-search"


def execute_hotel_search(task, intent):
    """
    Hotel Search Agent
    Converts structured intent → TBO-compatible payload
    and calls Node.js hotel service via POST.
    """

    # ---- Guard rails ----
    if intent.get("duration_days", 0) < 1:
        return {"status": "skipped", "reason": "No overnight stay required"}

    destination = intent.get("destination")
    check_in = intent.get("start_date")
    check_out = intent.get("end_date")

    if not destination or not check_in or not check_out:
        return {"status": "error", "reason": "Missing destination or hotel dates"}

    # ---- Resolve destination → HotelCodes ----
    hotel_codes = resolve_hotel_codes(destination)
    if not hotel_codes:
        return {
            "status": "error",
            "reason": f"No hotel codes found for destination '{destination}'",
        }

    # ---- Passengers (intent > system defaults) ----
    intent_passengers = intent.get("passengers") or {}
    default_passengers = SYSTEM_DEFAULTS["passengers"]

    pax_rooms = [
        {
            "Adults": intent_passengers.get("adults", default_passengers["adults"]),
            "Children": intent_passengers.get(
                "children", default_passengers["children"]
            ),
            "ChildrenAges": intent_passengers.get(
                "children_ages", default_passengers["children_ages"]
            ),
        }
    ]

    # ---- Hotel preferences (intent > defaults) ----
    intent_prefs = intent.get("hotel_preferences") or {}
    default_prefs = SYSTEM_DEFAULTS["hotel_preferences"]

    filters = {
        "Refundable": intent_prefs.get("refundable", default_prefs["refundable"]),
        "NoOfRooms": intent_prefs.get("rooms", default_prefs["rooms"]),
        "MealType": intent_prefs.get("meal_type", default_prefs["meal_type"]),
    }

    # ---- Final POST payload (TBO-compatible) ----
    payload = {
        "CheckIn": check_in,
        "CheckOut": check_out,
        "HotelCodes": hotel_codes,
        "GuestNationality": SYSTEM_DEFAULTS["guest_nationality"],
        "PaxRooms": pax_rooms,
        "Filters": filters,
    }

    try:
        response = requests.post(HOTEL_API_URL, json=payload, timeout=15)
        response.raise_for_status()

        return {
            "status": "success",
            "results": response.json(),
            "meta": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
            },
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "reason": str(e)}
