# tools/search_place_tool.py
from langchain.tools import tool
import requests
from core.config import settings
from typing import List, Dict, Any


@tool("search_place")
def search_place(query: str) -> List[Dict[str, Any]]:
    """
    General purpose search for places, attractions, airports, or cities using Google Places API.
    - To find attractions, use queries like "tourist attractions in Goa".
    - To find an airport's IATA code, use a query like "airport in Delhi".
    - To get a city's ID for hotel searches, use a query like "Goa city".
    Returns a list of places with their name, address, rating, and internal Place ID.
    """
    api_key = settings.GOOGLE_API_KEY
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return [{"error": f"No places found for query: {query}"}]

        return [
            {
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating"),
                "place_id": place.get("place_id"),
            }
            for place in results[:5]
        ]
    except requests.RequestException as e:
        return [{"error": f"Place search API error: {e}"}]
