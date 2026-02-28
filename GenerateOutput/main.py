import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI()

# Temporary in-memory storage (For production, use Redis)
active_sessions = {}


class OrchestrationPayload(BaseModel):
    session_id: str
    destination: str
    flight_data: Optional[Dict[str, Any]] = None
    hotel_data: Optional[Dict[str, Any]] = None


@app.post("/orchestrate")
async def generate_itinerary(payload: OrchestrationPayload):
    session_id = payload.session_id

    # 1. Initialize session if not exists
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            "destination": payload.destination,
            "flight_data": None,
            "hotel_data": None
        }

    # 2. Store incoming data
    if payload.flight_data:
        active_sessions[session_id]["flight_data"] = payload.flight_data

    if payload.hotel_data:
        active_sessions[session_id]["hotel_data"] = payload.hotel_data

    session = active_sessions[session_id]

    # 3. Wait for both agents
    if session["flight_data"] is None or session["hotel_data"] is None:
        return {
            "status": "pending",
            "message": "Waiting for the other agent to send data."
        }

    # 4. Prepare data for LLM
    flight_json = json.dumps(session["flight_data"], indent=2)
    hotel_json = json.dumps(session["hotel_data"], indent=2)

    prompt = f"""
You are an expert AI Travel Orchestrator.
Analyze the following data from a Flight Agent and a Hotel Agent.

[FLIGHT AGENT DATA]
{flight_json}

[HOTEL AGENT DATA]
{hotel_json}

Provide response in Markdown:

1. Trip Summary
2. Budget Breakdown (Total Cost)
3. Important Constraints
4. Nearby Attractions in {session["destination"]} (3 places)
"""

    try:
        response = client.responses.create(
            model="gpt-5.2",
            input=prompt,
            temperature=0.4
        )

        # Clean session
        del active_sessions[session_id]

        return {
            "status": "success",
            "itinerary": response.output_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM Generation failed: {str(e)}"
        )