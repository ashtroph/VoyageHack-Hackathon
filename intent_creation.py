import json
from datetime import datetime

INTENT_SCHEMA = {
    "destination": None,
    "start_date": None,
    "end_date": None,
    "duration_days": None,
    "budget": None,  # ultra_low | low | medium | high
    "travel_mode": None,  # flight | train | road_trip | mixed
    "interests": [],
    "constraints": {"no_flights": False, "no_hotels": False},
}


def extract_structured_intent(user_text, llm):
    prompt = f"""
    You are an NLP extraction system.

    Extract structured travel intent from the text below.

    Follow this JSON schema exactly:
    {json.dumps(INTENT_SCHEMA, indent=2)}

    Rules:
    - Use null if information is missing
    - Normalize budget to: ultra_low, low, medium, high
    - Normalize travel_mode to: flight, train, road_trip, mixed
    - Do NOT infer or guess missing data
    - Return ONLY valid JSON

    Text:
    {user_text}
    """
    response = llm(prompt)
    return json.loads(response)


def post_process_intent(intent):
    # Derive duration if dates exist
    if intent["start_date"] and intent["end_date"]:
        sd = datetime.fromisoformat(intent["start_date"])
        ed = datetime.fromisoformat(intent["end_date"])
        intent["duration_days"] = (ed - sd).days

    # Enforce explicit constraints
    if intent["constraints"]["no_flights"]:
        intent["travel_mode"] = "road_trip"

    return intent


def validate_intent(intent):
    if not intent["destination"]:
        raise ValueError("Destination is required")

    if intent["duration_days"] is not None and intent["duration_days"] < 0:
        raise ValueError("Invalid duration")

    return True
