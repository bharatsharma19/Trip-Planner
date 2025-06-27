# agents/graph.py
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.messages import ToolMessage, AIMessage

from .state import TripState
from core.model_loader import get_llm
from prompts.system_prompts import PLANNER_PROMPT
from tools.weather_info_tool import weather_info
from tools.search_place_tool import search_place
from tools.calculator_tool import calculator
from tools.currency_conversion_tool import currency_converter
from tools.flight_search_tool import flight_search
from tools.hotel_search_tool import hotel_search
from tools.generate_itinerary_tool import generate_itinerary
from tools.create_multicity_route_tool import create_multicity_route
from database.models import (
    CityStop,
    ItineraryDay,
    BudgetItem,
    TripPlan,
    FlightDetails,
    HotelDetails,
)

external_tools = [
    weather_info,
    search_place,
    calculator,
    currency_converter,
    flight_search,
    hotel_search,
    generate_itinerary,
    create_multicity_route,
]
tool_map = {t.name: t for t in external_tools}


class PlanUpdater(BaseModel):
    """Use this internal tool to update the trip plan with new information."""

    origin_city: Optional[str] = Field(
        default=None, description="The user's city of origin."
    )
    origin_iata: Optional[str] = Field(
        default=None, description="The IATA code for the origin airport."
    )
    destination_iata: Optional[str] = Field(
        default=None, description="The IATA code for the destination airport."
    )
    destination: Optional[str] = Field(
        default=None, description="The destination of the trip."
    )
    duration_days: Optional[int] = Field(
        default=None, description="The duration of the trip in days."
    )
    interests: Optional[List[str]] = Field(
        default=None, description="List of user's interests to add."
    )
    route: Optional[List[CityStop]] = Field(
        default=None, description="The high-level, multi-city route."
    )
    current_city_index: Optional[int] = Field(
        default=None,
        description="The index of the city to plan next. Use this to advance the project.",
    )
    flights: Optional[List[FlightDetails]] = Field(
        default=None, description="List of flight options."
    )
    accommodation: Optional[List[HotelDetails]] = Field(
        default=None, description="List of hotel options."
    )
    itinerary: Optional[List[ItineraryDay]] = Field(
        default=None, description="A chunk of a day-by-day itinerary to add."
    )
    budget: Optional[List[BudgetItem]] = Field(
        default=None, description="Budget breakdown."
    )
    status: Optional[str] = Field(
        default=None, description="Set to 'complete' when the plan is finished."
    )


llm = get_llm()
model_with_tools = llm.bind_tools(external_tools + [PlanUpdater])


def planner_node(state: TripState) -> dict:
    prompt = PLANNER_PROMPT.partial(plan=state["plan"].model_dump_json(indent=2))
    response = model_with_tools.invoke(prompt.invoke({"messages": state["messages"]}))
    return {"messages": [response]}


def plan_updater_node(state: TripState) -> dict:
    """The 'Assembly Line' node. It correctly assembles the final plan."""
    last_message = state["messages"][-1]
    tool_messages = []
    updated_plan = state["plan"]

    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "PlanUpdater":
            args = tool_call["args"]
            updated_data = updated_plan.model_dump()

            # --- THIS IS THE ASSEMBLY LOGIC ---
            # Special handling for the itinerary to ensure days are sequential
            if "itinerary" in args and args["itinerary"]:
                new_itinerary_chunk = args["itinerary"]
                # Find the last day number in the existing itinerary
                last_day = (
                    updated_data["itinerary"][-1]["day"]
                    if updated_data["itinerary"]
                    else 0
                )
                # Re-number the new chunk to be sequential
                for i, day_plan in enumerate(new_itinerary_chunk):
                    day_plan["day"] = last_day + i + 1
                # Now extend the main itinerary with the re-numbered chunk
                updated_data["itinerary"].extend(new_itinerary_chunk)
                # Remove the chunk from args to avoid double-adding
                del args["itinerary"]
            # --- END OF ASSEMBLY LOGIC ---

            for key, value in args.items():
                if value is not None:
                    if isinstance(updated_data.get(key), list) and isinstance(
                        value, list
                    ):
                        updated_data[key].extend(
                            v for v in value if v not in updated_data[key]
                        )
                    else:
                        updated_data[key] = value

            updated_plan = TripPlan(**updated_data)
            tool_messages.append(
                ToolMessage(
                    content=f"Successfully updated the plan.",
                    tool_call_id=tool_call["id"],
                )
            )
    return {"plan": updated_plan, "messages": tool_messages}


def custom_tool_node(state: TripState) -> dict:
    tool_messages = []
    last_message = state["messages"][-1]
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        if tool_name in tool_map:
            tool_to_call = tool_map[tool_name]
            tool_output = tool_to_call.invoke(tool_call["args"])
            if (
                isinstance(tool_output, list)
                and tool_output
                and isinstance(tool_output[0], BaseModel)
            ):
                serialized_output = [item.model_dump() for item in tool_output]
                tool_output = json.dumps(serialized_output, indent=2)
            elif isinstance(tool_output, BaseModel):
                tool_output = tool_output.model_dump_json(indent=2)
            elif not isinstance(tool_output, str):
                tool_output = json.dumps(tool_output, indent=2)
            tool_messages.append(
                ToolMessage(content=tool_output, tool_call_id=tool_call["id"])
            )
    return {"messages": tool_messages}


def router(state: TripState) -> str:
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return END
    if any(call["name"] == "PlanUpdater" for call in last_message.tool_calls):
        return "update_plan"
    if any(call["name"] in tool_map for call in last_message.tool_calls):
        return "call_external_tools"
    return END


workflow = StateGraph(TripState)
workflow.add_node("planner", planner_node)
workflow.add_node("update_plan", plan_updater_node)
workflow.add_node("tools", custom_tool_node)
workflow.set_entry_point("planner")
workflow.add_conditional_edges(
    "planner",
    router,
    {"update_plan": "update_plan", "call_external_tools": "tools", END: END},
)
workflow.add_edge("update_plan", "planner")
workflow.add_edge("tools", "planner")
graph = workflow.compile()
