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

from API.flight_agent import execute_flight_search
from API.hotel_agent import execute_hotel_search

AGENT_EXECUTORS = {
    "FLIGHT_AGENT": execute_flight_search,
    "ACCOMMODATION_AGENT": execute_hotel_search,
}


class PlanningPipeline:
    def __init__(self, llm):
        self.llm = llm

    def run(self, user_text):
        intent = self._extract_intent(user_text)
        routed_tasks = self._decompose_tasks(intent)
        results = self._execute_tasks(routed_tasks, intent)

        return {
            "intent": intent,
            "tasks": routed_tasks,
            "results": results,
        }

    def _extract_intent(self, user_text):
        intent = extract_structured_intent(user_text, self.llm)
        intent = post_process_intent(intent)
        validate_intent(intent)
        return intent

    def _decompose_tasks(self, intent):
        excluded_agents, task_constraints = rule_based_filter(intent)
        tasks = llm_based_filter(intent, self.llm)

        filtered_tasks = [t for t in tasks if TASK_AGENT_MAP[t] not in excluded_agents]

        return route_tasks_to_agents(filtered_tasks, task_constraints)

    def _execute_tasks(self, routed_tasks, intent):
        results = {}

        for task in routed_tasks:
            agent = task["agent"]
            executor = AGENT_EXECUTORS.get(agent)

            if not executor:
                results[agent] = {
                    "status": "skipped",
                    "reason": "No executor registered",
                }
                continue

            results[agent] = executor(task, intent)

        return results
