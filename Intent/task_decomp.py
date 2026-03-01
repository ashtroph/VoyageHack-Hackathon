import json

AGENT_REGISTRY = {
    "FLIGHT_AGENT": {
        "type": "api",
        "required_fields": ["destination", "dates"],
        "skip_if": ["road_trip"],
    },
    "ACCOMMODATION_AGENT": {"type": "api", "required_fields": ["destination", "dates"]},
    "ACTIVITY_DINING_AGENT": {
        "type": "llm",
        "required_fields": ["destination", "interests"],
    },
    "LOGISTICS_AGENT": {"required_fields": ["destination"]},
}


# USES RULE BASED FILTERING TO EXCLUDE ANY AGENTS THAT ARE NOT NEEDED
def rule_based_filter(user_intent):
    excluded_agents = []
    task_constraints = {}

    if user_intent.get("travel_mode") == "road_trip":
        excluded_agents.append("FLIGHT_AGENT")

    if user_intent.get("duration_days", 0) < 1:
        excluded_agents.append("ACCOMMODATION_AGENT")

    if user_intent.get("budget") == "ultra_low":
        task_constraints["activities_planning"] = {
            "price_level": "budget",
            "paid_activities": False,
        }

    return excluded_agents, task_constraints


def llm_based_filter(structured_intent, llm):
    prompt = f"""
    You are a task classification system.

    Based on the structured travel intent below, return a JSON list
    of required planning tasks.

    Allowed tasks:
    - flight_search
    - hotel_search
    - activities_planning

    Rules:
    - If travel_mode is road_trip → exclude flight_search
    - Do not explain anything.

    Intent:
    {json.dumps(structured_intent)}
    """
    return json.loads(llm(prompt))


TASK_AGENT_MAP = {
    "flight_search": "FLIGHT_AGENT",
    "hotel_search": "ACCOMMODATION_AGENT",
    "activities_planning": "ACTIVITY_DINING_AGENT",
}


def route_tasks_to_agents(tasks, task_constraints):
    routed_tasks = []

    for task in tasks:
        routed_tasks.append(
            {
                "task_id": task,
                "agent": TASK_AGENT_MAP[task],
                "constraints": task_constraints.get(task, {}),
            }
        )

    return routed_tasks
