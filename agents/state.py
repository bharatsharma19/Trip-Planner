# agents/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from database.models import TripPlan


class TripState(TypedDict):
    # The `add_messages` function defines how messages are added to the state.
    messages: Annotated[list[BaseMessage], add_messages]
    # This is our structured plan that the agent will fill out.
    plan: TripPlan
