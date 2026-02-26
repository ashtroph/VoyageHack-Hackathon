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


def planning_pipeline(user_text, llm):
    intent = extract_structured_intent(user_text, llm)
    intent = post_process_intent(intent)
    validate_intent(intent)

    excluded_agents, task_constraints = rule_based_filter(intent)
    tasks = llm_based_filter(intent, llm)

    filtered_tasks = [t for t in tasks if TASK_AGENT_MAP[t] not in excluded_agents]

    return route_tasks_to_agents(filtered_tasks, task_constraints)
