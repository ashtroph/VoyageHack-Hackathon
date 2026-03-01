from mock_llm import mock_llm

from intent_creation import (
    extract_structured_intent,
    post_process_intent,
    validate_intent,
)
from task_decomp import (
    TASK_AGENT_MAP,
    llm_based_filter,
    route_tasks_to_agents,
    rule_based_filter,
)


def test_feature_1():
    user_text = "I want a cheap 3 day road trip to Jaipur with good food"

    # ---- NLP ----
    intent = extract_structured_intent(user_text, mock_llm)
    intent = post_process_intent(intent)
    validate_intent(intent)

    print("\nSTRUCTURED INTENT")
    print(intent)

    # ---- Rule-based filter ----
    excluded_agents, task_constraints = rule_based_filter(intent)

    print("\nEXCLUDED AGENTS")
    print(excluded_agents)

    print("\nTASK CONSTRAINTS")
    print(task_constraints)

    # ---- LLM task inference ----
    tasks = llm_based_filter(intent, mock_llm)

    print("\nLLM TASKS")
    print(tasks)

    # ---- Correct filtering (task → agent) ----
    filtered_tasks = [t for t in tasks if TASK_AGENT_MAP[t] not in excluded_agents]

    print("\nFILTERED TASKS")
    print(filtered_tasks)

    # ---- Routing ----
    final_tasks = route_tasks_to_agents(filtered_tasks, task_constraints)

    print("\nFINAL EXECUTION JSON")
    for t in final_tasks:
        print(t)


if __name__ == "__main__":
    test_feature_1()
