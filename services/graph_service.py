# services/graph_service.py
import uuid
from agents.graph import graph
from database.database import get_trip_plan, save_trip_plan
from database.models import QueryRequest


def run_graph(query_request: QueryRequest):
    """
    Runs the agentic graph for a given query and session.
    """
    session_id = query_request.session_id
    trip_plan = get_trip_plan(session_id)

    # Add a config to increase the recursion limit, as planning can take many steps
    config = {"recursion_limit": 50}

    initial_state = {
        "messages": [("human", query_request.query)],
        "plan": trip_plan,
    }

    # Invoke the graph with the config
    final_state = graph.invoke(initial_state, config=config)

    updated_plan = final_state["plan"]
    save_trip_plan(updated_plan)

    final_message = final_state["messages"][-1].content

    if not final_message:
        if updated_plan.status == "complete":
            final_message = (
                "I have finished planning your trip. Please see the details below."
            )
        else:
            final_message = "I have updated the plan with the new information."

    return {"answer": final_message, "plan": updated_plan.model_dump()}
