# mock_llm.py
def mock_llm(prompt: str) -> str:
    # Detect which prompt this is
    if "NLP extraction system" in prompt:
        # Structured intent output
        return """
        {
          "destination": "Jaipur",
          "start_date": null,
          "end_date": null,
          "duration_days": 3,
          "budget": "ultra_low",
          "travel_mode": "road_trip",
          "interests": ["food", "cafes"],
          "constraints": {
            "no_flights": true,
            "no_hotels": false
          }
        }
        """

    if "task classification system" in prompt:
        # Task list output
        return '["flight_search", "hotel_search", "activities_planning", "logistics_planning"]'

    raise ValueError("Unknown prompt")
