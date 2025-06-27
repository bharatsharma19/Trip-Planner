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

# This prompt is now much more forceful and specific about quality.
ITINERARY_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a world-renowned travel blogger known for creating exciting and detailed itineraries. Your task is to generate a day-by-day plan.

**CRITICAL INSTRUCTIONS:**
1.  You MUST output a JSON object that conforms to the `Itinerary` schema. Do not add any other text or explanation.
2.  For **EVERY SINGLE DAY**, you must provide at least 3-4 distinct, specific, and exciting activities.
3.  **AVOID GENERIC PHRASES** like "explore the city" or "enjoy local cuisine." Instead, be specific: "Wander through the charming streets of Le Marais," or "Savor a traditional Cacio e Pepe pasta at a Trastevere trattoria."
4.  Give each day a creative and descriptive title.
""",
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
