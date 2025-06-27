# tools/generate_itinerary_tool.py
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from core.model_loader import get_llm
from database.models import ItineraryDay
from typing import List


class Itinerary(BaseModel):
    """A container for a list of daily itinerary plans."""

    itinerary_list: List[ItineraryDay] = Field(
        description="A list of daily plans for the trip, with activities and meal suggestions for each day."
    )


itinerary_llm = get_llm()

ITINERARY_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a specialized itinerary planning assistant. Your sole purpose is to generate a detailed, day-by-day itinerary based on the user's request. You must output a JSON object that conforms to the `Itinerary` schema. Do not add any other text or explanation.""",
        ),
        (
            "human",
            "Generate an itinerary for a {duration_days}-day trip to {destination} with interests in {interests}.",
        ),
    ]
)

structured_llm = itinerary_llm.with_structured_output(Itinerary)


@tool("generate_itinerary")
def generate_itinerary(
    destination: str, duration_days: int, interests: List[str]
) -> List[ItineraryDay]:
    """Generates a complete, multi-day itinerary in a single step."""
    prompt = ITINERARY_GENERATION_PROMPT.invoke(
        {
            "destination": destination,
            "duration_days": duration_days,
            "interests": ", ".join(interests),
        }
    )
    try:
        itinerary_result = structured_llm.invoke(prompt)
        return itinerary_result.itinerary_list
    except Exception as e:
        print(f"Error in generate_itinerary_tool: {e}")
        return []
