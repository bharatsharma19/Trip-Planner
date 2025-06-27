# database/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union


class CityStop(BaseModel):
    """Represents a single city stop in a multi-city trip."""

    city: str
    country: str
    num_days: int


class FlightDetails(BaseModel):
    airline: str
    price: str
    departure_time: str
    arrival_time: str
    stops: int


class HotelDetails(BaseModel):
    name: str
    rating: float
    price_per_night: str
    review_score: float


class ItineraryDay(BaseModel):
    day: int
    title: str = "A day of exploration"
    activities: List[str] = Field(default_factory=list)
    meals: Union[Dict[str, str], str] = Field(
        default_factory=dict,
        description="e.g., {'breakfast': 'Local cafe', 'lunch': 'Restaurant X'} or 'Enjoy local cuisine'",
    )


class BudgetItem(BaseModel):
    category: str
    estimated_cost: float
    currency: str


class TripPlan(BaseModel):
    session_id: str
    origin_city: Optional[str] = None
    origin_iata: Optional[str] = None
    destination_iata: Optional[str] = None
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    interests: List[str] = Field(default_factory=list)
    route: List[CityStop] = Field(
        default_factory=list,
        description="The high-level, multi-city route for the trip.",
    )
    current_city_index: int = Field(
        default=0,
        description="The index of the city in the route currently being planned.",
    )
    flights: List[FlightDetails] = Field(
        default_factory=list, description="List of flight options."
    )
    accommodation: List[HotelDetails] = Field(
        default_factory=list, description="List of hotel options."
    )
    itinerary: List[ItineraryDay] = Field(default_factory=list)
    budget: List[BudgetItem] = Field(default_factory=list)
    status: str = "planning"


class QueryRequest(BaseModel):
    query: str
    session_id: str
