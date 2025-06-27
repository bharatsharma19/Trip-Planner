# tools/create_multicity_route_tool.py
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from core.model_loader import get_llm
from database.models import CityStop
from typing import List


class Route(BaseModel):
    """A container for a multi-city route plan."""

    route_plan: List[CityStop] = Field(
        description="A list of city stops, including the city, country, and number of days to spend in each."
    )


route_llm = get_llm()

ROUTE_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a high-level trip architect. Your job is to break down a long, multi-destination trip into a logical sequence of cities. You must output a JSON object that conforms to the `Route` schema. Do not add any other text or explanation.""",
        ),
        (
            "human",
            "Generate a route for a {duration_days}-day trip to {region} with interests in {interests}.",
        ),
    ]
)

structured_llm = route_llm.with_structured_output(Route)


@tool("create_multicity_route")
def create_multicity_route(
    region: str, duration_days: int, interests: List[str]
) -> List[CityStop]:
    """Creates a high-level, multi-city travel route for large regions like 'Europe' or 'Southeast Asia'."""
    prompt = ROUTE_GENERATION_PROMPT.invoke(
        {
            "region": region,
            "duration_days": duration_days,
            "interests": ", ".join(interests),
        }
    )
    try:
        route_result = structured_llm.invoke(prompt)
        return route_result.route_plan
    except Exception as e:
        print(f"Error in create_multicity_route_tool: {e}")
        return []
