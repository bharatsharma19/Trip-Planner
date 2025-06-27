# tools/flight_search_tool.py
from langchain.tools import tool
import requests
from core.config import settings
from typing import List, Dict, Any


@tool("flight_search")
def flight_search(
    origin_iata: str, destination_iata: str, departure_date: str
) -> List[Dict[str, Any]]:
    """
    Searches for one-way flights using a real-time Flight Data API.
    You must provide the IATA codes for the origin and destination airports.
    """
    url = "https://flight-data.p.rapidapi.com/search_one_way/"
    params = {
        "origin_iata": origin_iata,
        "destination_iata": destination_iata,
        "departure_date": departure_date,
        "currency": "INR",
    }
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "flight-data.p.rapidapi.com",
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data.get("flights"):
            return [{"error": "No flights found for the given route and date."}]

        # Extract and format the most important details for the top 3 flights
        flight_options = []
        for flight in data["flights"][:3]:
            flight_options.append(
                {
                    "airline": flight["airline"]["name"],
                    "price": f"{flight['price']['amount']} {flight['price']['currency']}",
                    "departure_time": flight["departure"]["scheduled_time"],
                    "arrival_time": flight["arrival"]["scheduled_time"],
                    "stops": len(flight.get("stops", [])),
                }
            )
        return flight_options
    except requests.RequestException as e:
        return [{"error": f"API request failed: {e}"}]
    except Exception as e:
        return [{"error": f"An unexpected error occurred: {e}"}]
